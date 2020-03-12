import cv2
import numpy as np
from PIL import Image
import pytesseract

img_location = []

def setLabel(image, str, contour):
    (text_width, text_height), baseline = cv2.getTextSize(str, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
    x, y, width, height = cv2.boundingRect(contour)
    pt_x = x+int((width-text_width)/2)
    pt_y = y+int((height + text_height)/2)
    cv2.rectangle(image, (pt_x, pt_y+baseline), (pt_x+text_width, pt_y-text_height), (200,200,200), cv2.FILLED)
    cv2.putText(image, str, (pt_x, pt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 1, 8)

def convert_image(img):
    kernel = np.ones((3, 3), np.uint8)
    denoised = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    erosion = cv2.erode(img, kernel, iterations=1)

    (thresh, img_bin) = cv2.threshold(erosion, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding the image
    img_bin = 255 - img_bin  # Invert the image
    #again_img_bin = img_bin
    return img, img_bin

def find_contours(img_final_bin, location_mode):
    # Find contours for image, which will detect all the boxes!!img_bin
    if location_mode:
        contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    (contours, boundingBoxes) = sort_contours(contours, method="top-to-bottom")
    return contours

def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0
    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    # handle if we are sorting against the y-coordinate rather than the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    # construct the list of bounding boxes and sort them from top to bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)

def edit_img(kernel_length, v_weith, v_length, h_weith, h_length, v_pixel, h_pixel, img_bin):
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))  # 세로 선 두께
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))  # 가로 선 두께
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (v_pixel, h_pixel))  # 선 그릴때 픽셀 크기를 지정(세로, 가로)

    # 세로선을 찾는다.
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=v_weith)  # 가로 인식할 선의 굵기 조정
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=v_length)  # 가로 인식된 선의 길이를 조정

    # 가로선을 찾는다.
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=h_weith)  # 세로 인식할 선의 굵기 조정
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=h_length)  # 세로 인식된 선의 길이를 조정

    # 찾은 선을 새 이미지에 그린다.
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    # img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 3.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=1)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return img_final_bin

def view_img(contours, img_final_edit, label):
    idx = 1
    for var in contours:
        x, y, w, h = cv2.boundingRect(var)
        if (y + h) - y > 15 and (x + w - x) > 40:
            new_img = img_final_edit[y:y + h, x:x + w]
            img_final_result = cv2.drawContours(img_final_edit, var, -1, (0, 255, 0), 2)
            if label == True:
                setLabel(img_final_result, str(idx), var)
            idx += 1
    # cv2.imshow('ori_img', origin_img)
    cv2.imshow(str(idx), img_final_result)
    cv2.waitKey(0)

def draw_line(event, x, y, flags, param):
    global ix, iy, drawing, mode
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    #elif event == cv2.EVENT_MOUSEMOVE:
    #    if drawing == True:
    #        cv2.line(img_final_bin01, (x, y), (ix, iy), (0, 255, 0), 1)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.line(dst, (x, y), (ix, iy), (0, 255, 0), 2)
    cv2.imshow('image', dst)
        #cv2.line(img, (x, y), (x, y), (255, 0, 0), 1)

def rotate(img, width, height):
    lines = np.array([[90, 90,
                       90 + (90 * np.cos(np.pi / 4)), 90 + (90 * np.sin(np.pi / 4))],
                      [90, 90,
                       90 + (90 * np.cos(np.pi / 2)), 90 + (90 * np.sin(np.pi / 2))],
                      [90, 90,
                       90 + (90 * np.cos(np.pi * 3 / 4)), 90 + (90 * np.sin(np.pi * 3 / 4))],
                      [90, 90,
                       90 + (90 * np.cos(np.pi)), 90 + (90 * np.sin(np.pi))],
                      [90, 90,
                       90 + (90 * np.cos(np.pi * 5 / 4)), 90 + (90 * np.sin(np.pi * 5 / 4))],
                      [90, 90,
                       90 + (90 * np.cos(np.pi * 6 / 4)), 90 + (90 * np.sin(np.pi * 6 / 4))],
                      [90, 90,
                       90 + (90 * np.cos(np.pi * 7 / 4)), 90 + (90 * np.sin(np.pi * 7 / 4))],
                      [90, 90,
                       90 + (90 * np.cos(np.pi * 8 / 4)), 90 + (90 * np.sin(np.pi * 8 / 4))]], dtype=np.int32)
    slope_degree = (np.arctan2(lines[:, 1] - lines[:, 3], lines[:, 0] - lines[:, 2]) * 180) / np.pi

    print(slope_degree)
    #matrix = cv2.getRotationMatrix2D((width / 2, height / 2), 90, 1)
    #img = cv2.warpAffine(img, matrix, (width, height))
    for line in lines:
        cv2.line(img, (line[0]+300, line[1]+100), (line[2]+300, line[3]+100), [255, 0, 0], 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)

if __name__ == '__main__':
    # 이미지 읽어 온다
    img = cv2.imread("../img/cigar/20191024_190605.jpg")  # Read the image
    img = cv2.resize(img, (800, 1000))
    height, width, channel = img.shape
    img = cv2.imread("../img/cigar/20191024_190605.jpg", 0)  # Read the image
    img = cv2.resize(img, (800, 1000))
    rotate(img, width, height)
    img, img_bin = convert_image(img)
    origin_img = img

    # 이미지 흑백처리, 라인 인식해서 강조, 연장하여 다시 그린다.
    img_final_bin01 = edit_img(55, 1, 1, 1, 1, 1, 1, img_bin) # 55는 라인의 최소 길이, 글자까지 인식하여 라인이된다.

    #boundringrect(140)

    dst = cv2.addWeighted(origin_img, 0.2, img_final_bin01, 0.8, 0)

    drawing = False
    mode = True
    ix, iy = -1, -1

    #img_tmp = np.zeros((800, 1000, 3), np.uint8)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_line)

    while True:
        cv2.imshow('image', dst)
        if cv2.waitKey(0) & 0xFF == 27:
            break

    img, img_bin = convert_image(dst)
    img_final_bin02 = edit_img(55, 1, 1, 1, 1, 1, 1, img_bin)
    contours02 = find_contours(img_final_bin02, True)
    view_img(contours02, origin_img, True)

    cv2.destroyAllWindows()