import os 
from tkinter import Tk, Frame, filedialog, Label, Button, Canvas, Entry, END, CENTER, BOTH

import numpy as np
from PIL import Image, ImageTk

from envi_code import *
from editBar import EditBar
from imageViewer import ImageViewer
from customScale import CustomScale


setting = {
    'menu_title_font': ("Verdana", 35),
    'page_title_font': ("Verdana", 20),
    'page_title_rely': 0.02,
    'menu_btn_width': 21,   # or set any value larger than 20
    'menu_btn_height': None,
    'menu_btn_font': None,
    'canvas_preview':(1100,780),

}


class App(Tk):
    # __init__ function for class App
    def __init__(self, *args, **kwargs):
        
        # __init__ function for class Tk
        Tk.__init__(self, *args, **kwargs)


        self.state('zoomed')
        self.title("ENVI Editor")
        self.geometry("1680x997")
        self.minsize(750,400)
        self.resizable(True, True)




        # creating a container
        container = Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.config(bg="white")
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)


        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting of the different page layouts
        for F in (StartPage, Page1, Page2, Page3, Page4, Page5, Page6, Page7, Page8, Page9):
            frame = F(container, self)
            # initializing frame of that object from startpage, page1, page2 respectively with for loop
            self.frames[F] = frame
            frame.config(width=1680, height=997)
            
            frame.grid(row = 0, column = 0, sticky ="nsew")
        
        self.show_frame(StartPage)

    
    def openfile(self, entryBox):
        filename = filedialog.askopenfilename(
                                            initialdir=os.getcwd(),
                                            title="Select spectral file",
                                            filetypes=(
                                                ("Spectral file", "*.hdr"),
                                                ))
        entryBox.delete(0, END)
        entryBox.insert(END, filename)

    def fit_gray_to_canvas(self, canvas_width, canvas_height, array, filename):
        hdr = read_hdr(filename)
        img_width = hdr['samples']
        img_height = hdr['lines']
        aspect_ratio = img_width/img_height

        disp_norm = np.uint8(array)

        image = Image.fromarray(disp_norm)

        canvas_width = canvas_width
        canvas_height = canvas_height

        if aspect_ratio > canvas_width/canvas_height:
            image = image.resize((canvas_width, int(canvas_width/aspect_ratio)), Image.NEAREST)
        else:
            image = image.resize((int(canvas_height*aspect_ratio), canvas_height), Image.NEAREST)
        return image

    def fit_rgb_to_canvas(self, canvas_width, canvas_height, array, filename):
        hdr = read_hdr(filename)
        img_width = hdr['samples']
        img_height = hdr['lines']
        aspect_ratio = img_width/img_height

        array = np.uint8(array)

        image = Image.fromarray(array, 'RGB')


        canvas_width = canvas_width
        canvas_height = canvas_height

        if aspect_ratio > canvas_width/canvas_height:
            image = image.resize((canvas_width, int(canvas_width/aspect_ratio)))
        else:
            image = image.resize((int(canvas_height*aspect_ratio), canvas_height))
        return image


    # display the current frame passed as parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()



class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        label = Label(self, text ="ENVI Editor", font = setting['menu_title_font'])
        label.place(anchor=CENTER, relx=0.5, rely=0.2)

        button1 = Button(self, text ="Band Reader", 
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page1)
        )

        button1.place(anchor=CENTER, relx=0.2, rely=0.4)

        button2 = Button(self, text ="RGB Reader",
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page2)
        )
        button2.place(anchor=CENTER, relx=0.2, rely=0.5)

        button3 = Button(self, text ="Image Cropper", 
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page3)
        )
        button3.place(anchor=CENTER, relx=0.2, rely=0.6)

        button4 = Button(self, text ="Reflectance Reader",
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page4)
        )
        button4.place(anchor=CENTER, relx=0.2, rely=0.7)

        button5 = Button(self, text ="Illumination Correction",
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page5)
        )
        button5.place(anchor=CENTER, relx=0.5, rely=0.4)

        button6 = Button(self, text ="Digital Inpainting",
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page6)
        )
        button6.place(anchor=CENTER, relx=0.5, rely=0.5)

        button7 = Button(self, text ="Image Registration",
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page7)
        )
        button7.place(anchor=CENTER, relx=0.5, rely=0.6)

        button8 = Button(self, text ="Principal Component Analysis",
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page8)
        )
        button8.place(anchor=CENTER, relx=0.8, rely=0.4)

        button9 = Button(self, text ="Spectral Angel Mapper",
                    width = setting['menu_btn_width'],
                    height=setting['menu_btn_height'], 
                    font=setting['menu_btn_font'],
                    command = lambda : controller.show_frame(Page9)
        )
        button9.place(anchor=CENTER, relx=0.8, rely=0.5)



class Page1(Frame):
    def __init__(self, parent, controller):

        Frame.__init__(self, parent)
        
        def load_gray_image(entryBox):
            filename = entryBox.get()
            canvas_width = setting['canvas_preview'][0]
            canvas_height = setting['canvas_preview'][1]

            array = read_band(filename, band=0, save=False)
            hdr = read_hdr(filename)

            fitted_array = controller.fit_gray_to_canvas(canvas_width, canvas_height, array, filename)
            global img
            img = ImageTk.PhotoImage(fitted_array)

            canvas = Canvas(self, width=canvas_width, height=canvas_height)
            canvas.place(anchor=CENTER, relx=0.5, rely=0.53)

            canvas.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=img)

            try:
                current_band = Label(self, text =f"Current wavelength: {str(hdr['wavelength'][0])} nm", font = ("Verdana", 13))
                current_band.place(anchor=CENTER, relx=0.92, rely=0.9)
            except:
                pass

            def update_image(scale):
                band = int(float(scale.get()))
                new_array = read_band(filename, band=band, save=False)

                new_fitted_array = controller.fit_gray_to_canvas(canvas_width, canvas_height, new_array, filename)

                global new_img
                new_img = ImageTk.PhotoImage(new_fitted_array)
                canvas.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=new_img)

                try:
                    current_band.config(text = f"Current wavelength: {str(hdr['wavelength'][int(band)])} nm")
                except:
                    pass

            def save_image():
                band = int(float(scale_g.get()))
                read_band(filename, band=band, save=True)

            scale_g = CustomScale(self, from_=0, to=hdr['bands']-1, length=1000)
            scale_g.place(anchor=CENTER, relx=0.5, rely=0.96)

            update_btn = Button(self, text ="Update", command=lambda:update_image(scale_g), width=7)
            update_btn.place(anchor=CENTER, relx=0.9, y=150)

            save_btn = Button(self, text ="Save PNG", command=save_image, width=7)
            save_btn.place(anchor=CENTER, relx=0.9, y=200)

        label = Label(self, text ="Band Reader", font = setting['page_title_font'])
        label.pack()

        fileEntry = Entry(self, width=int(100))
        fileEntry.place(anchor=CENTER, relx=0.5, y = 52)

        home_btn = Button(self, text ="Home", command=lambda:controller.show_frame(StartPage), width=7)
        home_btn.place(anchor=CENTER, relx=0.1, y=50)

        selectButton = Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry), load_gray_image(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=50)

        reset_btn = Button(self, text ="Reset slider", command=lambda:load_gray_image(fileEntry), width=7)
        reset_btn.place(anchor=CENTER, relx=0.9, y=100)



class Page2(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        def load_rgb_image(entryBox):
            filename = entryBox.get()
            canvas_width = setting['canvas_preview'][0]
            canvas_height = setting['canvas_preview'][1]
            hdr = read_hdr(filename)

            canvas = Canvas(self, width=canvas_width, height=canvas_height)
            canvas.place(anchor=CENTER, relx=0.5, rely=0.53)



            scale_r = CustomScale(self, from_=0, to=hdr['bands']-1, length=400)
            scale_r.place(anchor=CENTER, relx=0.2, rely=0.96)
            scale_g = CustomScale(self, from_=0, to=hdr['bands']-1, length=400)
            scale_g.place(anchor=CENTER, relx=0.5, rely=0.96)
            scale_b = CustomScale(self, from_=0, to=hdr['bands']-1, length=400)
            scale_b.place(anchor=CENTER, relx=0.8, rely=0.96)
            
            
            if hdr['default bands']:
                red = int(hdr['default bands'][0])
                green = int(hdr['default bands'][1])
                blue = int(hdr['default bands'][2])
                scale_r.set(red)
                scale_g.set(green)
                scale_b.set(blue)
            else:
                red = 0
                green = 0
                blue = 0

            array = read_rgb(filename, red=red, green=green, blue=blue, save=False)
            fitted_array = controller.fit_rgb_to_canvas(canvas_width, canvas_height, array, filename)

            global img
            img = ImageTk.PhotoImage(fitted_array)

            canvas.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=img)

            try:
                current_bands = Label(self, text =f"({str(hdr['wavelength'][int(red)])}, {str(hdr['wavelength'][int(green)])}, {str(hdr['wavelength'][int(blue)])}) nm", font = ("Verdana", 13))
                current_bands.place(anchor=CENTER, relx=0.92, rely=0.9)
            except:
                pass

            def update_image(scale_r, scale_g, scale_b):
                red = int(float(scale_r.get()))
                green = int(float(scale_g.get()))
                blue = int(float(scale_b.get()))
                new_array = read_rgb(filename, red=red, green=green, blue=blue, save=False)
                new_fitted_array = controller.fit_rgb_to_canvas(canvas_width, canvas_height, new_array, filename)

                global new_img
                new_img = ImageTk.PhotoImage(new_fitted_array)
                canvas.create_image((int(canvas_width/2),int(canvas_height/2)), anchor=CENTER, image=new_img)
                try:
                    current_bands.config(text = f"({str(hdr['wavelength'][int(red)])}, {str(hdr['wavelength'][int(green)])}, {str(hdr['wavelength'][int(blue)])}) nm")
                except:
                    pass

            def save_image(scale_r, scale_g, scale_b):
                red = int(float(scale_r.get()))
                green = int(float(scale_g.get()))
                blue = int(float(scale_b.get()))
                read_rgb(filename, red=red, green=green, blue=blue, save=True)

            update_btn = Button(self, text ="Update", command=lambda:update_image(scale_r, scale_g, scale_b), width=7)
            update_btn.place(anchor=CENTER, relx=0.9, y=150)

            save_btn = Button(self, text ="Save PNG", command=lambda:save_image(scale_r, scale_g, scale_b), width=7)
            save_btn.place(anchor=CENTER, relx=0.9, y=200)

        label = Label(self, text ="RGB Reader", font = setting['page_title_font'])
        label.pack()

        fileEntry = Entry(self, width=int(100))
        fileEntry.place(anchor=CENTER, relx=0.5, y = 52)

        home_btn = Button(self, text ="Home", command=lambda:controller.show_frame(StartPage), width=7)
        home_btn.place(anchor=CENTER, relx=0.1, y=50)

        selectButton = Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry), load_rgb_image(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=50)

        reset_btn = Button(self, text ="Reset slider", command=lambda:load_rgb_image(fileEntry), width=7)
        reset_btn.place(anchor=CENTER, relx=0.9, y=100)

class Page3(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        label = Label(self, text ="Image Cropper", font = setting['page_title_font'])
        label.pack()

        self.return_btn = Button(self, text ="Home", command = lambda : controller.show_frame(StartPage), width=7)
        self.return_btn.place(anchor=CENTER, relx=0.1, y=50)

        self.filename = ""
        self.original_image = None
        self.processed_image = None
        self.is_image_selected = False
        self.is_draw_state = False
        self.is_crop_state = False

        self.is_spectral = False
        self.hdr = None
        self.current_band = None

        self.filter_frame = None
        self.adjust_frame = None
        

        self.operation = []


        self.editbar = EditBar(master=self)
        self.editbar.pack(pady=6)

        self.image_viewer = ImageViewer(master=self)
        self.image_viewer.pack(fill=BOTH, padx=20, pady=10, expand=1)


class Page4(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Reflectance Reader", font = setting['page_title_font'])
        label.pack()

        fileEntry=Entry(self, width=130)
        fileEntry.place(anchor=CENTER, relx=0.5, y = 56)

        return_btn = Button(self, text ="Home", command = lambda : controller.show_frame(StartPage), width=7)
        return_btn.place(anchor=CENTER, relx=0.1, y=54)

        selectButton=Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=54)


class Page5(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Illumination Correction", font = setting['page_title_font'])
        label.place(anchor=CENTER,relx=0.5, y=20)

        fileEntry=Entry(self, width=130)
        fileEntry.place(anchor=CENTER, relx=0.5, y = 56)

        return_btn = Button(self, text ="Home", command = lambda : controller.show_frame(StartPage), width=7)
        return_btn.place(anchor=CENTER, relx=0.1, y=54)

        selectButton=Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=54)


class Page6(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Digital Inpainting", font = setting['page_title_font'])
        label.pack()

        fileEntry=Entry(self, width=130)
        fileEntry.place(anchor=CENTER, relx=0.5, y = 56)

        return_btn = Button(self, text ="Home", command = lambda : controller.show_frame(StartPage), width=7)
        return_btn.place(anchor=CENTER, relx=0.1, y=54)

        selectButton=Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=54)



class Page7(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Image Registration", font = setting['page_title_font'])
        label.pack()

        fileEntry=Entry(self, width=130)
        fileEntry.place(anchor=CENTER, relx=0.5, y = 56)

        return_btn = Button(self, text ="Home", command = lambda : controller.show_frame(StartPage), width=7)
        return_btn.place(anchor=CENTER, relx=0.1, y=54)

        selectButton=Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=54)



class Page8(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Principal Component Analysis", font = setting['page_title_font'])
        label.pack()

        fileEntry=Entry(self, width=130)
        fileEntry.place(anchor=CENTER, relx=0.5, y = 56)

        return_btn = Button(self, text ="Home", command = lambda : controller.show_frame(StartPage), width=7)
        return_btn.place(anchor=CENTER, relx=0.1, y=54)

        selectButton=Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=54)



class Page9(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Spectral Angel Mapper", font = setting['page_title_font'])
        label.pack()

        fileEntry=Entry(self, width=130)
        fileEntry.place(anchor=CENTER, relx=0.5, y = 56)

        return_btn = Button(self, text ="Home", command = lambda : controller.show_frame(StartPage), width=7)
        return_btn.place(anchor=CENTER, relx=0.1, y=54)

        selectButton=Button(self, text="Select file", command=lambda:[controller.openfile(fileEntry)], width=7)
        selectButton.place(anchor=CENTER, relx=0.9, y=54)





app = App()    # Driver Code
app.mainloop()    # Start the mainloop
