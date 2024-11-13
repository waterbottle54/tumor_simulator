
class Camera:
    """
    평면좌표계를 관측하는 가상의 카메라로, 좌표평면에서 관측되는 사각영역의 범위를 설정할 수 있다.

    Attributes:
        x0(float): 사각 영역의 left 좌표
        y0(float): 사각 영역의 top 좌표
        x1(float): 사각 영역의 right 좌표
        y1(float): 사각 영역의 bottom 좌표
        ratio(float): 사각 영역의 화면비(width/height)

    Methods:
        w: 관측영역의 가로 길이를 리턴한다.
        h: 관측영역의 세로 길이를 리턴한다.
        cx: 관측영역의 중심의 x좌표를 리턴한다.
        cy: 관측영역의 중심의 y좌표를 리턴한다.
        zoom_by: 관측영역을 요청된 값만큼 넓히거나 좁힌다.
        move_by: 관측영역을 요청된 값만큼 움직인다.
        fit_to: 관측영역을 요청된 영역을 포함하는 최소의 영역으로 조정한다.
        get_transform: 관측영역을 요청된 viewport 영역으로 변환하는 행렬을 리턴한다.
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, x0, y0, x1, y1): 
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.ratio = (x1 - x0) / (y1 - y0)

    def w(self):
        # 관측영역의 가로 길이 리턴
        return (self.x1 - self.x0)
    
    def h(self):
        # 관측영역의 세로 길이 리턴
        return (self.y1 - self.y0)
    
    def cx(self):
        """
        관측영역 중심의 x좌표를 리턴한다

        Returns:
            (float): 관측영역 중심의 x좌표
        """
        return (self.x0 + self.x1) / 2

    def cy(self):
        """
        관측영역 중심의 y좌표를 리턴한다

        Returns:
            (float): 관측영역 중심의 y좌표
        """
        return (self.y0 + self.y1) / 2
    
    def zoom_by(self, times):
        """
        관측영역을 중심점을 기준으로 times배만큼 넓힌다. 
        ex) times > 1 이면 확장, times < 1 이면 축소.
        Args:
            times (float): 화면 증폭률
        """
        cx, cy = self.cx(), self.cy()
        self.x0 = cx - (cx - self.x0) / times
        self.x1 = cx + (self.x1 - cx) / times
        self.y0 = cy - (cy - self.y0) / times
        self.y1 = cy + (self.y1 - cy) / times

    def move_by(self, x_percent, y_percent):
        """
        관측영역을 가로, 세로 길이의 몇 퍼센트만큼 움직인다.
        ex) 가로의 10% 움직이면 +x 방향으로, 세로의 -10% 움직이면 -y 방향으로 이동.

        Args:
            x_percent (float): 가로 길이의 퍼센티지로 표현된 이동거리
            y_percent (float): 세로 길이의 퍼센티지로 표현된 이동거리
        """
        w, h = self.w(), self.h()
        self.x0 += x_percent * w
        self.x1 += x_percent * w
        self.y0 += y_percent * h
        self.y1 += y_percent * h

    def fit_to(self, w_object, h_object, aspect_ratio):
        """
        관측영역을 주어진 영역을 포함하는 최소의 영역으로 맞춘다 (화면비도 따라야함)

        Args:
            w_object (float): 주어진 영역의 가로 길이
            h_object (float): 주어진 영역의 세로 길이
            aspect_ratio (float): 관측 영역이 따라야하는 화면비
        """
        if w_object / h_object > aspect_ratio: # 주어진 영역이 관측영역보다 화면비가 큰 경우 (가로로 뚱뚱한 경우)
            self.x0 = 0
            self.y0 = 0
            self.x1 = w_object                  # 주어진 영역의 가로 길이에 맞추고 세로는 주어진 화면비에 따라 정한다
            self.y1 = w_object / aspect_ratio
            dy = (self.y1 - self.y0) / 2 - w_object / 2     # 주어진 영역이 관측영역의 수직 중심에 오도록 한다
            self.y0 -= dy
            self.y1 -= dy
        else:                                   # 주어진 영역이 관측영역보다 화면비가 작은 경우 (세로로 홀쭉한 경우)
            self.x0 = 0
            self.y0 = 0
            self.y1 = h_object                  # 주어진 영역의 세로 길이에 맞추고 가로는 주어진 화면비에 따라 정한다
            self.x1 = h_object * aspect_ratio
            dx = (self.x1 - self.x0) / 2 - w_object / 2     # 주어진 영역이 관측영역의 수평 중심에 오도록 한다
            self.x0 -= dx
            self.x1 -= dx

    def get_transform(self, w_viewport, h_viewport):
        """
        관측영역을 요청된 viewport 영역으로 변환시키는 행렬을 리턴한다

        Args:
            w_viewport (float): viewport의 가로 길이
            h_viewport (float): viewport의 세로 길이

        Returns:
            tuple: 변환 행렬로서 m(x축 배율), n(y축 배율), dx(x축 평행이동), dy(y축 평행이동)
        """
        w, h = self.w(), self.h()
        m = float(w_viewport) / w
        n = float(h_viewport) / h
        dx = -float(w_viewport) * self.x0 / w
        dy = -float(h_viewport) * self.y0 / h
        return m, 0, 0, n, dx, dy
    
