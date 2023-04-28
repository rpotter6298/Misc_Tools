import subprocess
from tkinter import Tk, Label, Button, filedialog, OptionMenu, StringVar
from tkinter.ttk import Combobox
from merge_images_funct import merge_images
from PIL import Image


class App:
    def __init__(self, master):
        self.mode = StringVar()
        self.mode.set("centered")

        self.master = master
        master.title("Image Stacker")

        # Create labels for the input image file paths
        self.image1_label = Label(master, text="Image 1: No file selected")
        self.image2_label = Label(master, text="Image 2: No file selected")
        self.image1_label.pack()
        self.image2_label.pack()

        # Create buttons to select the input images
        self.image1_button = Button(
            master, text="Select Image 1", command=self.select_image1
        )
        self.image2_button = Button(
            master, text="Select Image 2", command=self.select_image2
        )
        self.image1_button.pack()
        self.image2_button.pack()

        # Create labels for the output image file path
        self.output_label = Label(master, text="Output: No file selected")
        self.output_label.pack()

        # Create a button to select the output image file path
        self.output_button = Button(
            master, text="Select Output", command=self.select_output
        )
        self.output_button.pack()

        # Create a dropdown menu to select the merge mode
        self.mode_var = Combobox(
            master, values=["centered", "aligned"], state="readonly"
        )
        self.mode_var.set("centered")
        self.mode_label = Label(master, text="Merge mode:")
        self.mode_label.pack()
        self.mode_var.pack()

        # Create a button to stack the input images and save the result
        self.stack_button = Button(
            master, text="Stack Images", command=self.stack_images
        )
        self.stack_button.pack()

    def select_image1(self):
        self.image1_path = filedialog.askopenfilename(
            title="Select Image 1",
            filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg")),
        )
        self.image1_label.config(text="Image 1: {}".format(self.image1_path))

    def select_image2(self):
        self.image2_path = filedialog.askopenfilename(
            title="Select Image 2",
            filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg")),
        )
        self.image2_label.config(text="Image 2: {}".format(self.image2_path))

    def select_output(self):
        self.output_path = filedialog.asksaveasfilename(
            title="Save Output As",
            defaultextension=".png",
            filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg")),
        )
        self.output_label.config(text="Output: {}".format(self.output_path))

    def stack_images(self):
        # Load the input images
        image1 = Image.open(self.image1_path)
        image2 = Image.open(self.image2_path)

        mode = self.mode_var.get()  # Get the selected mode from the dropdown menu

        # Merge the images using the selected mode
        composite_image = merge_images(image1, image2, mode)

        # Save the composite image to the selected output file path
        composite_image.save(self.output_path)

        # Show a success message
        success_label = Label(self.master, text="Image stacking successful")
        success_label.pack()


# Create the Tkinter app and run the main loop
root = Tk()
app = App(root)
root.mainloop()
