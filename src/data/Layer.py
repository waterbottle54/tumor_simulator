import numpy as np
import datetime
from PyQt5.QtGui import QPixmap, QImage
import pydicom
import mritopng
from mritopng.models import GrayscaleImage


class Layer:
    """ DICOM을 구성하는 한 시리즈(series)의 한 단면(layer)을 나타낸다

    Attributes:
        series(str): 이 layer를 포함하는 시리즈의 이름 (e.g. Gd Inhanced Axial)
        study_date(date): 촬영일자(UTC+0)
        birth_date(date): 환자 생년월일
        pixel_spacing(list[float]): 이미지의 픽셀 간 물리적 거리 (dx=[0], dy=[1])
        position(list[float]): 환자의 물리적 위치, x(L/R)=[0], y(A/P)=[1], z(H/F)=[2])
        direction_row(list[float]): 이미지의 픽셀행(row)의 물리적(world) 방향벡터
        direction_column(list[float]): 이미지의 픽셀열(column)의 물리적 방향벡터
        pixmap(QPixmap): 단면의 픽셀 이미지 (grayscaled)
        path(list[list[float]]): 종양의 경계를 이루는 vertex의 리스트. [x0, y0, z0, x1, y1, z1, ...]

    Methods:
        from_dicom_file(classmethod): DICOM 데이터 파일을 읽어 Layer객체를 생성한다
        from_layer(classmethod): 다른 레이어를 복사하여 새 레이어를 생성한다
        get_area: 단면의 넓이를 계산하여 리턴한다
        get_distance: 다른 레이어와의 gap을 구한다
        image_to_world: 이미지 상의 좌표를 그에 대응되는 실세계 좌표로 변환한다
        world_to_image: 실세계 좌표를 그에 대응되는 이미지 좌표로 변환한다
        
    """
            
    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(
        self,
        series,
        study_date,
        birth_date,
        pixel_spacing,
        position,
        direction_row,
        direction_col,
        pixmap,
        path,
    ):
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
        """
        DICOM 데이터 파일을 읽어 Layer객체를 생성한다

        Args:
            filename (str): DICOM 데이터 파일의 경로

        Raises:
            ValueError: 누락된 정보가 있을 때 발생

        Returns:
            Layer: 생성된 레이어 객체
        """
        dicom = pydicom.dcmread(filename)
        if dicom is None:
            raise ValueError("dicom must not be None")
        attributes = [
            "SeriesDescription",
            "PixelSpacing",
            "ImagePositionPatient",
            "ImageOrientationPatient",
            "StudyDate",
            "PatientBirthDate",
        ]
        for attr in attributes:
            if not hasattr(dicom, attr):
                raise ValueError(f"dicom must have '{attr}' attribute")
        series = dicom.SeriesDescription
        study_date = datetime.datetime.strptime(dicom.StudyDate, "%Y%m%d").date()
        birth_date = datetime.datetime.strptime(dicom.PatientBirthDate, "%Y%m%d").date()
        pixel_spacing = dicom.PixelSpacing
        position = dicom.ImagePositionPatient
        direction_row = dicom.ImageOrientationPatient[:3]
        direction_row = direction_row / np.linalg.norm(direction_row)
        direction_col = dicom.ImageOrientationPatient[3:]
        direction_col = direction_col / np.linalg.norm(direction_col)
        grayscale_image: GrayscaleImage = mritopng.extract_grayscale_image(filename)
        image = QImage(
            grayscale_image.image,
            grayscale_image.width,
            grayscale_image.height,
            QImage.Format.Format_Grayscale8,
        )
        pixmap = QPixmap.fromImage(image)
        if pixmap is None:
            raise ValueError("pixmap must not be None")
        return Layer(
            series,
            study_date,
            birth_date,
            pixel_spacing,
            position,
            direction_row,
            direction_col,
            pixmap,
            [],
        )

    @classmethod
    def from_layer(cls, layer):
        """
        다른 레이어를 복사하여 새 레이어를 생성한다

        Args:
            layer (Layer): 참조할 레이어

        Raises:
            ValueError: layer가 None일 때

        Returns:
            Layer: 생성된 레이어
        """
        if layer is None:
            raise ValueError("layer must not be None")
        path = []
        for point in layer.path:
            path.append([point[0], point[1], point[2]])
        return Layer(
            layer.series,
            layer.study_date,
            layer.birth_date,
            layer.pixel_spacing,
            layer.position,
            layer.direction_row,
            layer.direction_col,
            layer.pixmap,
            path,
        )

    def get_area(self):
        """
        원점, 두 이웃하는 꼭지점으로 형성되는 삼각형의 넓이를 모두 구하여 단면의 넓이를 리턴한다
        calculate the area of self.path by summing up the area of triangles which are formed by 
        (0,0,0), one vertext(v1), and the next one(v2). (v1)x(v2)/2 will be each small area.

        Returns:
            float: self.path가 이루는 내부 면적 (mm2)
        """
        
        if len(self.path) < 3:  # make sure that self.path is closed
            return 0
        n = len(self.path)
        cross_product_sum = np.zeros(3)
        for i in range(n):
            current = self.path[i]
            next = self.path[(i + 1) % n]   # so that the last point is connected to the first, making a closed path 
            cross_product = np.cross(current, next)
            cross_product_sum += cross_product
        return 0.5 * np.linalg.norm(cross_product_sum)

    def get_distance(self, other):
        """
        다른 레이어와 이격된 거리를 구한다

        Args:
            other (Layer): 이격된 다른 레이어

        Returns:
            float: 이격된 거리 (mm)
        """
        n = np.cross(self.direction_row, self.direction_col)        # self의 단위방향벡터 n
        r = np.array(other.position) - np.array(self.position)      # self에 대한 other의 위치벡터 r
        return abs(np.dot(r, n))                                    # 위치벡터 r을 단위방향벡터 n에 projection한 값 (거리)

    def image_to_world(self, coord_image):
        """
        2D 이미지 좌표를 그에 대응되는 실제 공간(world)의 3D 좌표로 변환한다

        Args:
            coord_image (list[float]): 이미지 좌표. x=[0], y=[1]

        Returns:
            list[float]: 변환된 실제 공간 상의 3D 좌표
        """
        
        # get dicom data
        du, dv = self.pixel_spacing
        u = np.array(self.direction_row)
        v = np.array(self.direction_col)

        # transform image coordinates (j, i) to world coordinates (x, y, z)
        j, i = coord_image[0], coord_image[1]
        coord_world = np.array(self.position) + (j * du * u) + (i * dv * v)
        return coord_world.tolist()

    def world_to_image(self, coord_world):
        """
        3D world 좌표를 그에 대응되는 image 상의 좌표(2D)로 변환한다

        Args:
            coord_world (list[float]): world 좌표. x=[0], y=[1], z=[2]

        Returns:
            list[float]: 변환된 이미지 상의 좌표
        """

        # get dicom data
        du, dv = self.pixel_spacing
        u = np.array(self.direction_row)
        v = np.array(self.direction_col)

        # transform world coordinates (x, y, z) to image coordinates (j, i)
        pos_relative = np.array(coord_world) - np.array(self.position)
        j = np.dot(pos_relative, u) / np.linalg.norm(u) / du
        i = np.dot(pos_relative, v) / np.linalg.norm(v) / dv
        return [j, i]
