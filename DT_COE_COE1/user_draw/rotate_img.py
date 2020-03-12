from cv2 import cv2
import numpy as np
import argparse

class ROTATE_API:
    def check_angle(self, contours):
        no1x, no1y, no1w, no1h, no2x, no2y, no2w, no2h = 0, 0, 0, 0, 0, 0, 0, 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if no1w < w:
                no1w, no1x, no1y = w, x, y
            if no1h < h:
                no1h, no1x, no1y = w, x, h
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if no1w > w and no2w < w:
                no2w, no2x, no2y = w, x, y
            if no1h > w and no2h < h:
                no2h, no2x, no2y = h, x, y
        return no1x, no1y, no1w, no1h, no2x, no2y, no2w, no2h

    def rotate_90(self, image):
        #cv2.resize(image, (800, 800))
        #cv2.imshow('dddimage', image)
        #cv2.waitKey(0)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        angle = 90

        (h, w) = image.shape[:2]
        #print(h, w)
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        #cv2.resize(rotated, (800, 1000))
        #cv2.imshow('rotated', rotated)
        #cv2.waitKey(0)
        file_path_name = 'img/rotate_img.jpg'
        cv2.imwrite(file_path_name, rotated)
        return file_path_name

    def rotate_auto(self, image):
        #image = cv2.imread(args["image"])
        #image = cv2.resize(image, (800, 1000))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)

        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated