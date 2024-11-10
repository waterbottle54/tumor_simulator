
class LiveData:
    def __init__(self, value):
        self.value = value
        self.observers = []
    
    def _set_value(self, value):
        self.value = value
        for observer in self.observers:
            observer(self.value)

    def _publish(self):
        self.set_value(self.value)

    def observe(self, observer):
        observer(self.value)
        self.observers.append(observer)
        if self.value is not None:
            observer(self.value)

class MutableLiveData(LiveData):
    def __init__(self, value):
        super().__init__(value)

    def set_value(self, value):
        super()._set_value(value)

    def publish(self):
        super()._publish()

def map(source, t):
    data = LiveData(None)
    source.observe(lambda value: data._set_value(t(value)))
    return data

def map2(source1, source2, t):
    data = LiveData(None)
    source1.observe(lambda value: data._set_value(t(value, source2.value)))
    source2.observe(lambda value: data._set_value(t(source1.value, value)))
    return data

def map3(source1, source2, source3, t):
    data = LiveData(None)
    source1.observe(lambda value: data._set_value(t(value, source2.value, source3.value)))
    source2.observe(lambda value: data._set_value(t(source1.value, value, source3.value)))
    source3.observe(lambda value: data._set_value(t(source1.value, source2.value, value)))
    return data
