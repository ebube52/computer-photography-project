
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def apply_film_effect(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to the grayscale image
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Add graininess to the image by generating random pixel intensity values
    grain = np.zeros_like(gray, dtype=np.uint8)
    cv2.randu(grain, 0, 255)
    noisy_image = cv2.addWeighted(blurred, 0.5, grain, 0.5, 0)
    
    # Increase contrast using histogram equalization
    equalized = cv2.equalizeHist(noisy_image)
    
    return equalized

def apply_effect_on_click():
    image_path = filedialog.askopenfilename()  # Ask user to select an image
    if image_path:
        image = cv2.imread(image_path)
        if image is None:
            print("Error: Unable to load the image.")
        else:
            filtered_image = apply_film_effect(image)
            # Convert the OpenCV image to PIL format for displaying in tkinter
            filtered_image_rgb = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(filtered_image_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            label.configure(image=img_tk)
            label.image = img_tk  # Keep a reference to prevent garbage collection

# Create the main window
root = tk.Tk()
root.title("Film Effect App")

# Create a button to apply the effect
apply_button = tk.Button(root, text="Apply Film Effect", command=apply_effect_on_click)
apply_button.pack()

# Create a label to display the image
label = tk.Label(root)
label.pack()

# Run the application
root.mainloop()

