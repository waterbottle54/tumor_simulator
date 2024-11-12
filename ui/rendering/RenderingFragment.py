
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHeaderView, QTableWidgetItem
from PyQt5.QtGui import QColor
from ui.ViewModel import *
from ui.rendering.RenderingWidget import *

class RenderingFragment(QWidget):
    """
    view model의 3D 종양 모델을 렌더링하는 화면
    - 비교군 list를 표시하고 불러올 수 있다.

    Attributes:
        view_model(ViewModel): 뷰모델
        layout(QVBoxLayout): 최상위 레이아웃
        rendering_widget(RenderingWidget): 3D 렌더링 위젯
        tumor_table(QTableWidget): 비교군 list를 표시하는 위젯

    Methods:
        update_tumor_rendering: 요청된 종양 모델을 RenderingWidget으로 렌더링한다
        update_tumor_table: 요청된 비교군 종양 리스트를 TableWidget에 표시한다.
        on_model_selected: 비교군 list에서 종양이 선택되면 뷰모델에 통보한다.
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, view_model: ViewModel):
        super().__init__()

        # view model, layout 지정
        self.view_model = view_model
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # RenderingWidget를 생성하고 화면 상단에 배치한다
        self.rendering_widget = RenderingWidget()
        self.rendering_widget.setFixedSize(600, 600)
        self.layout.addWidget(self.rendering_widget)

        self.layout.addSpacing(12)

        # TableWidget을 생성하고 남는 하단에 배치한다.
        self.tumor_table = QTableWidget(self)
        self.tumor_table.setColumnCount(3)
        self.tumor_table.horizontalHeader().hide()
        self.tumor_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tumor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tumor_table.itemSelectionChanged.connect(self.on_model_selected)
        self.layout.addWidget(self.tumor_table)

        # 종양 모델과 비교군 리스트를 observe하고 UI에 업데이트한다
        self.view_model.current_tumor_model.observe(self.update_tumor_rendering)
        self.view_model.tumor_model_list.observe(self.update_tumor_table)

    def update_tumor_rendering(self, tumor_model):
        """
            요청된 종양 모델을 RenderingWidget으로 렌더링한다
        Args:
            tumor_model (TriangleMesh): 종양의 3D mesh 모델
        """
        if tumor_model is not None:
            self.rendering_widget.set_mesh(tumor_model.mesh)
        else:
            self.rendering_widget.set_mesh(None)

    def update_tumor_table(self, tumors):
        """
        요청된 비교군 종양 리스트를 TableWidget에 표시한다.

        Args:
            tumors (list[Tumor]): 종양 데이터 리스트
        """
        self.tumor_table.setRowCount(len(tumors))
        for row, tumor in enumerate(tumors):
            item_patient = QTableWidgetItem(str(tumor.patient_birthday))    # 환자 생년월일
            item_date = QTableWidgetItem(str(tumor.date))                   # 촬영 일시
            item_volume = QTableWidgetItem(f'{tumor.volume/1000:.2f}㎤')    # 종양 체적
            if row == 0:
                color_special = QColor(241,231,64, 255)
                item_patient.setBackground(color_special)
                item_date.setBackground(color_special)
                item_volume.setBackground(color_special)
            self.tumor_table.setItem(row, 0, item_patient)
            self.tumor_table.setItem(row, 1, item_date)
            self.tumor_table.setItem(row, 2, item_volume)

    def on_model_selected(self):
        """
        비교군 list에서 종양이 선택되면 뷰모델에 통보한다.
        """
        items = self.tumor_table.selectedItems()    # Multiselection not allowed
        if len(items) > 0 and items[0].row() >= 0:
            self.view_model.on_model_selected(items[0].row())
        
    