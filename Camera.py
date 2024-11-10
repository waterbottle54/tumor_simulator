
class Camera:
    """
    3D 공간에서의 관측자를 표현

    Attributes:
        x0(float): 

    Methods:

    """

    x0: float
    y0: float
    x1: float
    y1: float
    ratio: float
    
    def __init__(self, x0, y0, x1, y1): 
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def w(self):
        return (self.x1 - self.x0)
    
    def h(self):
        return (self.y1 - self.y0)
    
    def cx(self):
        return (self.x0 + self.x1) / 2

    def cy(self):
        return (self.y0 + self.y1) / 2
    
    def zoom_by(self, times):
        cx, cy = self.cx(), self.cy()
        self.x0 = cx - (cx - self.x0) / times
        self.x1 = cx + (self.x1 - cx) / times
        self.y0 = cy - (cy - self.y0) / times
        self.y1 = cy + (self.y1 - cy) / times

    def move_by(self, x_percent, y_percent):
        w, h = self.w(), self.h()
        self.x0 += x_percent * w
        self.x1 += x_percent * w
        self.y0 += y_percent * h
        self.y1 += y_percent * h

    def fit_to(self, w_object, h_object, aspect_ratio):
        if w_object / h_object > aspect_ratio:
            self.x0 = 0
            self.y0 = 0
            self.x1 = w_object
            self.y1 = w_object / aspect_ratio
            dy = (self.y1 - self.y0) / 2 - w_object / 2
            self.y0 -= dy
            self.y1 -= dy
        else:
            self.x0 = 0
            self.y0 = 0
            self.y1 = h_object
            self.x1 = h_object * aspect_ratio
            dx = (self.x1 - self.x0) / 2 - w_object / 2
            self.x0 -= dx
            self.x1 -= dx

    def get_transform(self, w_viewport, h_viewport):
        w, h = self.w(), self.h()
        m = float(w_viewport) / w
        n = float(h_viewport) / h
        dx = -float(w_viewport) * self.x0 / w
        dy = -float(h_viewport) * self.y0 / h
        return m, 0, 0, n, dx, dy
    
