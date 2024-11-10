from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from ViewModel import *
from PyQt5.QtCore import QSize, QModelIndex
from LayerWidget import *
from Layer import *

class LayersFragment(QWidget):
    
    view_model: ViewModel
    layout = QVBoxLayout
    layer_widget: LayerWidget
    series_list_view: QListWidget

    def __init__(self, view_model):
        super().__init__()
        
        self.view_model = view_model
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layer_widget = LayerWidget()
        self.layer_widget.setFixedSize(600, 600)
        self.layer_widget.on_drag = self.on_layer_drag
        self.layer_widget.on_hover = self.on_layer_hover
        self.layer_widget.on_wheel = self.on_layer_wheel
        self.layer_widget.on_key_press = self.on_key_press
        self.layout.addWidget(self.layer_widget)

        self.data_widget = QWidget(self.layer_widget)
        self.data_widget.setGeometry(self.layer_widget.width() - 150 - 10, 10, self.layer_widget.width() - 10, 10 + 70)
        self.data_widget.setContentsMargins(4, 4, 2, 4)
        self.data_widget.setFixedWidth(150)
        self.data_widget.setStyleSheet("background-color: rgba(255, 255, 255, 32); border-radius:10px;")
        data_layout = QVBoxLayout(self.data_widget)
        data_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.series_label = QLabel()
        self.series_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgb(200, 200, 200);")
        data_layout.addWidget(self.series_label)

        self.volume_label = QLabel()
        self.volume_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgb(200, 200, 200);")
        data_layout.addWidget(self.volume_label)

        self.area_label = QLabel()
        self.area_label.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgb(200, 200, 200);")
        data_layout.addWidget(self.area_label)

        self.layer_widget.show()
        self.layout.addSpacing(12)        

        self.series_list_view = QListView()
        self.series_list_view.setFixedSize(600, 125)
        self.series_list_view.setIconSize(QSize(100, 100))
        self.series_list_view.setFlow(QListView.Flow.LeftToRight)
        self.series_list_view.clicked.connect(self.on_series_click)
        self.layout.addWidget(self.series_list_view)

        self.view_model.layer.observe(self.layer_widget.set_layer)
        self.view_model.layer_map.observe(self.update_series_list_view)
        self.view_model.series_description.observe(self.update_series_description)
        self.view_model.area.observe(lambda area: self.area_label.setText(f'Area: {(area/100):.2f}㎤'))
        self.view_model.volume.observe(lambda volume: self.volume_label.setText(f'Volume: {(volume/1000):.2f}㎠'))

    def on_key_press(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key.Key_PageUp:
            self.view_model.on_layer_scroll_by(5)
        elif key == Qt.Key.Key_PageDown:
            self.view_model.on_layer_scroll_by(-5)
        elif key == Qt.Key.Key_Home:
            self.view_model.on_layer_scroll_to_end()
        elif key == Qt.Key.Key_End:
            self.view_model.on_layer_scroll_to(0)

        super().keyPressEvent(event)

    def on_series_click(self, model_index: QModelIndex):
        self.view_model.on_series_change(model_index.row())

    def on_layer_drag(self, pos_world):
        self.view_model.on_layer_drag(pos_world)

    def on_layer_hover(self, pos_world):
        self.view_model.on_layer_hover(pos_world)

    def on_layer_wheel(self, up_down):
        self.view_model.on_layer_scroll_by(1 if up_down == True else -1)

    def update_series_list_view(self, layer_map):
        model = QStandardItemModel()
        for series, layer_list in layer_map.items():
            layer_list: list[Layer]
            if len(layer_list) > 0:
                pixmap = layer_list[0].pixmap
                if pixmap is None:
                    pixmap = QPixmap(100, 100)
                    pixmap.fill(QColor.fromRgb(0, 0, 0, 255))
                scaled = pixmap.scaled(100, 100, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
                icon = QIcon(scaled)
                item = QStandardItem()
                item.setIcon(icon)
                item.setToolTip(series)
                model.appendRow(item)
        self.series_list_view.setModel(model)

    def update_series_description(self, description):
        if description is not None:
            series, count, position = description
            if len(series) >= 12:
                series = series[:11] + ".."
            self.series_label.setText(f'{series} ({1+position}/{count})')
        else:
            self.series_label.setText('DICOM IMAGES (0/0)')
