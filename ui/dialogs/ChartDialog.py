import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from data.Tumor import *

class ChartDialog(QDialog):

    tumor_models: list[TumorModel]

    def __init__(self, parent, tumor_models):
        super().__init__(parent)
        self.tumor_models = [ tumor for tumor in tumor_models if tumor.volume > 0 ]
        self.tumor_models = sorted(self.tumor_models, key=lambda x: x.date)

        self.setWindowTitle("Growth Pattern")
        self.setGeometry(0, 0, 1200, 500)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.axes1 = self.figure.add_subplot(121)
        self.axes1.set_ylabel("Volume (cc)")

        self.axes2 = self.figure.add_subplot(122)
        self.axes2.set_ylabel("Growth Rate (cc/month)")

        layout.addWidget(self.canvas)
        self.update_chart()

    def update_chart(self):

        if len(self.tumor_models) < 2:
            return

        dates = [ tumor.date for tumor in self.tumor_models ]
        str_dates = [ d.strftime('%m-%d') for d in dates ]
        str_periods = [ f'{str_dates[i-1]}~{str_dates[i]}' if i == 1 else f'~{str_dates[i]}' for i in range(1, len(str_dates)) ]
        volumes = [ tumor.volume/1000 for tumor in self.tumor_models ]
        rates = []

        tumor_prev = None
        for tumor in self.tumor_models:
            if tumor_prev is not None:
                volume = tumor.volume/1000
                volume_prev = tumor_prev.volume/1000
                days = (tumor.date - tumor_prev.date).days
                dv = volume - volume_prev
                dp = (volume - volume_prev) / volume_prev * 100
                rates.append(dv/days*30 if days > 0 else 0)
            tumor_prev = tumor

        self.axes1.plot(dates, volumes)
        self.axes1.set_xticks(dates)
        self.axes1.set_xticklabels(str_dates)

        self.axes2.bar(str_periods, rates, width=0.5)

