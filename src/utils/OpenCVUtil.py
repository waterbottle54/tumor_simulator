"""
이 모듈은 어플리케이션에서 활용되는 OpenCV의 기능 및 code snippet을 메소드 형태로 제공합니다. 
"""

from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np


class ContourDetectionResult:
    """
    이 클래스는 Contour detection 결과를 저장하는 데이터 클래스입니다.
    This class represents data structure that Contour detection returns
    """
    def __init__(self, contours, hierarchy, pixmap):
        self.contours = contours
        self.hierarchy = hierarchy
        self.pixmap = pixmap

def detectPixmapContour(pixmap_src: QPixmap, threshold: int, min_area: int) -> ContourDetectionResult:
    """
    주어진 pixmap에 contour detection을 적용한 결과(ContourDetectionResult)를 리턴합니다.

    Args:
        pixmap_src (QPixmap): contour detection을 적용할 pixmap
        threshold (int): binarization threshold 값. 0~255
        min_area (int): 이 값보다 면적이 작은 contour는 noise로 간주하여 제거한다

    Returns:
        ContourDetectionResult: detection 결과를 담은 데이터 구조체
    """
    # 원본 pixmap을 전처리하여 threshold를 기준으로 binary 이미지화 한다
    image = pixmapToCv2Image(pixmap_src)
    grayed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(grayed, (11, 11), 0)
    _, binary_image = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)

    # binary 이미지로부터 contours 를 계산한다
    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # min_area보다 면적이 작은 noise contours를 걸러낸다
    contours_filtered = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area:
            contours_filtered.append(contour)
            cv2.drawContours(image, [contour], -1, (0, 255, 0), 1)
    
    return ContourDetectionResult(contours, hierarchy, cv2ImageToPixmap(image))

def pixmapToCv2Image(pixmap):
    # pixmap을 cv2 이미지로 변환한다.
    qimage = pixmap.toImage()
    width = qimage.width()
    height = qimage.height()
    channels = 4  # 4채널 RGBA 포맷
    
    image_data = qimage.bits().asarray(height * width * channels)
    cv_image = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width, channels))
    
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGBA2BGR)
    return cv_image

def cv2ImageToPixmap(cv_image):
    # cv2 이미지를 pixmap으로 변환한다.
    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb_image.shape
    qt_image = QImage(rgb_image.data, width, height, channels * width, QImage.Format_RGB888)
    return QPixmap.fromImage(qt_image)