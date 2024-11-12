
#========================= TumorModelData Class ===============================

class TumorModelData:
    """
    point cloud로 구성된 3D 종양 모델을 표현한다.
    surface reconstruction을 통해, mesh로 구성된 3D 종양 모델(TumorModel)로 변환할 수 있다.

    Attributes:
        points(list): 종양의 표면을 이루는 point cloud. [x0, y0, z0, x1, y1, z1, ...] (mm)
        volume(float): 종양의 부피(mm2)
        date(datetime.date): 촬영일자
        patient_birthday(datetime.date): 환자 생년월일
    """
    
    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, points, volume, date, patient_birthday):
        self.points = points
        self.volume = volume
        self.date = date
        self.patient_birthday = patient_birthday

#========================= TumorModel Class ====================================

class TumorModel:
    """
    mesh로 구성된 3D 종양 모델을 표현한다.
    TumorModelData를 surface reconstruction을 통해 이 클래스로 변환할 수 있다.

    Attributes:
        mesh(TriangleMesh): 종양의 표면을 이루는 mesh
        volume(float): 종양의 부피(mm2)
        date(datetime.date): 촬영일자
        patient_birthday(datetime.date): 환자의 생년월일

        Methods:
            @classmethod
            from_tumor_model_data: TumorModelData와 mesh로부터 TumorModel을 생성한다.
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, mesh, volume, date, patient_birthday):
        self.mesh = mesh
        self.volume = volume
        self.date = date
        self.patient_birthday = patient_birthday

    @classmethod
    def from_tumor_model_data(cls, data, mesh):
        """TumorModelData와 mesh로부터 TumorModel을 생성한다.

        Args:
            data (TumorModelData): mesh가 없는 TumorModelData
            mesh (TriangleMesh): TumorModelData와 함께 TumorModel을 구성할 mesh

        Returns:
            TumorModel: TumorModelData와 mesh를 기반으로 TumorModel을 리턴한다
        """
        return TumorModel(mesh, data.volume, data.date, data.patient_birthday)