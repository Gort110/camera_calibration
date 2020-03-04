# -*-coding:utf-8-*-
import cv2 as cv
import numpy as np
import glob
import Trigger_Hardware
import init_image


def calibartion_camera_ChArUco_board(images, mgrid_board, criteria, squaresize, dictionary, charucoboard):
    allcorners = []
    allids = []
    objp = np.zeros((mgrid_board[0] * mgrid_board[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:mgrid_board[0], 0:mgrid_board[1]].T.reshape(-1, 2) * squaresize
    objpoints = []
    for fname in images:
        img = cv.imread(fname)
        gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        corners0, ids0, rejectedImgPoints0 = cv.aruco.detectMarkers(gray, dictionary)
        corners, ids, rejectedImgPoints, recover = cv.aruco.refineDetectedMarkers(
            gray, charucoboard, corners0, ids0, rejectedImgPoints0)
        if len(corners) > 0:
            ret_inter, charucorners, charucoids = cv.aruco.interpolateCornersCharuco(corners, ids, gray, charucoboard)
            corners2 = cv.cornerSubPix(gray, charucorners, (11, 11), (-1, -1), criteria)
            if len(charucoids) > 0:
                allcorners.append(corners2)
                objpoints.append(objp)
                allids.append(charucoids)
            cv.aruco.drawDetectedCornersCharuco(img, corners2, charucoids, cornerColor=(0, 0, 255))
        cv.imshow("img", img)
        # cv.waitKey(500)
        cv.imwrite(f"./{fname.strip('.png')}_charuco_calibration.jpg", img)
    cv.destroyAllWindows()
    ret, mtx, dist, rvecs, tvecs = cv.aruco.calibrateCameraCharuco(
        allcorners, allids, charucoboard, gray.shape[::-1], None, None)
    # mean_error = 0
    # for i in range(len(objpoints)):
    #     imgpoints, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    #     error = cv.norm(allcorners[i], imgpoints, cv.NORM_L2) / len(imgpoints)
    #     mean_error += error
    # mean_error = mean_error / len(objpoints)
    return mtx, dist, ret


if __name__ == "__main__":
    mgrid_board = (11, 8)
    squaresize = 0.03
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_100)
    charucoboard = cv.aruco.CharucoBoard_create(mgrid_board[0]+1, mgrid_board[1]+1, squaresize, 0.0225, dictionary)
    init_image.clean_exit_image()
    init_image.clean_exit_npz()
    # Get camera image, at least 10pcs
    camera_serialnumber = {}
    calibration_image_count = 2  # image pcs
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
        mtx, dist, mean_error = calibartion_camera_ChArUco_board(
            images, mgrid_board, criteria, squaresize, dictionary, charucoboard)
        print(f"----------------------{camera_serialnumber[i]} calibration is Done-----------------------------")
        print(f"mtx is: {mtx}\n dist is: {dist}\n mean_error is: {mean_error}pixel")
        print("--------------------------------------------------------------------------------")
        np.savez(f"{camera_serialnumber[i]}_cablication_parameter.npz", mtx=mtx, dist=dist, mean_error=mean_error)
