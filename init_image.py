# -*-coding:utf-8-*-

import glob
import os


def clean_exit_image():
    """
    cleaning the exist image files, including .png, .jpg.
    """
    image_png_exist = glob.glob("*.png")
    for img_png in image_png_exist:
        os.remove(img_png)

    image_jpg_exist = glob.glob("*.jpg")
    for img_jpg in image_jpg_exist:
        os.remove(img_jpg)


def clean_exit_npz():
    """
    cleaning the exist parameter files, including .npz.
    """
    npz_exist = glob.glob("*.npz")
    for npz_file in npz_exist:
        os.remove(npz_file)
