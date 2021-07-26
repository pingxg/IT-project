# -*- coding: utf-8 -*-
import os

import numpy as np
import matplotlib.pyplot as plt

import cv2
from PIL import Image

# from spectral import *
from spectral.io.envi import save_image


FILE_EXTS = ['img', 'dat', 'sli', 'hyspex', 'raw']  # Define spectral file extentions

dtype_map = [
    ('1', np.uint8),                   # unsigned byte
    ('2', np.int16),                   # 16-bit int
    ('3', np.int32),                   # 32-bit int
    ('4', np.float32),                 # 32-bit float
    ('5', np.float64),                 # 64-bit float
    ('6', np.complex64),               # 2x32-bit complex
    ('9', np.complex128),              # 2x64-bit complex
    ('12', np.uint16),                 # 16-bit unsigned int
    ('13', np.uint32),                 # 32-bit unsigned int
    ('14', np.int64),                  # 64-bit int
    ('15', np.uint64),                 # 64-bit unsigned int
    ]

envi_to_dtype = dict((k, np.dtype(v)) for (k, v) in dtype_map)  # convert to dict
dtype_to_envi = dict(tuple(reversed(item)) for item in list(envi_to_dtype.items())) # reverse conversion

def read_hdr(file):
    """
    input: hdr file path
    output: dict including parameters
    """
    
    HEADER = {}
    hdr_path=file
    f_name, _ = os.path.splitext(file)
    if os.path.isfile(f_name+".hdr"):
        hdr_path = f_name+".hdr"
    elif os.path.isfile(f_name+".HDR"):
        hdr_path = f_name+".HDR"
    else:
        print('The file does not exist!')

    with open(hdr_path, 'r') as f:
        lines = f.readlines()

    # loop through hdr file and add information to a dict
    while lines:
        line = lines.pop(0).lower()
        if line.find('=') == -1: continue
        if line[0] == ';': continue
        (key, sep, val) = line.partition('=')
        key = key.strip()
        val = val.strip()
        if val and val[0] == '{':
            str = val.strip()
            while str[-1] != '}':
                line = lines.pop(0)
                if line[0] == ';': continue
                str += '\n' + line.strip()
            if key == 'description':
                HEADER[key] = str.strip('{}').strip()
            else:
                vals = str[1:-1].split(',')
                for j in range(len(vals)):
                    vals[j] = vals[j].strip()
                HEADER[key] = vals
        else:
            HEADER[key] = val
    
    # datatype conversion
    try:
        HEADER['lines'] = int(HEADER['lines'])      # nrows
        HEADER['samples'] = int(HEADER['samples'])  # ncols
        HEADER['bands'] = int(HEADER['bands'])
        HEADER['wavelength'] = [float(i) for i in HEADER['wavelength']]
        HEADER['fwhm'] = [float(i) for i in HEADER['fwhm']]
        HEADER['default bands'] = [int(i) for i in HEADER['default bands']]
        HEADER['default bands index'] = [int(i)-1 for i in HEADER['default bands']]
        HEADER['default bands wavelength'] = [float(HEADER['wavelength'][int(i)-1]) for i in HEADER['default bands']]
    except KeyError:
        pass
    return HEADER


def envi_opener(filename):
    """
    input: file path to hdr file or raw file, these two files must have same filename and under the same folder
    output: the spectral data which is a 3D numpy array
    """
    f_name, _ = os.path.splitext(filename)

    hdr_path = filename
    if os.path.isfile(f_name+".hdr"):
        hdr_path = f_name+".hdr"
    elif os.path.isfile(f_name+".HDR"):
        hdr_path = f_name+".HDR"
    else:
        print('The file does not exist!')

    hdr = read_hdr(hdr_path)

    if hdr['file type'] not in ["envi", "envi standard"]:
        print("This is not the right file type!")
    
    data_path = ""
    for e in FILE_EXTS:
        if os.path.isfile(f_name + "." + e):
            data_path = f_name + "." + e
    
    hdr['data_path'] = data_path
    
    R, C, B = hdr['lines'], hdr['samples'], hdr['bands']
    interleave = hdr["interleave"]
    
    try:
        # get the max value of current datatype
        divisor = np.iinfo(envi_to_dtype[hdr['data type']]).max

        # Exceptions: Some sensors save 16-bit data, but only store 12-bit values.
        if hdr['sensor type'] == 'specim iq' and hdr['data type'] == '12':
            # This device has a 12-bit sensor, so the 16-bit divisor is too much
            divisor = 4095
    except:
        divisor = 0
    hdr['scale_factor'] = divisor   # add to the hdr dict

    # read file using numpy memory map, and reshape the data based on the interleave
    if interleave == 'bil':
        data = np.memmap(data_path, dtype=envi_to_dtype[hdr['data type']], mode='r+', shape=(R, B, C))
    elif interleave == 'bip':
        data = np.memmap(data_path, dtype=envi_to_dtype[hdr['data type']], mode='r+', shape=(R, C, B))
    elif interleave == 'bsq':
        data = np.memmap(data_path, dtype=envi_to_dtype[hdr['data type']], mode='r+', shape=(B, R, C))

    return data, hdr

def tiff_opener(filename):
    image = None
    _, f_ext = os.path.splitext(filename)
    if f_ext in [".tiff", ".tif", ".TIFF", ".TIF"]:
        image = plt.imread(filename)
    return image

def read_band(filename, band=0, save=False):
    output = None
    data, hdr = envi_opener(filename)


    if hdr['interleave'] == 'bil':
        output = np.array(data[:, band, :])
    elif hdr['interleave'] == 'bip':
        output = np.array(data[:, :, band])
    elif hdr['interleave'] == 'bsq':
        output = np.array(data[band, :, :])
    
    if save:
        f_name, _ = os.path.splitext(filename)
        plt.imsave(f_name + f"_grayscale_{band}" +'.png', output, cmap="gray", dpi=500, format="png")

    # scale data based on the camera type
    if hdr['scale_factor'] != 0 and hdr['scale_factor'] != 1:
        output = output/float(hdr['scale_factor'])
        hdr['scale_factor'] = 1
    
    # scale the data to 0-255
    output = ((output-np.min(output))*255/(np.max(output)-np.min(output)))
    
    return output

# def read_bands(filename, band_min=0, band_max=None):
#     output = None
#     data, hdr = envi_opener(filename)
#     if band_max is None:
#         band_max = hdr['bands']
    
#     if hdr['interleave'] == 'bil':
#         output = np.array(data[:, band_min:band_max, :])
#         output = output.transpose((0, 2, 1))
#     elif hdr['interleave'] == 'bip':
#         output = np.array(data[:, :, band_min:band_max])
#     elif hdr['interleave'] == 'bsq':
#         output = np.array(data[band_min:band_max, :, :])
#         output = output.transpose((1, 2, 0))
#     return output

def read_pixel(filename, row=0, col=0, save=False):
    output = None
    data, hdr = envi_opener(filename)
    if hdr['interleave'] == 'bil':
        output = np.array(data[row, :, col])
    elif hdr['interleave'] == 'bip':
        output = np.array(data[row, col, :])
    elif hdr['interleave'] == 'bsq':
        output = np.array(data[:, row, col])

    if save:
        f_name, _ = os.path.splitext(filename)
        plt.plot(output)
        plt.savefig(f_name + f"_pixel_({row},{col})" +'.png', bbox_inches='tight',transparent=False, pad_inches=0)
    return output

def read_subcube(filename=None, oringinal_data=None, hdr=None, row_min=0, row_max=None, col_min=0, col_max=None, save=False):
    output = None

    if row_max is None:
        row_max = hdr['lines']
    if col_max is None:
        col_max = hdr['samples']

    if isinstance(oringinal_data, np.ndarray):
        data = oringinal_data
        # if band_min == None and band_max == None:
        output = np.array(data[row_min:row_max, col_min:col_max, :])
        # elif band_min != None and band_max != None:
                # output = np.array(data[row_min:row_max, col_min:col_max, band_min:band_max])
    else:
        data, _ = envi_opener(filename)
        # if band_min == None and band_max == None:
        if hdr['interleave'] == 'bil':
            output = np.array(data[row_min:row_max, :, col_min:col_max])
            output = output.transpose((0, 2, 1))

        elif hdr['interleave'] == 'bip':
            output = np.array(data[row_min:row_max, col_min:col_max, :])
        elif hdr['interleave'] == 'bsq':
            output = output.transpose((1, 2, 0))
            output = np.array(data[:, row_min:row_max, col_min:col_max])
        # elif band_min != None and band_max != None:
            # if hdr['interleave'] == 'bil':
            #     output = np.array(data[row_min:row_max, band_min:band_max, col_min:col_max])
            #     output = output.transpose((0, 2, 1))
            # elif hdr['interleave'] == 'bip':
            #     output = np.array(data[row_min:row_max, col_min:col_max, band_min:band_max])
            # elif hdr['interleave'] == 'bsq':
            #     output = np.array(data[band_min:band_max, row_min:row_max, col_min:col_max])
            #     output = output.transpose((1, 2, 0))
        # else:
        #     print("Please specify the band range!")
    # if hdr['scale_factor'] != 0 and hdr['scale_factor'] != 1:
    #     output = output/float(hdr['scale_factor'])
    #     hdr['scale_factor'] = 1
    
    f_name, _ = os.path.splitext(filename)
    if save == True:
        save_image(f_name + f"_envi_({row_min}_{row_max},{col_min}_{col_max})" +'.hdr', output, force=True, ext="raw")
    return output

def read_rgb(filename, red=None, green=None, blue=None, save=False):
    hdr = read_hdr(filename)
    rgb = np.ndarray((hdr['lines'], hdr['samples'], 3))

    if red == None:
        try:
            red = int(hdr['default bands'][0])
        except:
            pass
    if green == None:
        try:
            green = int(hdr['default bands'][1])
        except:
            pass
    if blue == None:
        try:
            blue = int(hdr['default bands'][2])
        except:
            pass

    if red is None or green is None or blue is None:
        print("Please specify the RGB value!")
    else:
        r_band = read_band(filename, red)
        g_band = read_band(filename, green)
        b_band = read_band(filename, blue)
    
    try:
        rgb[:,:,0] = r_band/np.max(r_band)
        rgb[:,:,1] = g_band/np.max(g_band)
        rgb[:,:,2] = b_band/np.max(b_band)
        rgb = rgb*255
        rgb = rgb.astype(int)
    except:
        pass

    if save:
        f_name, _ = os.path.splitext(filename)
        plt.imsave(f_name + f"_rgb_({red},{green},{blue})" +'.png', rgb, dpi=500, format="png")
    return rgb


def read_reflectance(filename, row=0, col=0, white_corr=True, save=False):
    output = None
    data = read_pixel(filename, row=row, col=col, save=False)
    print(data.shape)
    if white_corr:
        white_ref_path = os.path.join(os.path.split(filename)[0], f'WHITEREF_{os.path.split(filename)[-1]}')
        white_ref = read_subcube(white_ref_path, save=False)
        white_slice = white_ref[:, col, :].ravel()
        output = data/white_slice.max(axis=0, keepdims=True)
    if save:
        f_name, _ = os.path.splitext(filename)
        plt.plot(output)
        plt.savefig(f_name + f"_pixel_({row},{col})_white_corrected" +'.png', bbox_inches='tight',transparent=False, pad_inches=0)
    return output

def illumination_correction(img):
    if not isinstance(img, np.ndarray):
        image = cv2.imread(img)
    else:
        image = img

    RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)#convert to RGB
    R,G,B = cv2.split(RGB)

    #Create a CLAHE object: The image is divided into small block 8x8 which they are equalized as usual.
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    #Applying this method to each channel of the color image
    output_2R = clahe.apply(R)
    output_2G = clahe.apply(G)
    output_2B = clahe.apply(B)

    #mergin each channel back to one
    img_output = cv2.merge((output_2R,output_2G,output_2B))
    #coverting image from RGB to Grayscale
    eq=cv2.cvtColor(img_output,cv2.COLOR_BGR2GRAY)
    #Using image thresholding to classify pixels as dark or light

    #This method provides changes in illumination and the contrast of the image is improved.
    # gauss = cv2.adaptiveThreshold(eq, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 17, 45)
    return eq


def image_registration(reference, target, features=5000, save=False):

    # Open the image files.
    img1_color = cv2.imread(target)       # Image to be aligned.
    img2_color = cv2.imread(reference)    # Reference image.

    # Convert to grayscale.
    img1 = cv2.cvtColor(img1_color, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)
    height, width = img2.shape

    # Create ORB detector with defined features.
    orb_detector = cv2.ORB_create(features) # change this value to get the best outcome.

    # Find keypoints and descriptors.
    # The first arg is the image, second arg is the mask (which is not reqiured in this case).
    kp1, d1 = orb_detector.detectAndCompute(img1, None)
    kp2, d2 = orb_detector.detectAndCompute(img2, None)

    # Match features between the two images.
    # We create a Brute Force matcher with Hamming distance as measurement mode.
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)

    # Match the two sets of descriptors.
    matches = matcher.match(d1, d2)

    # Sort matches on the basis of their Hamming distance.
    matches.sort(key = lambda x: x.distance)

    # Take the top 90 % matches forward.
    matches = matches[:int(len(matches)*90)]
    no_of_matches = len(matches)

    # Define empty matrices of shape no_of_matches * 2.
    p1 = np.zeros((no_of_matches, 2))
    p2 = np.zeros((no_of_matches, 2))

    for i in range(len(matches)):
        p1[i, :] = kp1[matches[i].queryIdx].pt
        p2[i, :] = kp2[matches[i].trainIdx].pt

    # Find the homography matrix.
    homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)

    # Use this matrix to transform the colored image wrt the reference image.
    transformed_img = cv2.warpPerspective(img1_color, homography, (width, height))

    # Save the output.
    if save:
        cv2.imwrite('output.jpg', transformed_img)
    return transformed_img[:,:,0]

def digital_inpainting(img, mask, methods=cv2.INPAINT_NS, save=False):
    dst = cv2.inpaint(img, mask, 3, methods)
    if save:
        cv2.imwrite('inpainted.png', dst)
    return dst


def rotate_clockwise(data):
    return np.rot90(data, k=-1)



def show(data):
    if len(data.shape) == 1:
        plt.plot(data)
    elif len(data.shape) == 2:
        plt.imshow(data, cmap='gray')
    elif len(data.shape) == 3:
        plt.imshow(data)
    else:
        print('Cannot show data with more than 4 dimensions!')
    plt.show()


def read_tif(path):
    img = Image.open(path)
    images = []
    for i in range(1, img.n_frames):
        img.seek(i)
        images.append(np.array(img))
    try:
        images = np.array(images)
    except:
        images = np.array(images[1:])
    finally:
        return images


def save_tif(array):
    pass


# Preview functions
# show(read_rgb("spec/Specim IQ/510.raw"))

# show(read_band("Colorchecker.hdr", 3, save=False))

# show(read_subcube("spec/Specim IQ/510.hdr",row_min=10,row_max=300, col_min=20,col_max=300,save=True)[:,:,10])

# show(read_pixel("spec/Specim IQ/510.hdr",200,200))

# show(read_reflectance("spec/Specim IQ/510.hdr",200,200))


# Image processing
# show(illumination_correction("spec/Specim IQ/510_grayscale_100.png"))

# show(image_registration("spec/Specim IQ/510_grayscale_100.png","spec/sCMOS/halogen_emptyname_0008_grayscale_200.png", features=4700))


