from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import QSize, QModelIndex
from ui.ViewModel import *
from ui.layers.LayerWidget import *
from data.Layer import *

class LayersFragment(QWidget):
    """
    view model의 현재 Layer(image & 종양 경계)를 보여주는 화면
    - series, layer를 탐색하고, layer 위에 종양의 경계를 마킹할 수 있다.
    
    Attributes:
        view_model(ViewModel): 뷰모델
        layout_top(QVBoxLayout): 최상위 레이아웃
        layer_widget(LayerWidget): layer를 그리는 위젯
        data_widget(QWidget): series_label, volume_label이 배치되는 위젯
        series_label(QLabel): 현재 탐색중인 series 제목을 표시하는 label
        volume_label(QLabel): 현재 종양의 부피를 표시하는 label
        area_label(QLabel): 현재 layer에 마킹된 종양의 단면적을 표시하는 label
        series_list_view(QListView): series들을 표시하고 선택하는 ListView

    Methods:
        on_key_press: 키 눌림이 감지되면 뷰모델에 통보한다.
        on_series_click: series 리스트에서 항목 선택이 감지되면 뷰모델에 통보한다.
        on_layer_drag: LayerWidget이 drag 감지 시 호출하는 콜백
        on_layer_hover: LayerWidget이 hovering 감지 시 호출하는 콜백
        on_layer_wheel: LayerWidget이 마우스 휠 조작 감지 시 호출하는 콜백
        update_series_list_view: series 리스트를 series_list에 업데이트한다.
        update_series_description: 시리즈 이름과 현재 layer index, layer 개수를 label에 표시한다.
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, view_model):
        super().__init__()
        
        self.view_model = view_model
        self.layout_top = QVBoxLayout()
        self.setLayout(self.layout_top)

        # layer_widget을 생성, 초기화하고 화면 상단에 배치한다.
        self.layer_widget = LayerWidget()
        self.layer_widget.setFixedSize(600, 600)
        self.layer_widget.on_drag = self.on_layer_drag      # 콜백 등록
        self.layer_widget.on_hover = self.on_layer_hover
        self.layer_widget.on_wheel = self.on_layer_wheel
        self.layer_widget.on_key_press = self.on_key_press
        self.layout_top.addWidget(self.layer_widget)

        # data_widget(170x70)을 생성하고 layer_widget 우상단에 겹쳐 배치한다
        data_widget_width = 180
        self.data_widget = QWidget(self.layer_widget)
        self.data_widget.setGeometry(
            self.layer_widget.width() - data_widget_width - 10, 
            10, 
            self.layer_widget.width() - 10, 
            10 + 70)
        self.data_widget.setContentsMargins(4, 4, 2, 4)
        self.data_widget.setFixedWidth(data_widget_width)
        self.data_widget.setStyleSheet("background-color: rgba(255, 255, 255, 32); border-radius:10px;")
        data_layout = QVBoxLayout(self.data_widget)
        data_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # label들을 생성하고 data_layout(data_widget)에 배치한다.
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
        self.layout_top.addSpacing(12)        

        # series_list_view를 생성, 초기화하고 화면 하단에 배치한다.
        self.series_list_view = QListView()
        self.series_list_view.setFixedSize(600, 125)
        self.series_list_view.setIconSize(QSize(100, 100))
        self.series_list_view.setFlow(QListView.Flow.LeftToRight)
        self.series_list_view.clicked.connect(self.on_series_click)
        self.layout_top.addWidget(self.series_list_view)

        # 현재 layer, series, 종양 단면적, 종양 부피 등의 정보를 observe하고 UI에 표시한다.
        self.view_model.current_layer.observe(self.layer_widget.set_layer)
        self.view_model.layers.observe(self.update_series_list_view)
        self.view_model.series_description.observe(self.update_series_description)
        self.view_model.area.observe(lambda area: self.area_label.setText(f'Area: {(area/100):.2f}㎤'))
        self.view_model.volume.observe(lambda volume: self.volume_label.setText(f'Volume: {(volume/1000):.2f}㎠'))

    def on_key_press(self, event: QKeyEvent):
        """
        키 눌림이 감지되면 뷰모델에 통보한다.

        Args:
            event (QKeyEvent): 키 이벤트
        """
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
        """
        series 리스트에서 항목 선택이 감지되면 뷰모델에 통보한다.

        Args:
            model_index (QModelIndex): 리스트뷰에서의 항목 위치
        """
        self.view_model.on_series_click(model_index.row())

    def on_layer_drag(self, pos_world):
        """
        LayerWidget이 drag 감지 시 호출하는 콜백. 마우스의 world 좌표를 뷰모델에 전달한다.
        
        Args:
            pos_world(list[float]): 마우스의 위치에 대응되는 world 좌표. x=[0], y=[1], z=[2]
        """
        self.view_model.on_layer_drag(pos_world)

    def on_layer_hover(self, pos_world):
        """
        LayerWidget이 hovering 감지 시 호출하는 콜백. 마우스의 world 좌표를 뷰모델에 통보한다.

        Args:
            pos_world (list[float]): 마우스의 위치에 대응되는 world 좌표. x=[0], y=[1], z=[2]
        """
        self.view_model.on_layer_hover(pos_world)

    def on_layer_wheel(self, up_down):
        """
        LayerWidget이 마우스 휠 조작 감지 시 호출하는 콜백. up/down(1,-1)을 뷰모델에 전달한다.

        Args:
            up_down (bool): 휠 up이면 true, down이면 false
        """
        self.view_model.on_layer_wheel_scroll_by(1 if up_down == True else -1)

    def update_series_list_view(self, layers):
        """
        series 리스트를 series_list에 업데이트한다.

        Args:
            layer_map(dict[str, Layer]): series의 이름과 그 series에 속하는 Layer 리스트가 key-value인 dictionary
        """
        model = QStandardItemModel()
        for series, layer_list in layers.items():
            # 각 series에 속하는 layer list 확보
            layer_list: list[Layer]
            if len(layer_list) > 0:
                # layer_list[0]을 series의 대표 이미지로 사용
                pixmap = layer_list[0].pixmap
                if pixmap is None:
                    pixmap = QPixmap(100, 100)      # series image는 100x100, 배경은 black
                    pixmap.fill(QColor.fromRgb(0, 0, 0, 255))
                scaled = pixmap.scaled(100, 100, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
                icon = QIcon(scaled)
                item = QStandardItem()
                item.setIcon(icon)
                item.setToolTip(series)
                model.appendRow(item)
        self.series_list_view.setModel(model)

    def update_series_description(self, description):
        """
        시리즈 이름과 현재 layer index, layer 개수를 label에 표시한다.

        Args:
            description(tuple): series 이름, layer 개수, 현재 layer index로 구성된 tuple

        """
        if description is not None:
            series, count, position = description   # unpack
            if len(series) >= 12:
                series = series[:11] + ".."
            self.series_label.setText(f'{series} ({1+position}/{count})')
        else:
            self.series_label.setText('DICOM IMAGES (0/0)')
