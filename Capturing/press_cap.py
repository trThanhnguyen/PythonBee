"""
This script provides a live feed of frames and let user determine when to save the image by pressing spacebar.
The capturing process will continue until user press 'q'.
The resulting images can be found in output/press
"""

import PyCapture2
from sys import exit
import numpy as np
import cv2
import os

save_path = './output/press'
if not os.path.exists(save_path):
    os.makedirs(save_path)


def grab_images(cam):
    i = 0
    while True:
    # for i in range(number_of_images):
        k = cv2.waitKey(1)
        try:
            image = cam.retrieveBuffer()
            array = np.array(image.getData(), dtype=np.uint8)
            left = array[1::2].reshape((image.getRows(), image.getCols()))
            right = array[0::2].reshape((image.getRows(), image.getCols()))

        # Display captured images and write
            cv2.imshow(f'left', left)
            cv2.imshow(f'right', right)
            if k%256 ==32: 
                cv2.imwrite(f'{save_path}/left_{i:04}.png', left)
                cv2.imwrite(f'{save_path}/right_{i:04}.png', right)
                print(f'Frame {i} written.')
                i += 1

        except PyCapture2.Fc2error as fc2Err:
            print('Error retrieving buffer : %s' % fc2Err)
            continue

        if k & 0xFF == ord('q'):
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
    fmt7_info, supported = c.getFormat7Info(PyCapture2.MODE.MODE_3)

# Check whether the chosen format is supported
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
    print('Starting image capture...')
    c.startCapture()
    print('Ready!')
    print("Press 'SPACE' to capture or press 'q' to quit.")
    grab_images(c)
    c.stopCapture()
    print('Stopped image capture...')

# Disconnect the camera
    c.disconnect()
    print('DONE')

