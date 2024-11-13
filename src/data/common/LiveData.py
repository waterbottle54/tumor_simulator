"""
LiveData.py

이 모듈은 Observer 패턴을 구현하기 위해,
LiveData 클래스와, 기존의 LiveData로부터 새로운 LiveData를 파생하는 map 함수를 제공한다
LiveData는 초기값을 수정할 수 없지만, MutableLiveData는 수정 가능하다.

Example usage:
    ViewModel.py
    >>> import * from LiveData.py
    >>> width = MutableLiveData(3)                      # 정수 3을 값으로 갖는 LiveData를 선언한다
    >>> height = MutableLiveData(5)
    >>> area = map(width, height, lambda w, h: w * h)   # width and/or height 갱신 시 자동 갱신되는 area(LiveData) 파생
    App.py
    >>> view_model.area.observe(                        # area를 observe하고 갱신 시 label의 텍스트 자동 갱신
    >>>    lambda area: label.setText(f'{area}'cc))
    >>> view_model.width.set_value(6)                   # width 갱신 시, area의 값이 30으로 바뀌고, label의 텍스트도 '30cc'로 바뀐다.
"""

# Copyright (c) 2023 Sung Won Jo
# For more details: https://github.com/waterbottle54/tumor_simulator


class LiveData:
    """
    내부 값이 변경될때마다, 이 클래스를 관측하는 observer(함수/lambda)를 호출하여 콜백을 일으킨다.
    Attributes:
        value(Any): 현재 데이터
        observers(list): 이 LiveData를 관측하는 함수/lambda의 리스트

    Methods:
        _set_value: 현재 데이터를 변경하고 콜백 촉발 (protected)
        _publish: 현재 데이터를 변경하지 않고 콜백 촉발 (protected)
        observe: 현재 데이터가 바뀔 때 촉발될 콜백 추가

    """
    def __init__(self, value):
        self.value = value
        self.observers = []
    
    def _set_value(self, value):
        """현재 데이터를 수정하고, observer들을 호출하여 콜백을 일으킨다.

        Args:
            value (Any): 새로운 값
        """
        self.value = value
        for observer in self.observers:
            observer(self.value)

    def _publish(self):
        """현재 데이터를 수정하지 않고 observer들을 호출하여 콜백을 일으킨다.
        """
        self.set_value(self.value)

    def observe(self, observer):
        """데이터 변경 시 콜백을 받을 함수/lambda를 추가한다

        Args:
            observer (Callable[[Any], None]): 함수 또는 lambda
        """
        observer(self.value)
        self.observers.append(observer)
        if self.value is not None:
            observer(self.value)

class MutableLiveData(LiveData):
    """
    내부 data가 변경될때마다, 이 클래스를 observe하는 observer(함수/lambda)를 호출하여 콜백을 일으킨다.

    Attributes:
        value(Any): 현재 데이터
        observers: 이 LiveData를 observe하는 함수/lambda의 리스트

    Methods:
        set_value: 현재 데이터를 수정하고, observer들을 호출하여 콜백을 일으킨다.
        publish: 현재 데이터를 수정하지 않고 observer들을 호출하여 콜백을 일으킨다.

    """
    def __init__(self, value):
        super().__init__(value)

    def set_value(self, value):
        """현재 데이터를 수정하고, observer들을 호출하여 콜백을 일으킨다.

        Args:
            value (Any): 새로운 값
        """
        super()._set_value(value)

    def publish(self):
        """현재 데이터를 수정하지 않고 observer들을 호출하여 콜백을 일으킨다.
        """
        super()._publish()

def map(source, t):
    """
    한 가지의 livedata로부터 새 livedata를 파생한다. 
    Example usage: widthInCM = map(widthInInch, lambda: inch * 2.54)

    Args:
        source (LiveData): 참조할 기존 livedata
        t (Callable[[Any], Any]): 변환 함수

    Returns:
        LiveData: 파생된 livedata
    """
    data = LiveData(None)
    source.observe(lambda value: data._set_value(t(value)))
    return data

def map2(source1, source2, t):
    """
    두 가지의 livedata로부터 새 livedata를 파생한다. 
    Example usage: area = map(width, height: lambda: w, h: w*h)

    Args:
        source1 (LiveData): 참조할 기존 livedata
        source2 (LiveData): 참조할 기존 livedata
        t (Callable[[Any, Any], Any]): 변환 함수

    Returns:
        LiveData: 파생된 livedata
    """
    data = LiveData(None)
    source1.observe(lambda value: data._set_value(t(value, source2.value)))
    source2.observe(lambda value: data._set_value(t(source1.value, value)))
    return data

def map3(source1, source2, source3, t):
    """
    3 가지의 livedata로부터 새 livedata를 파생한다. 
    Example usage: volume = map(width, height, depth: lambda: w, h, d: w*h*d)

    Args:
        source1 (LiveData): 참조할 기존 livedata
        source2 (LiveData): 참조할 기존 livedata
        source3 (LiveData): 참조할 기존 livedata
        t (Callable[[Any, Any, Any], Any]): 변환 함수

    Returns:
        LiveData: 파생된 livedata
    """
    data = LiveData(None)
    source1.observe(lambda value: data._set_value(t(value, source2.value, source3.value)))
    source2.observe(lambda value: data._set_value(t(source1.value, value, source3.value)))
    source3.observe(lambda value: data._set_value(t(source1.value, source2.value, value)))
    return data
