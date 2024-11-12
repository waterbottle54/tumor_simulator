from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QPen, QColor, QMouseEvent, QWheelEvent, QKeyEvent, QPainterPath, QPainter, QTransform
from PyQt5.QtCore import QPoint, Qt, QPointF
from data.Camera import *
from data.Layer import *

class LayerWidget(QGraphicsView):
    """
    입력받은 Layer(영상 단면)의 이미지와 종양 경계를 화면에 표시한다.

    Attributes:
        layer: 위젯에 표시할 Layer 객체
        camera: 유저가 layer에서 관측가능한 사각영역을 관리하는 객체
        right_mouse: 우측 버튼 drag 진행 여부
        left_mouse: 좌측 버튼 drag 진행 여부
        on_drag: 마우스 drag 감지 시 호출되는 콜백
        on_hover: 마우스 hovering 감지 시 호출되는 콜백
        on_wheel: 마우스 휠 회전 감지 시 호출되는 콜백
        on_key_press: 키 눌림 감지 시 콜백

    Methods:
        set_layer: 위젯에 그려질 레이어(layer)를 설정하고 화면을 업데이트한다.
        mousePressEvent: 마우스 버튼이 눌려지면 드래그 인식을 시작한다.
        mouseReleaseEvent: 마우스 버튼이 release되면 드래그 인식을 종료한다.
        mouseMoveEvent: 마우스 움직임이 감지되면 hovering, dragging에 따라 다른 처리를 한다.
        wheelEvent: 마우스 휠 회전이 감지되면 zoom을 조정한다.
        keyPressEvent: 키 눌림이 감지되면 외부 리스너의 콜백을 호출한다.
        drawShapes: 설정된 layer의 영상 이미지와 종양 경계를 scene 위에 그린다.
        create_viewport_pixmap: 새로운 pixmap 위에 현재 layer의 영상 이미지를 그려서 리턴한다.
        viewport_to_image: viewport 좌표에 대응되는 layer의 image 좌표를 구한다.
        image_to_viewport: layer의 image 좌표에 대응되는 viewport 좌표를 구한다.
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self):
        super().__init__()

        self.layer = None
        self.camera = Camera(0, 0, self.width(), self.height())
        self.right_mouse: QPoint = None
        self.left_mouse: QPoint = None
        self.on_drag = None
        self.on_hover = None
        self.on_wheel = None
        self.on_key_press = None

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.pen = QPen(QColor(0, 255, 0, 128))
        self.pen.setWidth(10)

        self.drawShapes()

    def set_layer(self, layer: Layer):
        """
        위젯에 그려질 레이어(layer)를 설정하고 화면을 업데이트한다.

        Args:
            layer (Layer): 위젯에 그려질 레이어(Layer) 객체
        """
        self.layer = None
        self.pixmap = None
        if layer is not None:
            pixmap = layer.pixmap
            if self.layer is None or self.layer.series != layer.series:
                # 카메라의 zoom 배율을 layer의 이미지 크기에 맞춘다
                self.camera.fit_to(pixmap.width(), pixmap.height(), float(self.width()) / self.height())
            self.layer = layer
        self.drawShapes()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        마우스 버튼이 눌려지면 드래그 인식을 시작한다.

        Args:
            event (QMouseEvent): 마우스 상태를 담은 이벤트
        """
        if event.button() == Qt.MouseButton.RightButton:
            self.right_mouse = event.pos()
        elif event.button() == Qt.MouseButton.LeftButton and self.layer is not None:
            self.left_mouse = event.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        마우스 버튼이 release되면 드래그 인식을 종료한다.

        Args:
            event (QMouseEvent): 마우스 상태를 담은 이벤트
        """
        if event.button() == Qt.MouseButton.RightButton:
            self.right_mouse = None
        elif event.button() == Qt.MouseButton.LeftButton:
            self.left_mouse = None
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        1. 마우스 움직임이 감지되면 마우스 위치에 대응되는 실제 공간 좌표를 계산하고 관련 콜백을 호출한다. (3D 좌표 표시, etc)
        2. 우측 버튼 드래그가 감지되면 그에 따라 카메라(시점)을 움직인다.
        3. 좌측 버튼 드래그가 감지되면 관련 콜백을 호출한다. (종양 경계 마킹, etc)

        Args:
            event (QMouseEvent): 마우스 상태를 담은 이벤트
        """
        if self.layer is not None:
            x, y = event.pos().x(), event.pos().y()
            pos_image = self.viewport_to_image([x, y])
            pos_world = self.layer.image_to_world(pos_image)
            self.on_hover(pos_world)

        if self.right_mouse is not None:
            delta = event.pos() - self.right_mouse
            dx, dy = float(delta.x()), float(delta.y())
            self.camera.move_by(-dx / self.width(), -dy / self.height())
            self.right_mouse = event.pos()
            self.drawShapes()
        elif self.left_mouse is not None:
            if self.on_drag is not None and self.layer is not None:
                x, y = event.pos().x(), event.pos().y()
                pos_image = self.viewport_to_image([x, y])
                pos_world = self.layer.image_to_world(pos_image)
                self.on_drag(pos_world)
            self.left_mouse = event.pos()

        super().mouseMoveEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        마우스 휠 회전이 감지되면 zoom을 조정한다.

        Args:
            event (QWheelEvent): 휠 변화 이벤트 객체
        """
        angle_delta = event.angleDelta().y()
        if event.modifiers() == Qt.ControlModifier:
            self.camera.zoom_by(1.2 if angle_delta > 0 else 0.8)
            self.drawShapes()
        elif self.on_wheel is not None:
            self.on_wheel(angle_delta > 0)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        키 눌림이 감지되면 외부 리스너의 콜백을 호출한다. (시점 변환 등에 사용)

        Args:
            event (QKeyEvent): 키 눌림 이벤트 객체
        """
        if self.on_key_press is not None:
            self.on_key_press(event)
         
    def drawShapes(self):
        """
        설정된 layer의 영상 이미지와 종양 경계를 scene 위에 그린다.
        """
        self.scene.clear()

        # layer가 그려진 pixmap을 생성하고 scene에 연결한다
        viewport_pixmap = self.create_viewport_pixmap()
        if viewport_pixmap is not None:
            self.scene.addPixmap(viewport_pixmap)
    
        # 종양의 경계가 존재하면, 경계를 pixmap에 그린다 (path)
        if self.layer is not None and len(self.layer.path) > 1:
            path = QPainterPath()
            for i, pos_world in enumerate(self.layer.path):
                pos_image = self.layer.world_to_image(pos_world)
                pos_viewport = self.image_to_viewport(pos_image)
                if i == 0:
                    path.moveTo(QPointF(*pos_viewport))
                else:
                    path.lineTo(QPointF(*pos_viewport))
            self.pen.setWidth(5 if self.camera.w() > self.width()/2 else 10)
            self.scene.addPath(path, self.pen)

    def create_viewport_pixmap(self) -> QPixmap:
        """
        새로운 pixmap 위에 현재 layer의 영상 이미지를 그려서 리턴한다.

        Returns:
            QPixmap: layer의 영상 이미지가 그려진 pixmap
        """
        # 검정색 pixmap 을 생성한다
        pixmap = QPixmap(self.width(), self.height())
        pixmap.fill(QColor.fromRgb(0, 0, 0, 255))
        if self.layer is None:
            return pixmap
        # 설정된 layer의 이미지를 그린다
        painter = QPainter(pixmap)
        t = self.camera.get_transform(self.width(), self.height())
        painter.setTransform(QTransform(*t))    # zoom 배율, focus 위치 적용
        painter.drawPixmap(0, 0, self.layer.pixmap)
        painter.end()
        return pixmap

    def viewport_to_image(self, pos_viewport):
        """
        viewport 좌표에 대응되는 layer의 image 좌표를 구한다.
        zoom in/out, focus 이동을 하지 않은 상태라면 두 좌표는 일치한다.

        Args:
            pos_viewport (list[float]): 변환하려는 viewport 좌표. x=[0], y=[1]

        Returns:
            list[float]: 변환된 image 좌표
        """
        t = QTransform(*self.camera.get_transform(self.width(), self.height()))
        inverted = t.inverted()[0]  # image*T = viewport 이므로, image = viewport*(T_inv)
        return list(inverted.map(*tuple(pos_viewport)))
    
    def image_to_viewport(self, pos_image):
        """
        layer의 image 좌표에 대응되는 viewport 좌표를 구한다.
        zoom in/out, focus 이동을 하지 않은 상태라면 두 좌표는 일치한다.

        Args:
            pos_image (list[float]): 변환하려는 image 좌표. x=[0], y=[1]

        Returns:
            list[float]: 변환된 viewport 좌표
        """
        t = QTransform(*self.camera.get_transform(self.width(), self.height())) # image*T = viewport
        return list(t.map(*tuple(pos_image)))