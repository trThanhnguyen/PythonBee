"""
This script captures images infinitely and display them until user press 'q'
Resulting frames are decoded into raw stereo images (Left and Right).
The infomation of format 7 mode 3 of the camera is also shown.
The resulting image is saved locally in ./output/stereo directory.

Color image: left camera (with PAN 0 and Little endian (Flycapture default settings))
"""

import PyCapture2
from sys import exit
import numpy as np
import cv2
import os

save_path = './output/stereo'
if not os.path.exists(save_path):
    os.makedirs(save_path)


def print_format7_capabilities(fmt7_info):
    print('\nFormat 7 original capabilities:')
    print(f'\tMode: {fmt7_info.mode}')
    print('\tMax image pixels ({}, {}):'.format(fmt7_info.maxWidth, fmt7_info.maxHeight))
    print('\tImage unit size: (imageHStepSize, imageVStepSize) ({}, {})'.format(fmt7_info.imageHStepSize, fmt7_info.imageVStepSize))
    print('\tOffset unit size (offsetHStepSize, offsetVStepSize): ({}, {})'.format(fmt7_info.offsetHStepSize, fmt7_info.offsetVStepSize))
    print('\tPixel format bitfield: 0x{}'.format(fmt7_info.pixelFormatBitField))
    print()


def capture(cam):
    while True:
        i = 0
        try:
            image = cam.retrieveBuffer()
        except PyCapture2.Fc2error as fc2Err:
            print('Error retrieving buffer : %s' % fc2Err)

        # color = image.convert(PyCapture2.PIXEL_FORMAT.BGR)
        array = np.array(image.getData(), dtype=np.uint8)
        
        left = array[1::2].reshape((image.getRows(), image.getCols()))
        right = array[0::2].reshape((image.getRows(), image.getCols()))
        cv2.imshow('left', left)
        cv2.imshow('right', right)

        cv2.imwrite(f'left_{i}.png', left)
        cv2.imwrite(f'right_{i}.png', right)
        
        i += 1
    # Quit when user press q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':

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

# Print camera details
    fmt7_info, supported = c.getFormat7Info(PyCapture2.MODE.MODE_3)

# Print details of Format 7 
    print_format7_capabilities(fmt7_info)

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

# Capture
    print('Starting image capture...')
    c.startCapture()
    capture(c)
    c.stopCapture()
    print('Stopped image capture...')

# Disconnect camera 
    c.disconnect()

    print('DONE')
