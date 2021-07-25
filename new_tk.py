import os 

from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from PIL import Image, ImageTk
import numpy as np

from envi_code import *

from editBar import EditBar
from imageViewer import ImageViewer
from filterFrame import FilterFrame
from adjustFrame import AdjustFrame

import cv2

setting = {
    'menu_title_font': ("Verdana", 35),
    'page_title_font': ("Verdana", 20),
    'page_title_rely': 0.02,
    'menu_btn_width': 21, # or set any value larger than 20
    'menu_btn_height': None,
    'menu_btn_font': None,
    'canvas_preview':(1100,780),

}

def show_frame(frame):
    frame.tkraise()

def openfile(entryBox):
    filename = filedialog.askopenfilename(
                                        initialdir=os.getcwd(),
                                        title="Select hdr file or spectral file.",
                                        filetypes=(("header files", "*.hdr"),("all files", "*.*")))
    entryBox.delete(0, END)
    entryBox.insert(END, filename)

def fit_gray_to_canvas(canvas_width, canvas_height, array, filename):
    hdr = read_hdr(filename)
    img_width = hdr['samples']
    img_height = hdr['lines']
    aspect_ratio = img_width/img_height
    
    _min = np.amin(array)
    _max = np.amax(array)
    disp_norm = (array - _min) * 255.0 / (_max - _min)
    disp_norm = np.uint8(disp_norm)

    image = Image.fromarray(disp_norm)

    canvas_width = canvas_width
    canvas_height = canvas_height

    if aspect_ratio > canvas_width/canvas_height:
        image = image.resize((canvas_width, int(canvas_width/aspect_ratio)), Image.NEAREST)
    else:
        image = image.resize((int(canvas_height*aspect_ratio), canvas_height), Image.NEAREST)
    return image

def fit_rgb_to_canvas(canvas_width, canvas_height, array, filename):
    hdr = read_hdr(filename)
    img_width = hdr['samples']
    img_height = hdr['lines']
    aspect_ratio = img_width/img_height


    array = array*255
    array = array.astype(int)
    array = np.uint8(array)

    image = Image.fromarray(array, 'RGB')


    canvas_width = canvas_width
    canvas_height = canvas_height

    if aspect_ratio > canvas_width/canvas_height:
        image = image.resize((canvas_width, int(canvas_width/aspect_ratio)))
    else:
        image = image.resize((int(canvas_height*aspect_ratio), canvas_height))
    return image


window = Tk()
window.state('zoomed')
window.title("ENVI Editor")
window.geometry(f"1680x997")
window.minsize(750,400)
window.resizable(True, True)
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)



StartPage = Frame(window)
Page1 = Frame(window)
Page2 = Frame(window)
Page3 = Frame(window)
Page4 = Frame(window)
Page5 = Frame(window)
Page6 = Frame(window)
Page7 = Frame(window)
Page8 = Frame(window)
Page9 = Frame(window)


for frame in (StartPage, Page1, Page2, Page4, Page5, Page6, Page7, Page8, Page9):
    frame.grid(row=0, column=0, sticky='nsew')


show_frame(StartPage)

# ======================================== Custom Slider ========================================

class CustomScale(ttk.Scale):
    def __init__(self, master=None, **kw):
        kw.setdefault("orient", "horizontal")
        self.variable = kw.pop('variable', DoubleVar(master))
        ttk.Scale.__init__(self, master, variable=self.variable, **kw)
        self._style_name = '{}.custom.{}.TScale'.format(self, kw['orient'].capitalize()) # unique style name to handle the text
        self['style'] = self._style_name
        self.variable.trace_add('write', self._update_text)
        self._update_text()

    def _update_text(self, *args):
        style.configure(self._style_name, text="{:d}".format(int(self.variable.get())))


trough = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x02\x08\x06\x00\x00\x00r\xb6\r$\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x19tEXtSoftware\x00www.inkscape.org\x9b\xee<\x1a\x00\x00\x00\x15IDAT\x08\x99c\\\xb5j\xd5\x7f\x06\x06\x06\x06&\x06(\x00\x00.\x08\x03\x01\xa5\\\x04^\x00\x00\x00\x00IEND\xaeB`\x82'
slider = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x000\x00\x00\x000\x08\x06\x00\x00\x00W\x02\xf9\x87\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x1d\x87\x00\x00\x1d\x87\x01\x8f\xe5\xf1e\x00\x00\x00\x19tEXtSoftware\x00www.inkscape.org\x9b\xee<\x1a\x00\x00\x05\xa4IDATh\x81\xd5\x9a\xcfo\x1bE\x14\xc7?3\xcez\x13\xb7k7\xb1\x9c4\x07\xdaT \xe8\x11*\x0e\xe5\x04A\xaa\x80\x1cP\x13\xe2\xcd\x85\x1eB\xab\x1e\x81\x0b\xe2ohOpD\xa8p(\x95\xaa\x8d\xa0\xad\x04F\xfc\x90\xc2\xad\x1c\xa0\xaa8\x15\xd1\xaa\xa4\x97\xd6?b\xe2\x9f\xb1\xb3\xf6>\x0e\xf6\x86%q\x9a8mj\xf7s\xb2gv\xc7\xdf7\x9e\x9d7\xef\xbdU<\x06\x16\x17\x17\x07\xd2\xe9\xf4\xcb\xa1P\xe8\xb8\xe7yG\x95R\xcf\x01\x07\x80X\xfb\x92\x02\xb0""\xb7\xb5\xd6\xb7\x94R\xd7\xe3\xf1\xf8\xef\x93\x93\x93\x8dG\xfdm\xf5(\xa2s\xb9\xdc\x9b\xc0)\x11y\x0b\xb0\xba\x1c\xa2(")\xa5\xd4W\x89D\xe2\x87\xdd\x1a\xd3\xb5\x01\x8e\xe3\x0c\x01\xa7\x81\x8f\x80C~\xbba\x18\x0c\r\ra\x9a&\x86a\x10\n\x85\xd0Z\x03\xe0y\x1e\xcdf\x13\xd7u\xa9\xd7\xeb\xd4j5\xd6\xd6\xd6\x82\xc3\xde\x13\x91\xf3\xd5j\xf5\xc2\xfc\xfc|m\xcf\x0cXXX\x98\x11\x91O\x80g|\xd1\xd1h\x14\xcb\xb2\x18\x18\x18\xe8f(\x1a\x8d\x06\xa5R\x89b\xb1\x88\xeb\xba~\xf3\x92R\xea\x83d2ym\xa7\xe3\xec\xc8\x80K\x97.\r\x1b\x86q\x01\x98\x060M\x93\x91\x91\x11\xf6\xed\xdb\xd7\x95\xe8N\x88\x08\xd5j\x95|>O\xbd^\xf7\x9b\xbf6\x0c\xe3\xcc\xf4\xf4\xf4\xcav\xf7ok\xc0\xe5\xcb\x97\x8fi\xad\xbf\x01\x0ek\xad\x89\xc7\xe3D\xa3Q\x94\xda\xf5\xe3\xb3%\x85B\x81\xe5\xe5e<\xcf\x03\xb8\x0b\xcc\xd8\xb6}\xf3a\xf7<T\xc5\xc2\xc2\xc2k"r\r\x88\x9a\xa6\xc9\xf8\xf8x\xd7K\xa5[\x1a\x8d\x06\x0f\x1e<\xa0V\xab\x01\x94\x95R\xef$\x93\xc9\x1f\xb7\xba~K\x03\x1c\xc7y\x1dH\x01\xa6eY\x8c\x8e\x8e\xee\xc9\xacwBD\xc8d2\x94J%\x80\x9a\x88L\xcd\xcd\xcd-v\xba\xb6\xa3\xa2\xf6\xb2\xf9\x05\xb0b\xb1\x18\x89Db\xef\xd4n\x81\x88\x90\xcb\xe5(\x14\n\x00E\xe0\xd5N\xcbi\x93\x01W\xae\\9\xe0\xba\xee\r\xe0\xc8\x93\x9e\xf9Nd2\x19\x8a\xc5"\xc0=\xe0%\xdb\xb6\xf3\xc1~\xbd\xf1\x06\xd7u\xbf\x00\x8e\x98\xa6\xd9s\xf1\x00\x89D\x82\xc1\xc1Ah\xf9\x9c\xcf6\xf6\xff\xcf\x00\xc7q\xa6\x81i\xad5\xe3\xe3\xe3=\x17\x0f\xa0\x94bll\xccw\x8a\xb3\x8e\xe3\xbc\x1d\xec_7\xa0\xeda?\x01\x88\xc7\xe3{\xbe\xdbt\x83a\x18\xc4\xe3q\xff\xeb\xa7\xa9T\xca\xf4\xbf\x04\xff\x81\xd3\xc0!\xd34\x89F\xa3OR\xdf\x8e\x88\xc5b\x98\xa6\t0Q.\x97\xdf\xf3\xdb5\xb4\x0ef\xb4\xce6\x0c\x0f\x0f\xf7\xc5\xd2\xe9\xc4\xc8\xc8\x88\xff\xf1\xe3\xb6\xe6\x96\x01\xd9l\xf6\r\xe0\x90a\x18\xec\xdf\xbf\xbfG\xf2\xb6\'\x12\x89\x10\x0e\x87\x01\x0e\xe7r\xb9\x13\xf0\xdf\x12:\x05\xf4\xe5\xd2\t\xa2\x94\nN\xf0)\x00\xb5\xb8\xb88\x90\xcdf\x97\x81\xe8\xc4\xc4D_=\xbc\x9dp]\x97\xa5\xa5%h\x05Iq\x9dN\xa7_\x06\xa2\x86a\xf4\xbdxh\xedH\x86a\x00\xc4<\xcf;\xa6C\xa1\xd0q\x80\xa1\xa1\xa1\xde*\xeb\x82H$\x02\x80R\xea\x15\xedy\xdeQ\xc0\xdf\xa2\x9e\n\xda\xff\x00\xc0\x0b\xba\x1d\x80\x07\x1b\xfb\x9e\xf6N\x84R\xeay\r\x0c\x03\x84B\xa1^j\xea\x8a\x80\xd6\x03\x1a\xd8\x0f\xf4\xad\xf3\xeaD@\xab\xb5\xe94\xfa\xb4\xa1\x812\xb4\x02\x88\xa7\x85\x80\xd6\x92\x06\xfe\x01h6\x9b=\x13\xd4-\x01\xad\xffh\x11\xb9\r\x04s3}\x8f\xafUD\xfe\xd2Z\xeb[@0\'\xd3\xf7\x04\xb4\xfe\xa9\x9b\xcd\xe6\xaf\x00\xab\xab\xab\xbdS\xd4%\xbeV\x11\xb9\xae\xc7\xc6\xc6~\x03\n\xae\xeb\xd2h<r\xb2x\xcfi4\x1a\xfe\x12Z\xd1Z\xdf\xd0\x93\x93\x93\r\x11\xf9\x1e\xf0\xf30}M@c\xca\xb6\xed\xa6\xef\x07.\x02~\xfa\xa2o\x11\x91\xa0\x01\x17\xa1\x1d\xd0\x8c\x8e\x8e\xfe\x08\xdcs]\x97J\xa5\xd2#y\xdbS\xa9T\xfc\xb4\xfc\xdf\x89D\xe2gh\x1b\xd0^F\xe7\x01\xf2\xf9\xfc\xd6#\xf4\x18_\x9b\x88\x9c\xf3\x0b"\xebG\x89j\xb5z\x01X\xaa\xd7\xeb~:\xaf\xafXYY\xf1g\xff\xaeeY_\xfa\xed\xeb\x06\xcc\xcf\xcf\xd7D\xe4C\x80\xe5\xe5\xe5\xberl\x8dFc}\xf6\x95R\xefOMM\xad;\x82\xff\x1d\xe6\xe6\xe6\xe6\xae\x02_{\x9eG:\x9d\xee\x8b\xf3\x91\x88p\xff\xfe}<\xcfC)\xe5$\x93\xc9o\x83\xfd\x9bN\xa3\x86a\x9c\x01\xee\xd6j\xb5\xbe0"\x93\xc9\xf8\x9e\xf7\x8e\x88\x9c\xdd\xd8\xbf\xc9\x80vYg\x06(\x96\xcber\xb9\\O\x8c\x10\x11\xb2\xd9\xac\xbfm\x16\xb4\xd63\xb6moz8;\xc6\x03\xb6m\xdf\x14\x91\x93@\xadP(\x90\xc9d\x9e\xa8\x11"B:\x9d\xf67\x93\x9aR\xea\xe4\xec\xec\xec\x1f\x9d\xae\xddI\x89\xe9*\x103M\x93\x83\x07\x0f\xeey\xec\xbc\xb1\xc4D\xabN\xf6\xd3V\xd7o\x1bG:\x8e\xf3"\xf0\rp\xc4/\xf2\xc5b\xb1\xedn\xdb\x15\x1b\x8a|w\xb4\xd63[\xcd\xbc\xcf\x8e\x02\xe1v\xd5\xe6s`\x16\xfe+\xb3F"\x91G\x8e\xa5E\x84J\xa5B>\x9f_/~+\xa5\x1c\x119\xdbi\xcdo\xa4\xab_o\x17\x17>\x05&\xa0\x95\xde\xb0,kW\x85n\xd7u)\x97\xcb\x94J\xa5`\xd5\xfe\xaeR\xea\xfd\x8d[\xe5\xc3\xe8z\xfaR\xa9\x94\xd9\xce\xcf\x7f\x0c\x1c\xf6\xdb\xc3\xe10\x83\x83\x83\x84\xc3a\xc2\xe1\xf0\xfa\xab\x06"\x82\x88\xac\x1f\x83\xd7\xd6\xd6X]]\xdd\xe8(\xff\x16\x91s\x96e}\x19tR{b\x80O\xfbe\x8f\x13"\xf2.0E\xeb\xed\x94nX\x11\x91\xef\x94R_\x01?\xd9\xb6\xbd\xab\xa0\xfc\xb1$\x83\x1c\xc7\ty\x9ewL)\xf5\x8aR\xea(\xf0,\x10\x07\xfc|}\x11X\xa6\xe5\x8cn\x89\xc8u\xad\xf5\x8d\xdd\x8a\x0e\xf2/#\xf8\x81 \xf2;_\x08\x00\x00\x00\x00IEND\xaeB`\x82'

img_trough = PhotoImage(master=window, data=trough)
img_slider = PhotoImage(master=window, data=slider)
style = ttk.Style(window)
# create scale elements
style.element_create('custom.Scale.trough', 'image', img_trough)
style.element_create('custom.Scale.slider', 'image', img_slider)
# create custom layout
style.layout('custom.Horizontal.TScale',
            [('custom.Scale.trough', {'sticky': 'ew'}),
            ('custom.Scale.slider',
            {'side': 'left', 'sticky': '',
            'children': [('custom.Horizontal.Scale.label', {'sticky': ''})]
            })])
style.configure('custom.Horizontal.TScale', background='#0e0e0e')


# ======================================== StartPage ========================================
label = Label(StartPage, text ="ENVI Editor", font = setting['menu_title_font'])
label.pack()

button1 = Button(StartPage, text ="Band Reader", 
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page1))
button1.place(anchor=CENTER, relx=0.2, rely=0.4)

button2 = Button(StartPage, text ="RGB Reader",
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page2))
button2.place(anchor=CENTER, relx=0.2, rely=0.5)

button3 = Button(StartPage, text ="Image Cropper", 
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page3))
button3.place(anchor=CENTER, relx=0.2, rely=0.6)

button4 = Button(StartPage, text ="Reflectance Reader",
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page4))
button4.place(anchor=CENTER, relx=0.2, rely=0.7)

button5 = Button(StartPage, text ="Illumination Correction",
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page5))
button5.place(anchor=CENTER, relx=0.5, rely=0.4)

button6 = Button(StartPage, text ="Digital Inpainting",
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page6))
button6.place(anchor=CENTER, relx=0.5, rely=0.5)

button7 = Button(StartPage, text ="Image Registration",
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page7))
button7.place(anchor=CENTER, relx=0.5, rely=0.6)

button8 = Button(StartPage, text ="Principal Component Analysis",
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page8))
button8.place(anchor=CENTER, relx=0.8, rely=0.4)

button9 = Button(StartPage, text ="Spectral Angel Mapper",
            width = setting['menu_btn_width'],
            height=setting['menu_btn_height'], 
            font=setting['menu_btn_font'],
            command=lambda:show_frame(Page9))
button9.place(anchor=CENTER, relx=0.8, rely=0.5)

# ======================================== Page1 ========================================
# def load_gray_image1(entryBox):
#     filename = entryBox.get()
#     canvas_width = setting['canvas_preview'][0]
#     canvas_height = setting['canvas_preview'][1]

#     array = read_band(filename, band=0, normalize=True, save=False)
#     hdr = read_hdr(filename)

#     fitted_array = fit_gray_to_canvas(canvas_width, canvas_height, array, filename)
#     global img
#     img = ImageTk.PhotoImage(fitted_array)

#     canvas1 = Canvas(Page1, width=canvas_width, height=canvas_height)
#     canvas1.place(anchor=CENTER, relx=0.5, rely=0.53)

#     canvas1.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=img)

#     try:
#         current_band1 = Label(Page1, text =f"Current wavelength: {str(hdr['wavelength'][0])} nm", font = ("Verdana", 13))
#         current_band1.place(anchor=CENTER, relx=0.92, rely=0.9)
#     except:
#         pass

#     def update_image1(scale):
#         band = int(float(scale.get()))
#         new_array = read_band(filename, band=band, normalize=True, save=False)

#         new_fitted_array = fit_gray_to_canvas(canvas_width, canvas_height, new_array, filename)

#         global new_img
#         new_img = ImageTk.PhotoImage(new_fitted_array)

#         canvas1.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=new_img)

#         current_band1.config(text = f"Current wavelength: {str(hdr['wavelength'][int(band)])} nm")

#     def save_image1():
#         band = int(float(scale_g1.get()))
#         read_band(filename, band=band, normalize=True, save=True)

#     scale_g1 = CustomScale(Page1, from_=0, to=hdr['bands']-1, length=1000)
#     scale_g1.place(anchor=CENTER, relx=0.5, rely=0.96)

#     update_btn1 = Button(Page1, text ="Update", command=lambda:update_image1(scale_g1), width=7)
#     update_btn1.place(anchor=CENTER, relx=0.9, y=150)

#     save_btn1 = Button(Page1, text ="Save PNG", command=save_image1, width=7)
#     save_btn1.place(anchor=CENTER, relx=0.9, y=200)

label1 = Label(Page1, text ="Band Reader", font = setting['page_title_font'])
label1.place(anchor=CENTER, relx=0.5, y=20)

# fileEntry1 = Entry(Page1, width=int(100))
# fileEntry1.place(anchor=CENTER, relx=0.5, y = 52)

return_btn1 = Button(Page1, text ="Home", command=lambda:show_frame(StartPage), width=7)
return_btn1.place(anchor=CENTER, relx=0.1, y=50)

# selectButton1 = Button(Page1, text="Select file", command=lambda:[openfile(fileEntry1), load_gray_image1(fileEntry1)], width=7)
# selectButton1.place(anchor=CENTER, relx=0.9, y=50)

# reset_btn1 = Button(Page1, text ="Reset slider", command=lambda:load_gray_image1(fileEntry1), width=7)
# reset_btn1.place(anchor=CENTER, relx=0.9, y=100)


# ======================================== Page2 ========================================
# def load_rgb_image(entryBox):
#     filename = entryBox.get()
#     canvas_width = setting['canvas_preview'][0]
#     canvas_height = setting['canvas_preview'][1]
#     hdr = read_hdr(filename)

#     canvas2 = Canvas(Page2, width=canvas_width, height=canvas_height)
#     canvas2.place(anchor=CENTER, relx=0.5, rely=0.53)

#     scale_2r = CustomScale(Page2, from_=0, to=hdr['bands']-1, length=400)
#     scale_2r.place(anchor=CENTER, relx=0.2, rely=0.96)
#     scale_2g = CustomScale(Page2, from_=0, to=hdr['bands']-1, length=400)
#     scale_2g.place(anchor=CENTER, relx=0.5, rely=0.96)
#     scale_2b = CustomScale(Page2, from_=0, to=hdr['bands']-1, length=400)
#     scale_2b.place(anchor=CENTER, relx=0.8, rely=0.96)
    
    
#     if hdr['default bands']:
#         red = int(hdr['default bands'][0])
#         green = int(hdr['default bands'][1])
#         blue = int(hdr['default bands'][2])
#         scale_2r.set(red)
#         scale_2g.set(green)
#         scale_2b.set(blue)
#     else:
#         red = 0
#         green = 0
#         blue = 0

#     array = read_rgb(filename, red=red, green=green, blue=blue, save=False)
#     fitted_array = fit_rgb_to_canvas(canvas_width, canvas_height, array, filename)

#     global img
#     img = ImageTk.PhotoImage(fitted_array)

#     canvas2.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=img)

#     try:
#         current_band2 = Label(Page2, text =f"({str(hdr['wavelength'][int(red)])}, {str(hdr['wavelength'][int(green)])}, {str(hdr['wavelength'][int(blue)])}) nm", font = ("Verdana", 13))
#         current_band2.place(anchor=CENTER, relx=0.92, rely=0.9)
#     except:
#         pass

#     def update_image2(scale_r, scale_g, scale_b):
#         red = int(float(scale_r.get()))
#         green = int(float(scale_g.get()))
#         blue = int(float(scale_b.get()))
#         new_array = read_rgb(filename, red=red, green=green, blue=blue, save=False)

#         new_fitted_array = fit_rgb_to_canvas(canvas_width, canvas_height, new_array, filename)

#         global new_img

#         new_img = ImageTk.PhotoImage(new_fitted_array)

#         canvas2.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=new_img)

#         current_band2.config(text = f"({str(hdr['wavelength'][int(red)])}, {str(hdr['wavelength'][int(green)])}, {str(hdr['wavelength'][int(blue)])}) nm")


#     def save_image2(scale_r, scale_g, scale_b):
#         red = int(float(scale_r.get()))
#         green = int(float(scale_g.get()))
#         blue = int(float(scale_b.get()))
#         read_rgb(filename, red=red, green=green, blue=blue, save=True)

#     update_btn2 = Button(Page2, text ="Update", command=lambda:update_image2(scale_2r, scale_2g, scale_2b), width=7)
#     update_btn2.place(anchor=CENTER, relx=0.9, y=150)

#     save_btn2 = Button(Page2, text ="Save PNG", command=lambda:save_image2(scale_2r, scale_2g, scale_2b), width=7)
#     save_btn2.place(anchor=CENTER, relx=0.9, y=200)

label2 = Label(Page2, text ="RGB Reader", font = setting['page_title_font'])
label2.place(anchor=CENTER, relx=0.5, y=20)

# fileEntry2 = Entry(Page2, width=int(100))
# fileEntry2.place(anchor=CENTER, relx=0.5, y = 52)

return_btn2 = Button(Page2, text ="Home", command=lambda:show_frame(StartPage), width=7)
return_btn2.place(anchor=CENTER, relx=0.1, y=50)

# selectButton2 = Button(Page2, text="Select file", command=lambda:[openfile(fileEntry2), load_rgb_image(fileEntry2)], width=7)
# selectButton2.place(anchor=CENTER, relx=0.9, y=50)

# reset_btn2 = Button(Page2, text ="Reset slider", command=lambda:load_rgb_image(fileEntry2), width=7)
# reset_btn2.place(anchor=CENTER, relx=0.9, y=100)

# ======================================== Page3 ========================================


window.mainloop()