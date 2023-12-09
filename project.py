import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import glob

def apply_film_effect(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
    grain = np.zeros_like(gray, dtype=np.uint8)
    cv2.randn(grain, 0, 255)
    noisy_image = cv2.addWeighted(blurred, 0.5, grain, 0.5, 0)
    equalized = cv2.equalizeHist(noisy_image)
    return equalized

def apply_effect_on_click():
    image_path = filedialog.askopenfilename()
    if image_path:
        image = cv2.imread(image_path)
        if image is None:
            print("Error: Unable to load the image.")
        else:
            filtered_image = apply_film_effect(image)
            filtered_image_rgb = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2RGB)
            img = Image.fromarray(filtered_image_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            label.configure(image=img_tk)
            label.image = img_tk

def stitch_images():
    image_paths = glob.glob('unstitchedImages/*.jpg')
    images = []

    for image in image_paths:
        img = cv2.imread(image)
        if img is not None:
            images.append(img)
        else:
            print(f"Error: Unable to load image {image}")

    if len(images) < 2:
        print("Insufficient images for stitching")
    else:
        imageStitcher = cv2.Stitcher_create()
        status, stitched_img = imageStitcher.stitch(images)

        if status == cv2.Stitcher_OK:
            cv2.imwrite("stitchedOutput.png", stitched_img)
            cv2.imshow("Stitched Image", stitched_img)
            cv2.waitKey(0)

            stitched_img = cv2.copyMakeBorder(stitched_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(0, 0, 0))
            gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
            _, thresh_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                areaOI = max(contours, key=cv2.contourArea)
                mask = np.zeros(thresh_img.shape, dtype="uint8")
                x, y, w, h = cv2.boundingRect(areaOI)
                cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

                minRectangle = mask.copy()
                sub = mask.copy()

                while cv2.countNonZero(sub) > 0:
                    minRectangle = cv2.erode(minRectangle, None)
                    sub = cv2.subtract(minRectangle, thresh_img)

                contours, _ = cv2.findContours(minRectangle, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if len(contours) > 0:
                    areaOI = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(areaOI)
                    stitched_img = stitched_img[y:y + h, x:x + w]

                    cv2.imwrite("stitchedOutputProcessed.png", stitched_img)
                    cv2.imshow("Stitched Image Processed", stitched_img)
                    cv2.waitKey(0)
                else:
                    print("Unable to find contours in the masked image")
            else:
                print("No contours found in the thresholded image")
        else:
            print("Stitching was unsuccessful")

root = tk.Tk()
root.title("Combined App")

apply_button = tk.Button(root, text="Apply Film Effect", command=apply_effect_on_click)
apply_button.pack()

label = tk.Label(root)
label.pack()

stitch_button = tk.Button(root, text="Stitch Images", command=stitch_images)
stitch_button.pack()

root.mainloop()
