
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHeaderView, QTableWidgetItem
from PyQt5.QtGui import QColor
from ui.ViewModel import *
from ui.rendering.RenderingWidget import *

class RenderingFragment(QWidget):

    view_model: ViewModel
    layout = QVBoxLayout
    rendering_widget: RenderingWidget
    tumor_table: QTableWidget


    def __init__(self, view_model: ViewModel):
        super().__init__()

        self.view_model = view_model
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.rendering_widget = RenderingWidget()
        self.rendering_widget.setFixedSize(600, 600)
        self.layout.addWidget(self.rendering_widget)

        self.layout.addSpacing(12)

        self.tumor_table = QTableWidget(self)
        self.tumor_table.setColumnCount(3)
        self.tumor_table.horizontalHeader().hide()
        self.tumor_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tumor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tumor_table.itemSelectionChanged.connect(self.on_model_selected)
        self.layout.addWidget(self.tumor_table)

        self.view_model.current_tumor_model.observe(self.update_tumor_rendering)
        self.view_model.tumor_model_list.observe(self.update_tumor_table)

    def update_tumor_rendering(self, tumor_model):
        if tumor_model is not None:
            self.rendering_widget.set_mesh(tumor_model.mesh)
        else:
            self.rendering_widget.set_mesh(None)

    def update_tumor_table(self, tumors):
        self.tumor_table.setRowCount(len(tumors))
        for row, tumor in enumerate(tumors):
            item_patient = QTableWidgetItem(str(tumor.patient_birthday))
            item_date = QTableWidgetItem(str(tumor.date))
            item_volume = QTableWidgetItem(f'{tumor.volume/1000:.2f}㎤')
            if row == 0:
                color_special = QColor(241,231,64, 255)
                item_patient.setBackground(color_special)
                item_date.setBackground(color_special)
                item_volume.setBackground(color_special)
            self.tumor_table.setItem(row, 0, item_patient)
            self.tumor_table.setItem(row, 1, item_date)
            self.tumor_table.setItem(row, 2, item_volume)

    def on_model_selected(self):
        items = self.tumor_table.selectedItems()
        if len(items) > 0 and items[0].row() >= 0:
            self.view_model.on_model_selected(items[0].row())
        
    