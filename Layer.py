import numpy as np
import datetime
from PyQt5.QtGui import QPixmap, QImage
import pydicom
import mritopng
from mritopng.models import GrayscaleImage

class Layer:

    series: str = None
    study_date: datetime.date = None
    birth_date: datetime.date = None
    pixel_spacing = [0.0, 0.0]
    position = [0.0, 0.0, 0.0]
    direction_row = [0.0, 0.0, 0.0]
    direction_col = [0.0, 0.0, 0.0]
    pixmap: QPixmap = None
    path: list = None

    def __init__(self, series, study_date, birth_date, pixel_spacing, position, direction_row, direction_col, pixmap, path):
        self.series = series
        self.study_date = study_date
        self.birth_date = birth_date
        self.pixel_spacing = pixel_spacing
        self.position = position
        self.direction_row = direction_row
        self.direction_col = direction_col
        self.pixmap = pixmap
        self.path = path

    @classmethod
    def from_dicom_file(cls, filename):
        dicom = pydicom.dcmread(filename)
        if dicom is None:
            raise ValueError("dicom must not be None")
        attributes = ['SeriesDescription', 'PixelSpacing', 'ImagePositionPatient', 'ImageOrientationPatient', 'StudyDate', 'PatientBirthDate' ]
        for attr in attributes:
            if not hasattr(dicom, attr):
                raise ValueError(f"dicom must have '{attr}' attribute")
        series = dicom.SeriesDescription
        study_date = datetime.datetime.strptime(dicom.StudyDate, '%Y%m%d').date()
        birth_date = datetime.datetime.strptime(dicom.PatientBirthDate, '%Y%m%d').date()
        pixel_spacing = dicom.PixelSpacing
        position = dicom.ImagePositionPatient
        direction_row = dicom.ImageOrientationPatient[:3]
        direction_row = direction_row / np.linalg.norm(direction_row)
        direction_col = dicom.ImageOrientationPatient[3:]
        direction_col = direction_col / np.linalg.norm(direction_col)
        grayscale_image: GrayscaleImage = mritopng.extract_grayscale_image(filename)
        image = QImage(grayscale_image.image, grayscale_image.width, grayscale_image.height, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(image)
        if pixmap is None:
            raise ValueError("pixmap must not be None")
        return Layer(series, study_date, birth_date, pixel_spacing, position, direction_row, direction_col, pixmap, [])

    @classmethod
    def from_layer(cls, layer):
        if layer is None:
            raise ValueError("layer must not be None")
        path = []
        for point in layer.path:
            path.append([point[0], point[1], point[2]])
        return Layer(layer.series, layer.study_date, layer.birth_date, layer.pixel_spacing, layer.position, layer.direction_row, layer.direction_col, layer.pixmap, path)
        
    def get_area(self):
        if len(self.path) < 3:
            return 0
        n = len(self.path)
        cross_product_sum = np.zeros(3)
        for i in range(n):
            current = self.path[i]
            next = self.path[(i + 1) % n]
            cross_product = np.cross(current, next)
            cross_product_sum += cross_product
        return 0.5 * np.linalg.norm(cross_product_sum)

    def get_distance(self, other):
        n = np.cross(self.direction_row, self.direction_col)
        r = np.array(other.position) - np.array(self.position)
        return abs(np.dot(r, n))

    def image_to_world(self, coord_image):
        # get dicom data
        du, dv = self.pixel_spacing
        u = np.array(self.direction_row)
        v = np.array(self.direction_col)
        
        # transform image coordinates (j, i) to world coordinates (x, y, z)
        j, i = coord_image[0], coord_image[1]
        coord_world = np.array(self.position) + (j * du * u) + (i * dv * v) 
        return coord_world.tolist()
    
    def world_to_image(self, coord_world):
        # get dicom data
        du, dv = self.pixel_spacing
        u = np.array(self.direction_row)
        v = np.array(self.direction_col)
        
        pos_relative = np.array(coord_world) - np.array(self.position)
        j = np.dot(pos_relative, u) / np.linalg.norm(u) / du
        i = np.dot(pos_relative, v) / np.linalg.norm(v) / dv
        return [j, i]