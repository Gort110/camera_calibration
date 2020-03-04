# -*-coding:utf-8-*-

import ctypes  # ctypes.cast(), ctypes.POINTER(), ctypes.c_ushort
import os  # os.getcwd()
from pathlib import Path
import numpy as np  # pip install numpy
from PIL import Image as PIL_Image  # pip install Pillow
from arena_api.system import system
import time

master_camera = 0

def think_lucid_init():
    # Get connected devices ---------------------------------------------------

    # create_device function with no arguments would create a list of
    # device objects from all connected devices
    devices = system.create_device()
    print(f'Created {len(devices)} device(s):')
    try:
        device = devices
    except IndexError as ie:
        print('No device found!')
        raise ie
    # print("Device used in the example:")
    for index in range(len(device)):
        print("\t", "SerialNumber:", device[index].nodemap.get_node('DeviceSerialNumber').value, device[index])
    # set some features before streaming.--------------------------------------
    for i in range(len(device)):
        device[i].nodemap.get_node("Width").value = device[i].nodemap.get_node("Width").max
        device[i].nodemap.get_node("Height").value = device[i].nodemap.get_node("Height").max
        device[i].nodemap.get_node("PixelFormat").value = "RGB8"
        device[i].nodemap.get_node("DeviceStreamChannelPacketSize").value = 1400
        device[i].nodemap.get_node("GevSCPD").value = 30000
        device[i].nodemap.get_node('ExposureTime').value = 25000.0

        if i == master_camera:
            device[i].nodemap.get_node('LineSelector').value = 'Line2'
            device[i].nodemap.get_node('LineMode').value = 'Output'
            device[i].nodemap.get_node('LineSource').value = 'ExposureActive'
            device[i].nodemap.get_node('TriggerMode').value = 'On'
            device[i].nodemap.get_node('TriggerSource').value = 'Software'
            device[i].nodemap.get_node('TriggerSelector').value = 'FrameStart'#AcquisitionStart
            device[i].nodemap.get_node('TriggerActivation').value = 'RisingEdge'
        else:
            # set hardware trigger.--------------------------------------
            device[i].nodemap.get_node('LineSelector').value = 'Line2'
            device[i].nodemap.get_node('LineMode').value = 'Input'
            device[i].nodemap.get_node('LineSource').value = 'Off'
            device[i].nodemap.get_node('TriggerMode').value = 'On'
            device[i].nodemap.get_node('TriggerSource').value = 'Line2'
            device[i].nodemap.get_node('TriggerSelector').value = 'FrameStart'
            device[i].nodemap.get_node('TriggerActivation').value = 'RisingEdge'

    print('camera init success')
    return device

def think_lucid_save_image(device):

    # grab and save an image buffer -------------------------------------------
    for k in range(len(device)):
        # print(device[k].nodemap.get_node("DeviceSerialNumber").value, 'is Grabbing an image buffer')
        try:
            image_buffer = device[k].get_buffer(timeout=2000)  # optional args
        except:
            print(device[k].nodemap.get_node("DeviceSerialNumber").value, "Get image buffer failed")
            return

        # Method 1
        # dtype is uint8 because Buffer.data returns a list or bytes and pixel
        # format is also Mono8
        nparray = np.asarray(image_buffer.data, dtype=np.uint8)
        # reshape array for pillow
        nparray_reshaped = nparray.reshape((image_buffer.height,
                                            image_buffer.width, 3))# PixelFormat is RGB8(color)


        # nparray_reshaped = nparray.reshape((image_buffer.height,
        #                                     image_buffer.width))# PixelFormat is Mono8(gray)

        # Method 2
        # a more general way (not used in this simple example)
        #
        # Creates an already reshaped array so can be used directly with
        # pillow.
        # np.ctypeslib.as_array() detect that pdata is (uint8, c_ubyte) type so
        # it interprets each byte as an element.
        # for 16Bit images Buffer.pdata must be casted to (uint16, c_ushort)
        # usinf ctypes.cast(). after casting np.ctypeslib.as_array() can
        # interpret every two bytes as one array element (a pixel).
        #
        # nparray_reshaped = np.ctypeslib.as_array(
        #    image_buffer.pdata,
        #   (image_buffer.height, image_buffer.width))
        #

        # saving
        # print(device[k].nodemap.get_node('DeviceSerialNumber').value, "is saving image")
        png_name = f'{device[k].nodemap.get_node("DeviceSerialNumber").value}_from_{device[k].nodemap.get_node("PixelFormat").value}_to_png_with_pil_{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.png'
        png_array = PIL_Image.fromarray(nparray_reshaped)
        png_array.save(png_name)
        # print(f'Saved image path is: {Path(os.getcwd()) / png_name}')
        print(device[k].nodemap.get_node('DeviceSerialNumber').value, "save image success")
        device[k].requeue_buffer(image_buffer)
        time.sleep(1)


def start_camera_capture(device):
    print('Starting stream')
    for j in range(len(device)):
        device[j].start_stream()
    device[master_camera].nodemap.get_node('TriggerSoftware').execute()
    think_lucid_save_image(device)
    for j in range(len(device)):
        device[j].stop_stream()


def destroy_camera():
    system.destroy_device()
    print('Destroyed all created devices')


if __name__ == "__main__":
    camera_six = think_lucid_init()
    while True:
        str = input("Please input Y/N(Y is start trigger, N is stop camera and quit): ")
        if str == "Y":
            start_camera_capture(camera_six)
        elif str == "N":
            destroy_camera()
            break
