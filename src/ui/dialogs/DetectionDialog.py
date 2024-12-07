from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QDialog, QWidget, QSlider, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QTransform, QPixmap, QColor
from Strings import about_text
from Strings import url_youtube
from Strings import get_image_path, url_github
from src.utils.PickableQPixmap import PickableQPixmap
from src.data.Camera import Camera
from src.data.common.LiveData import map3, MutableLiveData
from src.utils.OpenCVUtil import detectPixmapContour, ContourDetectionResult

class DetectionDialog(QDialog):
    """
    단면 영상에서 종양의 경계를 자동 지정하는 대화상자
    A dialog that automatically sets the boundary of tumor within a layter image
    
    유저가 조정 가능한 detection 파라미터들
    - binarization 시의 threshhold 값 
    - countour의 minumum area 값 (noise filtering)
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pixmap_layer = MutableLiveData(None)
        self.threshold = MutableLiveData(80)
        self.min_area = MutableLiveData(50)

        # 상기의 layer 이미지, threshold, min_area증 하나라도 변경되면 contour 결과를 갱신한다
        self.contour_result = map3(
            self.pixmap_layer, self.threshold, self.min_area,
            lambda pixmap, threshold, min_area: 
                detectPixmapContour(pixmap, threshold, min_area)
                if pixmap is not None else None
        )

        self.setWindowTitle("Auto Detection")
        self.setStyleSheet("background-color: white;")

        layout_dialog = QVBoxLayout()
        layout_dialog.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout_dialog)

        # GraphicsView for layer image
        self.canvas_layer = QGraphicsView()
        self.canvas_layer.setFixedSize(600, 600)
        self.canvas_layer.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.canvas_layer.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout_dialog.addWidget(self.canvas_layer)

        self.scene = QGraphicsScene()
        self.canvas_layer.setScene(self.scene)

        layout_dialog.addSpacing(16)

        # Threshold label, slide
        self.label_threshold = QLabel()
        self.label_threshold.setText('Threshold')
        layout_dialog.addWidget(self.label_threshold)

        self.slider_threshold = QSlider()
        self.slider_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_threshold.setRange(0, 255)
        self.slider_threshold.setValue(self.threshold.value)
        self.slider_threshold.sliderMoved.connect(lambda val: self.threshold.set_value(val))
        layout_dialog.addWidget(self.slider_threshold)

        layout_dialog.addSpacing(16)

        # Minimum area label, slide
        self.label_min_area = QLabel()
        self.label_min_area.setText('Min Area')
        layout_dialog.addWidget(self.label_min_area)

        self.slider_min_area = QSlider()
        self.slider_min_area = QSlider(Qt.Orientation.Horizontal)
        self.slider_min_area.setRange(0, 100)
        self.slider_min_area.setValue(self.min_area.value)
        self.slider_min_area.sliderMoved.connect(lambda val: self.min_area.set_value(val))
        layout_dialog.addWidget(self.slider_min_area)

        layout_dialog.addSpacing(16)

        # Buttons
        layout_button = QHBoxLayout()
        layout_dialog.addLayout(layout_button)
        
        button_cancel = QPushButton('Cancel')
        layout_button.addWidget(button_cancel, stretch=1)

        button_apply = QPushButton('Apply')
        layout_button.addWidget(button_apply, stretch=1)

        # Camera setting
        self.camera = Camera(0, 0, self.canvas_layer.width(), self.canvas_layer.height())
        
        # contour 결과 데이터(image, etc)를 UI에 업데이트
        self.contour_result.observe(lambda result: self.updateUI(result))

    def get_detected_contours(self):
        return self.contour_result.value

    def set_layer_pixmap(self, pixmap_new: PickableQPixmap):
        if pixmap_new is not None:
            # 카메라의 zoom 배율을 layer의 이미지 크기에 맞춘다
            self.camera.fit_to(pixmap_new.width(), 
                               pixmap_new.height(), 
                               float(self.canvas_layer.width()) / self.canvas_layer.height())
            self.pixmap_layer.set_value(pixmap_new)

    def updateUI(self, result: ContourDetectionResult):
        """
        설정된 layer의 영상 이미지와 종양 경계를 scene 위에 그린다.
        """
        self.scene.clear()

        if result is None:
            return

        # layer가 그려진 pixmap을 생성하고 scene에 연결한다
        viewport_pixmap = self.create_viewport_pixmap(result.pixmap, self.canvas_layer)
        if viewport_pixmap is not None:
            self.scene.addPixmap(viewport_pixmap)

    def create_viewport_pixmap(self, pixmap_src: QPixmap, viewport: QWidget) -> QPixmap:
        """
        새로운 pixmap 위에 현재 layer의 영상 이미지를 그려서 리턴한다.

        Returns:
            QPixmap: layer의 영상 이미지가 그려진 pixmap
        """
        # 검정색 pixmap 을 생성한다
        pixmap = QPixmap(viewport.width(), viewport.height())
        pixmap.fill(QColor.fromRgb(0, 0, 0, 255))
        if pixmap_src is None:
            return pixmap
        # 설정된 layer의 이미지를 그린다
        painter = QPainter(pixmap)
        t = self.camera.get_transform(viewport.width(), viewport.height())
        painter.setTransform(QTransform(*t))    # zoom 배율, focus 위치 적용
        painter.drawPixmap(0, 0, pixmap_src)
        painter.end()
        return pixmap