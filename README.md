# PythonBee
A python library for Bumblebee2 1394a Stereo Camera.
## Introduction
Available libraries for Bumblebee2 Camera are written in C/C++, while modern applications take python as a usual language. Rewriting the apps is certainly not a favorable solution, therefore, it is helpful to have a Python library for the camera instead.
## Build steps
### 1. Download and install the FlyCapture SDK from the Point Grey Research website.
- You can download the FlyCapture SDK from the Point Grey Research website at https://www.flir.com/products/flycapture-sdk/. Follow the instructions provided to install the SDK on your system.
- If you are using conda, make sure to specify the path to your target environment in the SDK's installation step. Also, make sure your python version is compatible with the that in the SDK (current support 2.7, 3.5 and 3.6 only).

### 2. Install and import the PyCapture2 packages
- Open your terminal, with the proper python environment and run the following command:
```
    $ pip install pycapture2
```
- Import Pycapture2 in your python script and you should be good.
```
    import PyCapture2
```

## Deployment
For mere image acquisition tasks, using the examples in Demo is perfectly fine. However, if certain post processing is required, you should use the scripts in other folders.
