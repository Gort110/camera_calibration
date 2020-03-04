# -*-coding:utf-8-*-
import cv2 as cv

dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_100)

charucoboard = cv.aruco.CharucoBoard_create(12, 9, 0.03, 0.0225, dictionary)

img = charucoboard.draw((1440, 1080))
# cv.imshow("img", img)
cv.imwrite("charucoboard.jpg", img)
cv.waitKey(5000)
