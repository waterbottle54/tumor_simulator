
class TumorModelData:
    def __init__(self, points, volume, date, patient_birthday):
        self.points = points
        self.volume = volume
        self.date = date
        self.patient_birthday = patient_birthday
        
class TumorModel:
    def __init__(self, mesh, volume, date, patient_birthday):
        self.mesh = mesh
        self.volume = volume
        self.date = date
        self.patient_birthday = patient_birthday

    @classmethod
    def from_tumor_model_data(cls, data, mesh):
        return TumorModel(mesh, data.volume, data.date, data.patient_birthday)