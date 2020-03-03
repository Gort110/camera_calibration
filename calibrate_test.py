# -*-coding:utf-8-*-

import numpy as np
import cv2 as cv
import glob
import Trigger_Hardware
import os


def clean_exit_image():
    """
    cleaning the exist image, including .png, .jpg.
    """
    image_png_exist = glob.glob("*.png")
    for img_png in image_png_exist:
        os.remove(img_png)

    image_jpg_exist = glob.glob("*.jpg")
    for img_jpg in image_jpg_exist:
        os.remove(img_jpg)


def calibration_camera(images, mgrid_board, criteria, squaresize):
    """
    calibration camera
    Parameters: images
                mgrid_board
                criteria
                impoints
                objpoints
    return: mnt
            dist
            meanerror
    """
    objp = np.zeros((mgrid_board[0] * mgrid_board[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:mgrid_board[0], 0:mgrid_board[1]].T.reshape(-1, 2) * squaresize
    objpoints = []
    imgpoints = []
    image_height = 0
    image_width = 0
    for fname in images:
        img = cv.imread(fname)
        image_height, image_width = img.shape[:2]
        gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)#RGB to GRAY
        ret, corners = cv.findChessboardCorners(gray, mgrid_board, None)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            cv.drawChessboardCorners(img, mgrid_board, corners2, ret)
            cv.imshow("img", img)
            cv.imwrite(f"./{fname.strip('.png')}_calibrate.jpg", img)
            # cv.waitKey(500)
    cv.destroyAllWindows()
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    # Undistortion
    #newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (image_width, image_height), 1, (image_width, image_height))
    # dst = cv.undistort(img, mtx, dist, None, newcameramtx)
    # x, y, w, h = roi
    # dst = dst[y:y+h, x:x+w]
    # cv.imwrite(f"./{fname.strip('.png')}_calibresult.jpg", dst)
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error
    mean_error = mean_error/len(objpoints)
    return mtx, dist, mean_error


criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
mgrid_board = (11, 8)
squaresize = 30 # girdm size 30mm*30mm

clean_exit_image()
# Get camera image, at least 10pcs
camera_lucid = []
camera_serialnumber = {}
calibration_image_count = 10  # image pcs
camera_lucid = Trigger_Hardware.think_lucid_init()
for j in range(len(camera_lucid)):
    camera_serialnumber[j] = camera_lucid[j].nodemap.get_node("DeviceSerialNumber").value
print(f"The calibration need to capture {calibration_image_count}pcs image.")
for pcs in range(1, calibration_image_count + 1):
    str = input(f"Starting capture the {pcs}th image(Y/N): ")
    if str == "Y":
        Trigger_Hardware.start_camera_capture(camera_lucid)
    else:
        continue
Trigger_Hardware.destroy_camera()


for i in range(len(camera_serialnumber)):
    images = glob.glob(f"{camera_serialnumber[i]}*.png")
    mnt, dist, mean_error =calibration_camera(images, mgrid_board, criteria, squaresize)
    print(f"----------------------{camera_serialnumber[i]} calibration is Done-----------------------------")
    print(f"mnt is: {mnt}\n dist is: {dist}\n mean_error is: {mean_error}pixel")
    print("--------------------------------------------------------------------------------")
