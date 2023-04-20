#=============================================================================
# Copyright 2017 FLIR Integrated Imaging Solutions, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ('Confidential Information'). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
#=============================================================================

import PyCapture2
from sys import exit

def print_build_info():
    lib_ver = PyCapture2.getLibraryVersion()
    print('PyCapture2 library version: %d %d %d %d' % (lib_ver[0], lib_ver[1], lib_ver[2], lib_ver[3]))
    print()

def print_camera_info(cam):
    cam_info = cam.getCameraInfo()
    print('\n*** CAMERA INFORMATION ***\n')
    print('Serial number - %d' % cam_info.serialNumber)
    print('Camera model - %s' % cam_info.modelName)
    print('Camera vendor - %s' % cam_info.vendorName)
    print('Sensor - %s' % cam_info.sensorInfo)
    print('Resolution - %s' % cam_info.sensorResolution)
    print('Firmware version - %s' % cam_info.firmwareVersion)
    print('Firmware build time - %s' % cam_info.firmwareBuildTime)
    print()

def print_format7_capabilities(fmt7_info):
    print('Max image pixels: ({}, {})'.format(fmt7_info.maxWidth, fmt7_info.maxHeight))
    print('Image unit size: ({}, {})'.format(fmt7_info.imageHStepSize, fmt7_info.imageVStepSize))
    print('Offset unit size: ({}, {})'.format(fmt7_info.offsetHStepSize, fmt7_info.offsetVStepSize))
    print('Pixel format bitfield: 0x{}'.format(fmt7_info.pixelFormatBitField))
    print()

def enable_embedded_timestamp(cam, enable_timestamp):
    embedded_info = cam.getEmbeddedImageInfo()
    if embedded_info.available.timestamp:
        cam.setEmbeddedImageInfo(timestamp = enable_timestamp)
        if enable_timestamp:
            print('\nTimeStamp is enabled.\n')
        else:
            print('\nTimeStamp is disabled.\n')

def grab_images(cam, num_images_to_grab):
    prev_ts = None
    for i in range(num_images_to_grab):
        try:
            image = cam.retrieveBuffer()
        except PyCapture2.Fc2error as fc2Err:
            print('Error retrieving buffer : %s' % fc2Err)
            continue

        ts = image.getTimeStamp()
        if prev_ts:
            diff = (ts.cycleSeconds - prev_ts.cycleSeconds) * 8000 + (ts.cycleCount - prev_ts.cycleCount)
            print('timestamp [ %d %d ] - %d' % (ts.cycleSeconds, ts.cycleCount, diff))
        prev_ts = ts

    print('Saving the last image to fc2CustomImageEx.png')
    image.save('fc2CustomImageEx.png'.encode('utf-8'), PyCapture2.IMAGE_FILE_FORMAT.PNG)

#
# Example Main
#

# Print PyCapture2 Library Information
print_build_info()

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
print_camera_info(c)
fmt7_info, supported = c.getFormat7Info(0)
print_format7_capabilities(fmt7_info)

# Check whether pixel format mono8 is supported
if PyCapture2.PIXEL_FORMAT.MONO8 & fmt7_info.pixelFormatBitField == 0:
    print('Pixel format is not supported\n')
    exit()

# Configure camera format7 settings
fmt7_img_set = PyCapture2.Format7ImageSettings(0, 0, 0, fmt7_info.maxWidth, fmt7_info.maxHeight, PyCapture2.PIXEL_FORMAT.MONO8)
fmt7_pkt_inf, isValid = c.validateFormat7Settings(fmt7_img_set)
if not isValid:
    print('Format7 settings are not valid!')
    exit()
c.setFormat7ConfigurationPacket(fmt7_pkt_inf.recommendedBytesPerPacket, fmt7_img_set)

# Enable camera embedded timestamp
enable_embedded_timestamp(c, True)

print('Starting image capture...')
c.startCapture()
grab_images(c, 10)
c.stopCapture()

# Disable camera embedded timestamp
enable_embedded_timestamp(c, False)
c.disconnect()

input('Done! Press Enter to exit...\n')