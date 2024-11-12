
class TumorModelData:
    """
    종양의 기본정보와 체적 및 point cloud를 포함한다.

    Attributes:
        points(list): 종양의 surface를 이루는 point cloud. [[x0, y0, z0], [x1, y1, z1], ...] (in cm)
        volume(float): 종양의 계측된 체적 (in cm3)
        date(datetime.date): 촬영일자
        patient_birthday(datetime.date): 환자 생년월일

    Methods:
        from_tumor_model_data(classmethod): TumorModelData로부터 TumorModel을 생성한다.
    """
    
    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, points, volume, date, patient_birthday):
        self.points = points
        self.volume = volume
        self.date = date
        self.patient_birthday = patient_birthday
        
class TumorModel:
    """
    종양의 기본정보와 체적 및 3D mesh를 포함한다.

    Attributes:
        mesh(TriangleMesh): 종양의 surface를 나타내는 mesh
        volume(float): 종양의 계측된 체적 (in cm3)
        date(datetime.date): 촬영일자
        patient_birthday(datetime.date): 환자 생년월일
    """
    def __init__(self, mesh, volume, date, patient_birthday):
        self.mesh = mesh
        self.volume = volume
        self.date = date
        self.patient_birthday = patient_birthday

    @classmethod
    def from_tumor_model_data(cls, data, mesh):
        """TumorModelData(not including mesh)로부터 TumorModel(including mesh)을 생성한다.

        Args:
            data (TumorModelData): 참조할 TumorModelData
            mesh (TriangleMesh): 참조할 mesh

        Returns:
            TumorModel: mesh가 포함된 TumorModel을 리턴한다
        """
        return TumorModel(mesh, data.volume, data.date, data.patient_birthday)