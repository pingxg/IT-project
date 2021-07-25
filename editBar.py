import os
from datetime import datetime
from tkinter import Frame, Button, Label, filedialog, CENTER, LEFT, NORMAL, DISABLED

import cv2

from filterFrame import FilterFrame
from adjustFrame import AdjustFrame
from customScale import CustomScale
from envi_code import *



class EditBar(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master=master)

        self.new_button = Button(self, text="Select")
        self.save_img_button = Button(self, text="Save")
        self.save_img_as_button = Button(self, text="Save As")
        self.crop_button = Button(self, text="Crop")
        self.rotate_clockwise_button = Button(self, text="Rotate")
        self.clear_button = Button(self, text="Clear")

        self.new_button.bind("<ButtonRelease>", self.new_button_released)
        self.save_img_button.bind("<ButtonRelease>", self.save_img_button_released)
        self.save_img_as_button.bind("<ButtonRelease>", self.save_img_as_button_released)
        self.crop_button.bind("<ButtonRelease>", self.crop_button_released)
        self.rotate_clockwise_button.bind("<ButtonRelease>", self.rotate_clockwise_button_released)
        self.clear_button.bind("<ButtonRelease>", self.clear_button_released)

        self.new_button.pack(side=LEFT)
        self.save_img_button.pack(side=LEFT)
        self.save_img_as_button.pack(side=LEFT)
        self.crop_button.pack(side=LEFT)
        self.rotate_clockwise_button.pack(side=LEFT)
        self.clear_button.pack(side=LEFT)


    def new_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.new_button:
            if self.master.is_draw_state:
                self.master.image_viewer.deactivate_draw()
            if self.master.is_crop_state:
                self.master.image_viewer.deactivate_crop()
            
            self.master.is_spectral = False
            self.master.operation = []
            # self.draw_button["state"] = NORMAL



            filename = filedialog.askopenfilename(
                initialdir=os.getcwd(),
                title="Select hdr file or image file.",
                filetypes=(

                    ("header or image files", "*.hdr"),
                    ("header or image files", "*.png"),
                    ("header or image files", "*.jpg"),
                    ("header or image files", "*.jpeg"),
                    ("header or image files", "*.tiff"),
                    ("header or image files", "*.tif"),
                    
                )
            )
            f_name, f_ext = os.path.splitext(filename)

            if f_ext in ['.hdr', '.HDR', 'img', 'dat', 'sli', 'hyspex', 'raw']:
                try:
                    self.slider.destroy()
                    self.current_band.destroy()
                    self.update_button.destroy()
                    self.apply_to_all_and_save_button.destroy()
                    self.adjust_button.destroy()
                    self.filter_button.destroy()
                    self.draw_button.destroy()

                except:
                    pass
                self.master.current_band = 0
                self.master.hdr = read_hdr(filename)
                self.master.is_spectral = True
                image = read_band(filename, band=self.master.current_band)

                self.master.return_btn.place(anchor=CENTER, relx=0.1, y=58)


                self.apply_to_all_and_save_button = Button(self, text="Apply to All and Save")
                self.apply_to_all_and_save_button.bind("<ButtonRelease>", self.apply_to_all_and_save_button_released)
                self.apply_to_all_and_save_button.pack(side=LEFT)

                self.update_button = Button(self, text="Update")
                self.update_button.bind("<ButtonRelease>", self.update_button_released)
                self.update_button.pack(side=LEFT)

                # self.slider = Scale(self, from_=0, to=int(self.master.hdr['bands'])-1, length=200, orient=HORIZONTAL, showvalue=1)
                self.slider = CustomScale(self, from_=0, to=int(self.master.hdr['bands'])-1, length=200,)
                self.slider.pack(side=LEFT, padx=5)
                try:

                    self.current_band = Label(self, text =f"{str(self.master.hdr['wavelength'][self.master.current_band])} nm", font = ("Verdana", 13))
                    self.current_band.pack(side=LEFT, padx=5)
                except:
                    pass

            else:
                try:
                    self.slider.destroy()
                    self.current_band.destroy()
                    self.update_button.destroy()
                    self.apply_to_all_and_save_button.destroy()
                    self.adjust_button.destroy()
                    self.filter_button.destroy()
                    self.draw_button.destroy()

                except:
                    pass

                self.draw_button = Button(self, text="Draw")
                self.draw_button.bind("<ButtonRelease>", self.draw_button_released)
                self.draw_button.pack(side=LEFT)

                # if 'rotation' in self.master.operation:
                #     if self.draw_button["state"] == NORMAL:
                #         self.draw_button["state"] = DISABLED

                self.filter_button = Button(self, text="Filter")
                self.filter_button.bind("<ButtonRelease>", self.filter_button_released)
                self.filter_button.pack(side=LEFT)

                self.adjust_button = Button(self, text="Adjust")
                self.adjust_button.bind("<ButtonRelease>", self.adjust_button_released)
                self.adjust_button.pack(side=LEFT)

                image = cv2.imread(filename)



            if image is not None:
                self.master.filename = filename
                self.master.original_image = image.copy()
                self.master.processed_image = image.copy()
                self.master.image_viewer.show_image()
                self.master.is_image_selected = True


    def save_img_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.save_img_button:
            if self.master.is_image_selected:
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()

                save_image = self.master.processed_image
                image_filename = self.master.filename
                current_time = datetime.now().strftime("%m%d%H%M%S")
                cv2.imwrite(f'{image_filename.split(".")[0]}_{current_time}.png', save_image)

    def save_img_as_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.save_img_as_button:
            if self.master.is_image_selected:
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()

                filename = filedialog.asksaveasfilename()
                current_time = datetime.now().strftime("%m%d%H%M%S")

                filename = f'{filename}_{current_time}.png'

                save_image = self.master.processed_image
                cv2.imwrite(filename, save_image)

                self.master.filename = filename

    def draw_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.draw_button:
            if self.master.is_image_selected:
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                else:
                    self.master.image_viewer.activate_draw()

    def crop_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.crop_button:
            if self.master.is_image_selected:
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()
                else:
                    self.master.image_viewer.activate_crop()

    def rotate_clockwise_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.rotate_clockwise_button:
            if self.master.is_image_selected:
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()
                self.master.processed_image = rotate_clockwise(self.master.processed_image.copy())
                self.master.image_viewer.show_image()

                self.master.operation.append("rotation")
                print(self.master.operation)

                # self.draw_button["state"] = DISABLED


    def filter_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.filter_button:
            if self.master.is_image_selected:
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()

                self.master.filter_frame = FilterFrame(master=self.master)
                self.master.filter_frame.grab_set()

    def adjust_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.adjust_button:
            if self.master.is_image_selected:
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()

                self.master.adjust_frame = AdjustFrame(master=self.master)
                self.master.adjust_frame.grab_set()

    def clear_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.clear_button:
            if self.master.is_image_selected:
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()
                try:
                    self.slider.set(0)
                except:
                    pass
                self.master.processed_image = self.master.original_image.copy()
                self.master.image_viewer.show_image()
                self.master.operation = []
                # self.draw_button["state"] = NORMAL



    def apply_to_all_and_save_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.apply_to_all_and_save_button:
            filename = self.master.filename

            hdr = self.master.hdr
            # data, hdr = envi_opener(filename)
            # data = read_bands(filename)
            data = read_subcube(filename=filename, hdr=hdr)

            print(data.shape)
            # for i in range(int(hdr['bands'])):

                # current_img = read_band(filename, band=i)

            while len(self.master.operation) != 0:
                current_operation = self.master.operation.pop(0)
                if current_operation == "rotation":
                    data = rotate_clockwise(data)
                    print(data.shape)
                else:
                    start_x = current_operation[0]
                    end_x = current_operation[1]
                    start_y = current_operation[2]
                    end_y = current_operation[3]
                    data = read_subcube(filename=filename, hdr=hdr, row_min=start_y, row_max=end_y, col_min=start_x, col_max=end_x)
            
            # output_array = np.asarray(output_array)
            # output_array = output_array.reshape((end_x-start_x, end_y-start_y, int(hdr['bands'])))
            f_name, _ = os.path.splitext(filename)
            current_time = datetime.now().strftime("%m%d%H%M%S")
            save_image(f'{f_name}_{current_time}.hdr', data, force=True, ext="raw")



    def update_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.update_button:
            if self.master.is_image_selected:
                if self.master.is_draw_state:
                    self.master.image_viewer.deactivate_draw()
                if self.master.is_crop_state:
                    self.master.image_viewer.deactivate_crop()
                self.master.current_band = int(float(self.slider.get()))
                self.master.processed_image = read_band(self.master.filename, band=self.master.current_band)
                try:

                    self.current_band.config(text = f"{str(self.master.hdr['wavelength'][int(self.master.current_band)])} nm")
                except:
                    pass

                self.master.image_viewer.show_image()
                self.master.operation = []
                # self.draw_button["state"] = NORMAL