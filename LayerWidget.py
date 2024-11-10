from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QPen, QColor, QMouseEvent, QWheelEvent, QKeyEvent, QPainterPath, QPainter, QTransform
from PyQt5.QtCore import QPoint, Qt, QPointF
from Camera import *
from Layer import *

class LayerWidget(QGraphicsView):

    layer: Layer = None

    camera: Camera
    right_mouse: QPoint = None
    left_mouse: QPoint = None

    scene: QGraphicsScene 
    pen: QPen

    on_drag = None
    on_hover = None
    on_wheel = None
    on_key_press = None
   
    def __init__(self):
        super().__init__()
        self.camera = Camera(0, 0, self.width(), self.height())

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.pen = QPen(QColor(0, 255, 0, 128))
        self.pen.setWidth(10)

        self.drawShapes()

    def set_layer(self, layer: Layer):
        self.layer = None
        self.pixmap = None
        if layer is not None:
            pixmap = layer.pixmap
            if self.layer is None or self.layer.series != layer.series:
                self.camera.fit_to(pixmap.width(), pixmap.height(), float(self.width()) / self.height())
            self.layer = layer
        self.drawShapes()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.right_mouse = event.pos()
        elif event.button() == Qt.MouseButton.LeftButton and self.layer is not None:
            self.left_mouse = event.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.right_mouse = None
        elif event.button() == Qt.MouseButton.LeftButton:
            self.left_mouse = None
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
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
        angle_delta = event.angleDelta().y()
        if event.modifiers() == Qt.ControlModifier:
            self.camera.zoom_by(1.2 if angle_delta > 0 else 0.8)
            self.drawShapes()
        elif self.on_wheel is not None:
            self.on_wheel(angle_delta > 0)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self.on_key_press is not None:
            self.on_key_press(event)
         
    def drawShapes(self):
        self.scene.clear()

        viewport_pixmap = self.get_viewport_pixmap()
        if viewport_pixmap is not None:
            self.scene.addPixmap(viewport_pixmap)
    
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

    def get_viewport_pixmap(self) -> QPixmap:
        pixmap = QPixmap(self.width(), self.height())
        pixmap.fill(QColor.fromRgb(0, 0, 0, 255))
        if self.layer is None:
            return pixmap
        painter = QPainter(pixmap)
        t = self.camera.get_transform(self.width(), self.height())
        painter.setTransform(QTransform(*t))
        painter.drawPixmap(0, 0, self.layer.pixmap)
        painter.end()
        return pixmap

    def viewport_to_image(self, pos_viewport):
        t = QTransform(*self.camera.get_transform(self.width(), self.height()))
        inverted = t.inverted()[0]
        return list(inverted.map(*tuple(pos_viewport)))
    
    def image_to_viewport(self, pos_image):
        t = QTransform(*self.camera.get_transform(self.width(), self.height()))
        return list(t.map(*tuple(pos_image)))