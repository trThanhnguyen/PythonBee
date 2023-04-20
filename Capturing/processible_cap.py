"""
This script captures stereo and color image from Bumbleebee2 camera.
The captured images are processed them to yeild processible frame instead of Pycapture2 images.
User can decide to save the images or not via arguments
The images are defaultly written, but can be adjust to show only.

Example: 
    python custom_cap.py --write_img 0

The capturing process ceases when user press 'q'.
"""

import PyCapture2
import numpy as np
import cv2
import argparse
from sys import exit
import os


def grab_images(cam, opt_write):
    if opt_write:
        # Prepare save directories
        left_save_path = './output/left'
        right_save_path = './output/right'
        color_save_path = './output/color'
        if not os.path.exists(left_save_path):
            os.makedirs(left_save_path)
        if not os.path.exists(right_save_path):
            os.makedirs(right_save_path)
        if not os.path.exists(color_save_path):
            os.makedirs(color_save_path)

    i = 0
# Capture image
    while (True):
        try:
            image = cam.retrieveBuffer()
        except PyCapture2.Fc2error as fc2Err:
            print('Error retrieving buffer : %s' % fc2Err)

    # Convert Pycapture2 raw image to processible raw image
        rawarray = np.array(image.getData(), dtype=np.uint8)
        left = rawarray[1::2].reshape((image.getRows(), image.getCols()))
        right = rawarray[0::2].reshape((image.getRows(), image.getCols()))
        # Key determine L/R is here: left starts from byte 1

    # Convert Pycapture2 raw image to Pycapture2 BGR image
        color = image.convert(PyCapture2.PIXEL_FORMAT.BGR)
    # Convert Pycapture2 BGR image to processible BGR image
        colorarray = np.array(color.getData(), dtype=np.uint8)
        imgcolorB = colorarray[0::3].reshape((image.getRows(), image.getCols()))
        imgcolorG = colorarray[1::3].reshape((image.getRows(), image.getCols()))
        imgcolorR = colorarray[2::3].reshape((image.getRows(), image.getCols()))
        imgcolor_merged = cv2.merge([imgcolorB, imgcolorG, imgcolorR])

    # Display images
        cv2.imshow('Left', left)
        cv2.imshow('right', right)
        cv2.imshow('color', imgcolor_merged)

        if opt_write:
            cv2.imwrite(f'{left_save_path}/{i:08}.png', left)
            cv2.imwrite(f'{right_save_path}/{i:08}.png', right)
            cv2.imwrite(f'{color_save_path}/{i:08}.png', imgcolor_merged)

        i += 1
    # Quit when user press q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    
    df_write = True      # Default maximum disparity = 1 * 16
    parser = argparse.ArgumentParser(description='Save output setting')
    parser.add_argument('--write_img', type=int, required=False,
                        default=df_write, help='Whether to save images')
    args = parser.parse_args()

# Ensure sufficient cameras are found
    bus = PyCapture2.BusManager()
    num_cams = bus.getNumOfCameras()
    print('Number of cameras detected: ', num_cams)
    if not num_cams:
        print('Insufficient number of cameras. Exiting...')
        exit()

# Select camera on 0th index
    c = PyCapture2.Camera()
    c.connect(bus.getCameraFromIndex(0))

# Get format7 info for image settings
    fmt7_info, supported = c.getFormat7Info(PyCapture2.MODE.MODE_3)

# Check whether pixel format mono8 is supported
    if PyCapture2.PIXEL_FORMAT.RAW16 & fmt7_info.pixelFormatBitField == 0:
        print('Pixel format is not supported\n')
        exit()

# Configure camera format7 settings
    fmt7_image_set = PyCapture2.Format7ImageSettings(PyCapture2.MODE.MODE_3, 0, 0, fmt7_info.maxWidth, fmt7_info.maxHeight, PyCapture2.PIXEL_FORMAT.RAW16)
    fmt7_pkt_inf, isValid = c.validateFormat7Settings(fmt7_image_set)
    if not isValid:
        print('Format7 settings are not valid!')
        exit()
    c.setFormat7ConfigurationPacket(fmt7_pkt_inf.maxBytesPerPacket, fmt7_image_set)

# Capturing
    c.startCapture()
    grab_images(c, args.write_img)
    c.stopCapture()

# Disable camera embedded timestamp
    c.disconnect()
    print('DONE')
