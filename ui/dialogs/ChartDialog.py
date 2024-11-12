from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from data.Tumor import *

class ChartDialog(QDialog):
    """
    종양 모델 리스트를 입력받고, 성장 패턴을 그래프(plot)로 보여주는 대화상자
    좌측 그래프: 시간에 따른 종양의 체적
    우측 그래프: 시간에 따른 종양의 성장률(체적의 증가율)

    Attributes:
        tumor_models(list[TumorModel]): 시간대순(오름차순)으로 정렬된 종양 모델 리스트
        figure(Figure): matplotlib의 GUI 객체 
        canvas(FigureCanvas): matplotlib의 그리기 화면
        axes1(Axes): 시간-체적 그래프
        axes2(Axes): 시간-성장률 그래프

    Methods:
        update_graph: 현재 종양 모델 리스트를 기반으로 성장패턴을 그래프로 표시한다.
    """
    
    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, parent, tumor_models):
        super().__init__(parent)

        # 부피를 가진 종양 모델 획득 / 촬영시간 시간대순(오름차순) 정렬
        self.tumor_models = [ tumor for tumor in tumor_models if tumor.volume > 0 ]
        self.tumor_models = sorted(self.tumor_models, key=lambda x: x.date)

        self.setWindowTitle("Growth Pattern")
        self.setGeometry(0, 0, 1200, 500)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # 시간-체적 그래프 (1행 2열 격자 중 1행 1열 위치)
        self.axes1 = self.figure.add_subplot(121)
        self.axes1.set_ylabel("Volume (cc)")

        # 시간-성장률 그래프 (1행 2열 격자 중 1행 2열 위치)
        self.axes2 = self.figure.add_subplot(122)
        self.axes2.set_ylabel("Growth Rate (cc/month)")

        layout.addWidget(self.canvas)
        self.update_graph()

    def update_graph(self):
        """
        현재 종양 모델 리스트를 기반으로 시간-체적 그래프, 시간-성장률 그래프를 표시한다.
        """
        
        # 종양 모델이 1개 이하일 때 성장 추이 표시 불가
        if len(self.tumor_models) <= 1:
            return

        # x(시간) 축에 표시할 날짜 및 날짜 간 간격 추출
        dates = [ tumor.date for tumor in self.tumor_models ]
        str_dates = [ d.strftime('%m-%d') for d in dates ]
        str_periods = [ f'{str_dates[i-1]}~{str_dates[i]}' if i == 1 else f'~{str_dates[i]}' for i in range(1, len(str_dates)) ]

        # y(체적, 성장률) 축에 표시할 값 추출
        volumes = [ tumor.volume/1000 for tumor in self.tumor_models ]
        rates = []

        tumor_prev = None
        for tumor in self.tumor_models:
            if tumor_prev is not None:
                volume = tumor.volume/1000                      # 단위 변환: mm2 to cm2 
                volume_prev = tumor_prev.volume/1000
                days = (tumor.date - tumor_prev.date).days
                dv = volume - volume_prev
                rates.append(dv/days*30 if days > 0 else 0)     # 성장률은 1개월간 체적 변화율 (cm2/month)
            tumor_prev = tumor

        self.axes1.plot(dates, volumes)
        self.axes1.set_xticks(dates)
        self.axes1.set_xticklabels(str_dates)

        self.axes2.bar(str_periods, rates, width=0.5)

