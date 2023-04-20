"""
This script captures and displays a live-feed of color, disparity and heatmap images.
The capturing process ceases when user press 'q'.
User can adjust the factor of maximum disparity (default 1) via argument, example:
    `python live_depth.py --maxd 4`

The resulting video from the capturing process is stored at ./output/videos/
Uncomment the image writing command to save images.
"""

import PyCapture2
import numpy as np
import cv2
import argparse
import os
from sys import exit

video_save_path = './output/videos'

def grab_video(cam, md):

    # Setting for video writing
    size = (fmt7_info.maxWidth, fmt7_info.maxHeight)
    color_img_array = []
    disp_img_array = []
    heatmap_img_array = []

    # Capture & display
    i = 0
    while (True):
        try:
            image = cam.retrieveBuffer()
            color = image.convert(PyCapture2.PIXEL_FORMAT.BGR)
        except PyCapture2.Fc2error as fc2Err:
            print('Error retrieving buffer : %s' % fc2Err)

    # Convert Pycapture2 raw image to processible raw image
        rawarray = np.array(image.getData(), dtype=np.uint8)
        left = rawarray[1::2].reshape((image.getRows(), image.getCols()))
        right = rawarray[0::2].reshape((image.getRows(), image.getCols()))
        # Key determine L/R is here: left starts from byte 1

        color_array = np.array(color.getData(), dtype=np.uint8)
        imgcolorB = color_array[0::3].reshape((image.getRows(), image.getCols()))
        imgcolorG = color_array[1::3].reshape((image.getRows(), image.getCols()))
        imgcolorR = color_array[2::3].reshape((image.getRows(), image.getCols()))
        color_image = cv2.merge([imgcolorB, imgcolorG, imgcolorR])
    # Generate disparity image
        disparity, heatmap = depth_map(
            left, right, md)  # Get the disparity map

    # Display images
        cv2.imshow('Color', color_image)
        cv2.imshow('Disparity', disparity)
        cv2.imshow('Heatmap', heatmap)

        color_img_array.append(color_image)
        disp_img_array.append(disparity)
        heatmap_img_array.append(disparity)

    # Quit when user press q
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        
    ## temp: Image writing
        # cv2.imwrite(f'./output/frames/depth/{i:08d}.png', heatmap)
        # cv2.imwrite(f'./output/frames/color/{i:08d}.png', color_image)
        # cv2.imwrite(f'./output/frames/disparity/{i:08d}.png', disparity)
        i += 1

    # Video writing
    if not os.path.exists(video_save_path):
        os.makedirs(video_save_path)
    out_color = cv2.VideoWriter(f'{video_save_path}/color.avi',cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
    out_disp = cv2.VideoWriter(f'{video_save_path}/disparity.avi',cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
    out_heat = cv2.VideoWriter(f'{video_save_path}/heatmap.avi',cv2.VideoWriter_fourcc(*'DIVX'), 30, size)

    for i in range(len(color_img_array)):
        out_color.write(color_img_array[i])
        out_disp.write(disp_img_array[i])
        out_heat.write(heatmap_img_array[i])

def depth_map(imgL, imgR, md):
    # SGBM Parameters -----------------
    window_size = 3

    left_matcher = cv2.StereoSGBM_create(
        minDisparity = 0,
        numDisparities = md * 16,  # max_disp has to be dividable by 16 f. E. HH 192, 256
        blockSize = 3,
        P1 = 8 * 3 * window_size**2,
        P2= 32 * 3 * window_size**2,
        disp12MaxDiff = 12,
        uniquenessRatio = 10,
        speckleWindowSize = 64,
        speckleRange = 2,
        preFilterCap = 63,
        mode = cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )
    right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
    # FILTER Parameters
    lmbda = 8000
    sigma = 3
    visual_multiplier = 6

    wls_filter = cv2.ximgproc.createDisparityWLSFilter(
        matcher_left=left_matcher)
    wls_filter.setLambda(lmbda)
    wls_filter.setSigmaColor(sigma)

    displ = left_matcher.compute(imgL, imgR)  # .astype(np.float32)/16
    dispr = right_matcher.compute(imgR, imgL)  # .astype(np.float32)/16
    displ = np.int16(displ)
    dispr = np.int16(dispr)
    # important to put "imgL" here!!!
    filteredImg = wls_filter.filter(displ, imgL, None, dispr)

    filteredImg = cv2.normalize(
        src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX)
    filteredImg = np.uint8(filteredImg)
    heatmap = cv2.applyColorMap(filteredImg, cv2.COLORMAP_JET)
    return filteredImg, heatmap


if __name__ == '__main__':

    df_maxd = 1      # Default maximum disparity = 1 * 16
    parser = argparse.ArgumentParser(description='Disparity setting')
    parser.add_argument('--maxd', type=int, required=False,
                        default=df_maxd, help='Maximum disparity coefficient')
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
    grab_video(c, args.maxd)
    c.stopCapture()

# Disable camera embedded timestamp
    c.disconnect()
    print('DONE')