from cv2 import cv2
import numpy as np
from rotate_img import ROTATE_API
import argparse

rotapi = ROTATE_API()
file_path_name = 'img/rotate_img.jpg'

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

def setLabel(image, str, contour):
    (text_width, text_height), baseline = cv2.getTextSize(str, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
    x, y, width, height = cv2.boundingRect(contour)
    pt_x = x+int((width-text_width)/2)
    pt_y = y+int((height + text_height)/2)
    cv2.rectangle(image, (pt_x, pt_y+baseline), (pt_x+text_width, pt_y-text_height), (200,200,200), cv2.FILLED)
    cv2.putText(image, str, (pt_x, pt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 1, 8)

def sort_contours(cnts, method="left-to-right"):
    reverse = False
    i = 0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b: b[1][i], reverse=reverse))
    return (cnts, boundingBoxes)

def find_contours(img_final_bin, location_mode):
    # Find contours for image, which will detect all the boxes!!img_bin
    if location_mode:
        contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    (contours, boundingBoxes) = sort_contours(contours, method="top-to-bottom")
    return contours, boundingBoxes

def edit_img(kernel_length, v_weith, v_length, h_weith, h_length, v_pixel, h_pixel, img_bin):
    # 선을 찾아낼 기준 조건들을 설정한다.
    #kernel_length = np.array(img_bin).shape[1] // 40  # 선 길이를 뜻
    #kernel_length = 20 # 선 길이 20 이상만 선으로 인식한다.
    #print(len(cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))))
    #print(len(cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))))
    #print('dddd', kernel_length)
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))  # 세로 선 두께
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))  # 가로 선 두께
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (v_pixel, h_pixel))  # 선 그릴때 픽셀 크기를 지정(세로, 가로)

    # 세로선을 찾는다.
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=v_weith)  # 가로 인식할 선의 굵기 조정
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=v_length)  # 가로 인식된 선의 길이를 조정

    #view_img(verticle_lines_img)

    # 가로선을 찾는다.
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=h_weith)  # 세로 인식할 선의 굵기 조정
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=h_length)  # 세로 인식된 선의 길이를 조정
    #view_img(horizontal_lines_img)

    # 찾은 선을 새 이미지에 그린다.
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    #img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 3.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=1)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    #img_final_bin111 = cv2.pyrDown(img_final_bin)
    #img_final_bin111 = cv2.pyrDown(img_final_bin111)
    #cv2.imshow('ori_img11', img_final_bin111)
    #cv2.waitKey(0)
    return img_final_bin

def convert_image(img):
    kernel = np.ones((3, 3), np.uint8)
    denoised = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    erosion = cv2.erode(img, kernel, iterations=1)

    (thresh, img_bin) = cv2.threshold(erosion, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding the image
    img_bin = 255 - img_bin  # Invert the image
    #again_img_bin = img_bin
    return img, img_bin

if __name__ == '__main__':
    # 이미지 2배 확대 하고 저장한다.
    img_path_name = "../img/cigars/20191024_190659.jpg"
    #img = cv2.imread(img_path_name)
    #height, width, channel = img.shape
    #dst = cv2.pyrUp(img, dstsize=(width * 2, height * 2), borderType=cv2.BORDER_DEFAULT)
    #cv2.imwrite("../img/cigars/result.jpg", dst)
    #cv2.imshow('img', img)
    #cv2.imshow('dst', dst)

    # 이미지 읽어서 누워있는거 세운다
    img = cv2.imread(img_path_name, 0)
    #cv2.imshow('dst', img)
    #cv2.waitKey(0)
    img, img_bin = convert_image(img)
    img_final_bin = edit_img(80, 1, 1, 1, 1, 1, 1, img_bin)
    contours, boundingBoxes = find_contours(img_final_bin, False)
    no1x, no1y, no1w, no1h, no2x, no2y, no2w, no2h = rotapi.check_angle(contours)
    if no2w > no2h:
        #file_path_name = rotapi.rotate_90(cv2.resize(cv2.imread(img_path_name), (weigh, height)))
        #file_path_name = rotapi.rotate_90(test_img)
        #file_path_name = rotapi.rotate_90(cv2.pyrDown(cv2.imread(img_path_name)))
        file_path_name = rotapi.rotate_90(cv2.imread(img_path_name))
        img = cv2.imread(file_path_name, 0)

    # 이미지에서 테이블만 잘라내 따로 저장한다.
    img, img_bin = convert_image(img)
    img_final_bin = edit_img(80, 1, 1, 1, 1, 1, 1, img_bin)
    contours, boundingBoxes = find_contours(img_final_bin, False)
    no1x, no1y, no1w, no1h, no2x, no2y, no2w, no2h = rotapi.check_angle(contours)
    piece_img = img[no2y:no2y + no2h, no2x:no2x + no2w]
    cv2.imwrite(file_path_name, piece_img)
    cv2.destroyAllWindows()

    # 이미지 새로 읽어서 테이블 수평 맞춰 주고 저장한다.
    img = cv2.imread(file_path_name)
    piece_img = rotapi.rotate_auto(img)
    cv2.imwrite(file_path_name, piece_img)

    # 저장한 이미지를 새로 읽는데 너무 커서 사이즈를 축소 시킨다. 웹에서 사용자 입력받는다면 필요 없다.
    piece_img = cv2.imread(file_path_name, 0)
    img = cv2.pyrDown(piece_img)
    img = cv2.pyrDown(img)
    #img = piece_img
    origin_img = img

    # 이미지 재처리 해서 화면에 띄운다.
    img, img_bin = convert_image(img)
    img_final_bin = edit_img(80, 1, 1, 1, 1, 1, 1, img_bin)
    dst = cv2.addWeighted(img, 0.4, img_final_bin, 0.6, 0)

    # 재처리된 이미지를 디비와 비교하여 같거나 비슷한 템플릿이 있는지 찾아 본다.
    # 찾아서 있다면 바로 아래 연산 건너뛴다.

    # 위 연산 결과가 없으면 이미지에 사용자 입력 받아서 쓴다.
    drawing = False
    mode = True
    ix, iy = -1, -1
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_line)
    while True:
        cv2.imshow('image', dst)
        if cv2.waitKey(0) & 0xFF == 27:
            break

    # 이미지에서 사각형 찾이 라벨링 하고 최종 결과 출력 한다.
    img, img_bin = convert_image(dst)
    img_final_bin = edit_img(80, 1, 1, 1, 1, 1, 1, img_bin)
    contours, boundingBoxes = find_contours(img_final_bin, True)
    inx = 1
    for var in contours:
        x, y, w, h = cv2.boundingRect(var)
        if h > 8 and w > 10:
            new_img = origin_img[y:y + h, x:x + w]
            img_final_result = cv2.drawContours(origin_img, var, -1, (0, 255, 0), 2)
            setLabel(origin_img, str(inx), var)
            cv2.imshow('img_final_result', origin_img)
            inx += 1
    cv2.waitKey(0)

    # 이미지 데이터화 하여 디비에 저장한다.



