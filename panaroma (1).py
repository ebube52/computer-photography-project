# Import necessary libraries
import numpy as np
import cv2
import glob
import imutils
import tkinter as tk
from tkinter import filedialog

# Function to stitch images together
def stitch_images():
    # Get paths of all .jpg images in the 'unstitchedImages' folder
    image_paths = glob.glob('unstitchedImages/*.jpg')
    images = []

    # Load images and add them to the 'images' list
    for image in image_paths:
        img = cv2.imread(image)
        if img is not None:
            images.append(img)
        else:
            print(f"Error: Unable to load image {image}")

    # Check if there are at least 2 images for stitching
    if len(images) < 2:
        print("Insufficient images for stitching")
    else:
        # Create a Stitcher object and stitch the images
        imageStitcher = cv2.Stitcher_create()
        status, stitched_img = imageStitcher.stitch(images)

        # Check if stitching was successful
        if status == cv2.Stitcher_OK:
            # Save and display the stitched image
            cv2.imwrite("stitchedOutput.png", stitched_img)
            cv2.imshow("Stitched Image", stitched_img)
            cv2.waitKey(0)

            # Add a border to the stitched image
            stitched_img = cv2.copyMakeBorder(stitched_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(0, 0, 0))

            # Convert the stitched image to grayscale and create a thresholded image
            gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
            _, thresh_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

            # Find contours in the thresholded image
            contours = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            
            # Check if contours are found
            if len(contours) > 0:
                # Get the largest contour and create a mask
                areaOI = max(contours, key=cv2.contourArea)
                mask = np.zeros(thresh_img.shape, dtype="uint8")
                x, y, w, h = cv2.boundingRect(areaOI)
                cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

                # Find the minimum rectangle enclosing the mask
                minRectangle = mask.copy()
                sub = mask.copy()

                # Process the minimum rectangle to remove unwanted areas
                while cv2.countNonZero(sub) > 0:
                    minRectangle = cv2.erode(minRectangle, None)
                    sub = cv2.subtract(minRectangle, thresh_img)

                # Find contours in the processed minimum rectangle
                contours = cv2.findContours(minRectangle, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(contours)

                # Check if contours are found after processing
                if len(contours) > 0:
                    # Get the largest contour and crop the stitched image
                    areaOI = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(areaOI)
                    stitched_img = stitched_img[y:y + h, x:x + w]

                    # Save and display the processed stitched image
                    cv2.imwrite("stitchedOutputProcessed.png", stitched_img)
                    cv2.imshow("Stitched Image Processed", stitched_img)
                    cv2.waitKey(0)
                else:
                    print("Unable to find contours in the masked image")
            else:
                print("No contours found in the thresholded image")
        else:
            print("Stitching was unsuccessful")

# Create a Tkinter window
root = tk.Tk()
root.title("Image Stitching")

# Function to call when the button is clicked
def on_button_click():
    stitch_images()

# Create a button in the Tkinter window to trigger image stitching
button = tk.Button(root, text="Stitch Images", command=on_button_click)
button.pack()

root.mainloop()
