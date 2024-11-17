from PyQt5.QtCore import QObject, pyqtSignal
from datetime import date
from data.common.LiveData import *
from data.Layer import *
from data.Tumor import *
import utils.O3dUtil
import numpy as np
import pickle
import logging

class Event: pass
class ShowMessage(Event):
    def __init__(self, message):
        self.message = message
class PromptDicomFiles(Event): pass
class PromptOpenFile(Event): pass
class PromptSaveFile(Event): pass
class ConfirmNewFile(Event): pass
class ConfirmDeleteSeries(Event):
    def __init__(self, series, any_point):
        self.series = series
        self.any_point = any_point
class PromptExportModel(Event): pass
class PromptOpenModels(Event): pass
class ShowGrowthPattern(Event):
    def __init__(self, tumor_models):
        self.tumor_models = tumor_models
class ConfirmExit(Event): pass
class TerminateApp(Event): pass

class ViewModel(QObject):
    """
    프로젝트의 단일한 뷰모델

    - ViewModel에 연결된 UI 모듈: MainWindow, LayerFragment, RenderingFragment
    - Observer 패턴을 구현하기 위해 data를 LiveData 형태로 노출한다.

    Ability:
        - Dicom file로부터 *series, **layer를 읽어들이고 data model로 변환할 수 있다.
        - Series, layer model에 대한 연산(select, delete, tumor marking)을 수행할 수 있다.
        - Memento pattern을 통해 undo, redo 동작을 수행할 수 있다.
        - Tumor marking을 통해 구성된 point cloud로 3D mesh 및 TumorModel을 빌드할 수 있다.
        - TumorModelData를 *.tmr 파일로 export 할 수 있다. (mesh가 아닌 point cloud가 저장된다.)
        - 다른 시기에 촬영된 종양(*.tmr)을 불러와 대조군으로 설정하고 연산(선택, 제거)을 할 수 있다.
        - 작성한 프로젝트 파일(*.bts)을 저장하고 불러올 수 있다.

    * series: 한 번의 scan으로 촬영된 온전한 영상
    ** layer: series를 구성하는 각각의 단면

    Attributes:
        current_filename(MutableLiveData[str]): 현재 열린 프로젝트 파일(*.bts)의 filename
        current_world_position(MutableLiveData[float]): 커서 등의 layer 상의 위치에 대응하는 world position

        series_title(MutableLiveData[str]): 현재 선택된 series의 제목
        series_description(LiveData[tuple[str, int, int]]): 현재 선택된 series의 제목, layer 수, 선택된 layer index

        layers(MutableLiveData[dict[str, list[Layer]]]): series 제목을 key로 하고, 그 series를 이루는 layer들을 value로 하는 자료구조
        index_layer(MutableLiveData[int]): layers 내에서 현재 선택된 layer의 index
        current_layer(LiveData[Layer]): 현재 선택된 layer
        area(LiveData[float]): 현재 layer에서 마킹된 폐곡선(path)의 넓이(mm2)
        volume(LiveData[float]): 각 layer의 폐곡선에 구분구적법을 적용한 종양 부피(mm3)

        undo_stack(list[dict]): dict에 저장된 상태(state)의 undo 스택
        redo_stack(list[dict]): dict에 저장된 상태(state)의 redo 스택

        mesh(MutableLiveData[TriangleMesh]): 종양 표면을 구성하는 3D mesh (layer의 point cloud를 reconstruct하여 얻는다)
        tumor_model(LiveData[TumorModel]): 프로젝트 종양 모델 (mesh와 종양의 세부정보 포함)

        comparison_models(MutableLiveData[list[TumorModel]]): 종양 대조군 리스트 (최신 촬영순)
        tumor_model_list(LiveData[list[TumorModel]]): 프로젝트 종양 모델, 종양 대조군 모델을 병합한 리스트
        tumor_model_index(MutableLiveData[int]): tumor_model_list에서 현재 선택된 TumorModel의 index
        current_tumor_model(LiveData[TumorModel]): tumor_model_list에서 현재 선택된 TumorModel

    Methods:
        on_new_project_click:       메뉴가 클릭되면 유저의 의사를 재확인한다.
        on_new_project_confirm:     유저의 의사가 확인되면 프로젝트 상태(state)를 clean-up한다.
        on_open_project_click:      메뉴가 클릭되면 파일 탐색기 이벤트를 발생시킨다.
        on_open_project_result:     프로젝트 파일(*.bts)이 선택되면 파일에 저장된 데이터를 불러온다.
        on_save_project_click:      메뉴가 클릭되면 파일 탐색기 이벤트를 발생시킨다.
        on_save_project_result:     파일이 선택되면 현재 상태를 프로젝트 파일(*.bts)로 저장한다.
        on_exit_click:              메뉴가 클릭되면 유저의 종료 의사를 재확인한다.
        on_exit_confirm:            유저의 의사가 확인되면 프로그램 종료 이벤트를 발생시킨다.

        on_import_dicom_click:      import 메뉴 클릭 시 파일 탐색기 이벤트를 발생시킨다.
        on_import_dicom_result:     파일이 선택되면 dicom 파일을 불러온다.
        on_undo_click:              메뉴가 클릭되면 undo를 실행한다.
        on_redo_click:              메뉴가 클릭되면 redo를 실행한다.
        on_clear_path_click:        메뉴가 클릭되면 현재 layer의 종양 경계를 삭제한다.

        on_delete_layer_click:      layer 삭제 클릭 시 선택된 layer를 삭제한다.
        on_delete_series_click:     series 삭제 클릭 시 삭제를 확인하는 대화상자를 띄운다.
        on_delete_series_confirm:   series 삭제에 동의한 경우 series를 삭제한다.

        on_series_click:            series가 클릭된 경우 해당 series를 선택하고 0번째 layer를 선택한다.
        on_index_layer_change:      주어진 index 위치의 layer를 선택한다.
        on_layer_drag:              현재 layer 위에 drag가 감지되면 종양 경계를 연장한다.
        on_layer_hover:             Hovering이 감지되면 현재 world position 값을 업데이트한다.
        on_layer_scroll_by:         offset만큼 index가 다른 layer를 선택하려는 의도가 감지되면 해당 layer를 선택한다.
        on_layer_scroll_to:         주어진 index에 있는 layer를 선택하려는 의도가 감지되면 해당 layer를 선택한다.
        on_layer_scroll_to_end:     마지막 layer를 선택하려는 의도가 감지되면 해당 layer를 선택한다.

        on_model_selected:            종양 모델이 클릭되면 해당 모델을 선택한다.
        on_reconstruct_click:         메뉴 클릭 시 종양의 point cloud로부터 곡면(mesh)을 계산한다.
        on_export_model_click:        메뉴 클릭 시 파일 탐색기 이벤트를 발생시킨다.
        on_export_model_result:       경로가 선택되면 프로젝트 종양 모델을 파일(*.tmr)로 저장한다.
        on_add_comparison_click:      메뉴가 클릭되면 파일 탐색기 이벤트를 발생시킨다.
        on_add_comparison_result:     외부 종양 모델 파일 경로(*.tmr)가 정해지면 대조군으로 읽어들인다.
        on_show_growth_pattern_click: 메뉴가 클릭되면 ShowGrowthPattern 이벤트를 발생시킨다.

        _is_valid_selection:        주어진 series가 실존하고 layer index가 유효한 범위에 있으면 True, 아니면 False를 리턴한다.
        _get_series_at:             주어진 index번째 series를 리턴한다.
        _delete_series:             현재 선택된 series를 삭제한다.
        _import_dicom_files:        주어진 dicom 파일들을 읽어 layer들을 생성하고 series별로 정리한다.

        _reconstruct_surface:       현재 선택된 series의 종양 경계점들(point cloud)을 reconstruct하여 종양의 곡면(mesh)을 계산한다.
        _extract_points:            현재 선택된 series의 종양 경계점들(point cloud)을 추출하여 리턴한다.
        _get_series_tumor_volume:   주어진 series의 종양 경계점들이 형성하는 곡면의 내부 부피(mm3)를 계산한다.
        _get_average_tumor_volume:  모든 series에서 계산된 종양 부피의 평균(mm3)을 계산한다.

        _get_current_state:         현재 프로젝트의 상태(state)를 리턴한다. undo, redo, serialization 등에 사용된다.
        _set_current_state:         프로젝트 상태를 주어진 state로 설정한다. serialization, undo, redo 등에 사용된다.
        _clean_up_state:            현재 프로젝트의 상태(state)를 초기화한다.
        _undo_state:                현재 상태를 redo 스택에 저장한 후 undo 한다.
        _redo_state:                현재 상태를 undo 스택에 저장한 후 redo 한다.
        _backup_undo:               undo 스택에 현재 상태를 백업한다.
   
    Copyright (c) 2023 Sung Won Jo
    
    For more details: [Github](https://github.com/waterbottle54/tumor_simulator)
    """

    event = pyqtSignal(Event)
    
    def __init__(self):
        super().__init__()

        self.current_filename = MutableLiveData(None)
        self.current_world_position = MutableLiveData(None)

        self.current_series = MutableLiveData(None)

        # 각 series를 이루는 layer의 배열을 value로 하고, 각 series의 이름을 key로 하는 dict형 자료구조
        # 'Flare Axial' series의 첫 번째 layer에 접근하려면 self.layers['Flare Axial'][0] 과 같이 접근한다.
        self.layers = MutableLiveData(dict[str, list[Layer]]())
        self.index_layer = MutableLiveData(0)

        self.undo_stack = []
        self.redo_stack = []

        self.mesh = MutableLiveData(None)
        self.comparison_models = MutableLiveData([])
        self.tumor_model_index = MutableLiveData(0)

        # 현재 선택된 series에 대한 설명
        self.series_description = map3(self.current_series, self.layers, self.index_layer, 
                                        lambda series_title, layers, index: 
                                            (series_title, len(layers[series_title]), index)
                                            if series_title is not None and series_title in layers 
                                            else None)

        # 현재 선택된 layer
        self.current_layer = map3(
                    self.layers, self.current_series, self.index_layer,
                    lambda layers, series, index: layers[series][index] 
                    if self.is_valid_selection(series, index) else None)


        # layer의 마킹된 폐곡선의 넓이
        self.area = map(self.current_layer, lambda layer: layer.get_area() if layer is not None else 0)

        # 종양의 부피
        self.volume = map3(self.layers, self.current_series, self.index_layer, lambda _, series, __: self.get_series_tumor_volume(series))

        # 프로젝트 종양 모델 (mesh 포함)
        self.tumor_model_project = map3(self.mesh, self.volume, self.current_layer,
                            lambda mesh, _, layer: TumorModel(mesh, self.get_average_tumor_volume(), layer.study_date, layer.birth_date)
                            if layer is not None else TumorModel(None, 0, date.today(), None))

        # 종양 모델 리스트 (프로젝트 모델 + 대조군 모델)
        self.tumor_model_list = map2(self.tumor_model_project, self.comparison_models,
                                lambda tumor_model, comparison_models: [tumor_model] + comparison_models)
        
        # 현재 선택된 종양 모델
        self.current_tumor_model = map2(self.tumor_model_list, self.tumor_model_index,
                                    lambda tumor_list, index: tumor_list[index] if 0 <= index < len(tumor_list) else None)

    def is_valid_selection(self, series_title, index_layer):
        """
        주어진 series가 존재하고 layer index가 유효한 범위에 있으면 True, 아니면 False를 리턴한다.

        Args:
            series_title (str): Series 제목
            index_layer (int): Layer 인덱스

        Returns:
            bool: True: 주어진 series가 존재하고 layer index가 유효한 범위에 있다.\n
            False: Otherwise
        """
        layers = self.layers.value
        if series_title not in layers:
            return False
        if (index_layer < 0) or (index_layer >= len(layers[series_title])):
            return False
        return True

    def get_series_at(self, layers: dict[str, list[Layer]], index):
        """
        주어진ㄹ layer의 key(=series title)들 중 index번째 key를 리턴한다.

        Args:
            layers (dict[str, list[Layer]]): 검색할 layers(dict)
            index (int): 찾고자 하는 series의 index

        Returns:
            str: index번째 series의 제목
        """
        return list(layers.keys())[index]
    
    def on_import_dicom_click(self):
        """
        import 메뉴 클릭 시 파일 탐색기 이벤트를 발생시킨다.
        """
        self.event.emit(PromptDicomFiles())

    def on_import_dicom_result(self, filenames):
        """
        import할 파일의 경로가 입력되었으면 import를 처리한다.
        
        Args:
            filenames (list[str]): import할 dicom 파일들의 경로 리스트
        """

        if len(filenames) > 0:
            self.event.emit(ShowMessage('Importing may take 1~2 minutes.'))
        else:
            self.event.emit(ShowMessage('Select a folder that directly contains DICOM files in it.'))
            return
        
        self.import_dicom_files(filenames)

    def import_dicom_files(self, filenames):
        """
        dicom 파일들을 읽어 layer들을 생성하고 series별로 정리한다.

        Args:
            filenames (list[str]): import할 dicom 파일들의 경로 리스트
        """
        layers = self.layers.value
        for filename in filenames:
            # 개별 dicom 파일을 읽어 Layer의 list를 구성하고 layers에 보관한다.
            try:
                layer = Layer.from_dicom_file(filename)
            except Exception as e: 
                logging.basicConfig(filename='error.log', level=logging.DEBUG)
                logging.error(f'on_import_result: {str(e)}')
                print(str(e))
                continue
            series = layer.series
            if layer.series in layers:
                layers[series].append(layer)
            else:
                layers[series] = [layer]

        if len(layers) > 0:
            first_series = self.get_series_at(layers, 0)        #  첫 번째 series를 선택한다
            self.current_series.set_value(first_series)
            self.layers.publish()                               # 리스트 변화를 publish한다. (set_value()가 사용되지 않았으므로.)
            if len(layers[first_series]) > 0:
                self.index_layer.set_value(0)
                

    def on_delete_layer_click(self):
        """
        layer 삭제 클릭 시 선택된 layer를 삭제한다.
        """
        layers = self.layers.value
        series = self.current_series.value
        index_layer = self.index_layer.value
        if self.is_valid_selection(series, index_layer):    # 선택이 유효한지 검증한다.
            self.backup_undo()                              # 삭제 전 상태를 undo 스택에 백업한다.
            layers[series].pop(index_layer)
            if len(layers[series]) == 0:                    # series의 마지막 layer가 삭제되면 series도 삭제한다.
                self.delete_series(series)
            elif index_layer == len(layers[series]):        # 삭제로 인해 선택이 범위를 벗어난 경우 마지막 layer를 선택한다.
                self.index_layer.set_value(index_layer - 1)
            self.layers.publish()

    def on_delete_series_click(self):
        """
        series 삭제 클릭 시 삭제를 확인하는 대화상자를 띄운다.
        """
        series = self.current_series.value
        if series in self.layers.value:
            layer_list = self.layers.value[series]
            any_points = False          # 종양 마킹 여부 flag
            for layer in layer_list:
                if len(layer.path) > 0:
                    any_points = True
                    break
            # 종양 마킹이 있으면 삭제 의사를 묻는다.
            if any_points is True:
                self.event.emit(ConfirmDeleteSeries(series, any_points))
            # 마킹이 없으면 삭제한다.
            else:
                self.backup_undo()                  # 삭제 전 상태를 undo 스택에 백업한다.
                self.delete_series(series)

    def on_delete_series_confirm(self, series_title):
        """
        series 삭제에 동의한 경우 series를 삭제한다.

        Args:
            series (str): 삭제할 series 제목
        """
        if series_title in self.layers.value:
            self.backup_undo()                      # 삭제 전 상태를 undo 스택에 백업한다.
            self.delete_series(series_title)

    def on_series_click(self, idx_new):
        """
        series 가 클릭된 경우 해당 series를 선택하고 0번째 layer를 선택한다.

        Args:
            idx_new (int): 선택할 시리즈의 index 
        """
        new_series = self.get_series_at(self.layers.value, idx_new)
        self.current_series.set_value(new_series)
        self.index_layer.set_value(0)
    
    def on_layer_index_change(self, index):
        """
        주어진 index 위치의 layer를 선택한다.

        Args:
            index (int): 선택하고자 하는 layer의 index
        """
        self.index_layer.set_value(index)
        
    def on_layer_drag(self, pos_world):
        """
        현재 layer 위에 drag가 감지되면 종양 경계를 연장한다.

        Args:
            pos_world (list[float]): drag 시 커서가 가리키는 실세계 좌표 [x, y, z]
        """
        series = self.current_series.value
        index = self.index_layer.value
        if self.is_valid_selection(series, index):          # 현재 layer 선택이 유효한지 검증한다.
            self.backup_undo()                              # 경계를 연장하기 전에 현재 상태를 undo stack에 백업한다.
            points = self.layers.value[series][index].path
            if len(points) == 0:
                points.append(pos_world)                    # 종양 경계를 연장한다. (첫 경계점)
            else:
                last_point = np.array(points[-1])           # 경계점 간 간격은 0.1mm 이상으로 한다.
                new_point = np.array(pos_world)
                if np.linalg.norm(new_point - last_point) >= 0.1:
                    points.append(pos_world)                # 종양 경계를 연장한다. (n번째 경계점)
            self.index_layer.publish()

    def on_layer_hover(self, pos_world):
        """
        Hovering이 감지되면 현재 world position 값을 업데이트한다.

        Args:
            pos_world (list[float]): Hovering 된 좌표에 대응하는 실세계 좌표
        """
        self.current_world_position.set_value(pos_world)

    def on_layer_scroll_by(self, offset):
        """
        offset만큼 index가 다른 layer를 선택하려는 의도가 감지되면 해당 layer를 선택한다.

        Args:
            offset (int): 이 값만큼 index를 변경한다.
        """
        series = self.current_series.value
        if series is None:
            return
        index = self.index_layer.value
        if self.is_valid_selection(series, index + offset):     # index를 offset만큼 이동했을 때 유효 범위인지 검사한다.
            self.index_layer.set_value(index + offset)          # 유효 범위이므로 offset만큼 이동한다.
        else:
            index_tip = len(self.layers.value[series]) - 1 if (offset > 0) else 0    # 유효하지 않으면 범위 내로 clamping 한다.
            self.index_layer.set_value(index_tip)

    def on_layer_scroll_to(self, new_index):
        """
        주어진 index에 있는 layer를 선택하려는 의도가 감지되면 해당 layer를 선택한다.

        Args:
            new_index (int): 새로운 layer index
        """
        series = self.current_series.value
        if self.is_valid_selection(series, new_index):
            self.index_layer.set_value(new_index)

    def on_layer_scroll_to_end(self):
        """
        마지막 layer를 선택하려는 의도가 감지되면 해당 layer를 선택한다.
        """
        series = self.current_series.value
        index_last = len(self.layers.value[series]) - 1
        self.index_layer.set_value(index_last)

    def on_reconstruct_click(self):
        """
        Build 메뉴 클릭 시 종양의 point cloud로부터 종양의 곡면(mesh)을 계산한다.
        """
        try:
            self.reconstruct_surface()
        except Exception as e:
            print(str(e))

    def on_new_project_click(self):
        """
        새 프로젝트 메뉴가 클릭되면 유저의 의사를 재확인한다.
        """
        if len(self.layers.value) > 0:
            self.event.emit(ConfirmNewFile())
        else:
            self.clean_up_state()

    def on_new_project_confirm(self):
        """
        유저의 의사가 확인되면 프로젝트 상태(state)를 clean-up한다.
        """
        self.clean_up_state()

    def on_open_project_click(self):
        """
        파일 열기 메뉴가 클릭되면 파일 탐색기 이벤트를 발생시킨다.
        """
        self.event.emit(PromptOpenFile())

    def on_open_project_result(self, filename):
        """
        열고자 하는 프로젝트 파일(*.bts)이 선택되면 파일에 저장된 데이터를 불러온다.

        Args:
            filename (str): 열고자 하는 프로젝트 파일(*.bts)의 경로
        """
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            self.set_current_state(data)
            try:
                self.reconstruct_surface()
            except Exception as e:
                print(str(e))
            self.current_filename.set_value(filename)
        except IOError as e:
            print(str(e))
            self.event.emit(ShowMessage('Could not open the file'))

    def on_save_project_click(self):
        """
        프로젝트 저장이 클릭되면 파일 탐색기 이벤트를 발생시킨다.
        """
        if len(self.layers.value) > 0:
            self.event.emit(PromptSaveFile())
        else:
            self.event.emit(ShowMessage('There are no layers'))
        
    def on_save_project_result(self, filename):
        """
        저장할 파일 경로가 선택되면, 현재 프로젝트 상태를 프로젝트 파일(*.bts)로 저장한다.

        Args:
            filename (str): 저장할 파일 경로
        """
        data = self.get_current_state()
        try:
            with open(filename, 'wb') as file:
                pickle.dump(data, file)
            self.event.emit(ShowMessage('File saved'))
            self.current_filename.set_value(filename)
        except IOError as e:
            print(str(e))
            self.event.emit(ShowMessage('Could not save the file'))

    def on_exit_click(self):
        """
        프로그램 종료가 클릭되면 유저의 의사를 재확인한다.
        """
        self.event.emit(ConfirmExit())

    def on_exit_confirm(self):
        """
        유저의 의사가 확인되면 프로그램 종료 이벤트를 발생시킨다.
        """
        self.event.emit(TerminateApp())

    def on_clear_path_click(self):
        """
        Clear Path가 클릭되면 현재 layer에 마킹된 종양 경계를 삭제한다.
        """
        series = self.current_series.value
        index = self.index_layer.value
        if self.is_valid_selection(series, index):
            self.backup_undo()                          # 경계를 삭제하기 전에 현재 상태를 undo 스택에 백업한다.
            layer = self.layers.value[series][index]
            layer.path = []
            self.layers.publish()

    def on_undo_click(self):
        """
        Undo가 클릭되면 undo를 실행한다.
        """
        self.undo_state()

    def on_redo_click(self):
        """
        Redo가 클릭되면 redo를 실행한다.
        """
        self.redo_state()

    def on_export_model_click(self):
        """
        Export가 클릭된 경우 파일 탐색기 이벤트를 발생시킨다.
        """
        tumor = self.tumor_model_project.value
        if tumor is None:
            self.event.emit(ShowMessage('No model to export exists'))
            return
        if self.mesh.value is None:
            self.event.emit(ShowMessage('You must build model before exporting'))
            return
        self.event.emit(PromptExportModel())

    def on_export_model_result(self, filename):
        """
        Export할 경로가 정해지면 프로젝트 종양 모델(TumorModelData)을 파일(*.tmr)에 저장한다. 

        Args:
            filename (str): 저장할 파일의 경로
        """
        mesh = self.mesh.value
        layer = self.current_layer.value 
        if mesh is None or layer is None:   # mesh를 확인한 경우에만 export 허용
            self.event.emit(ShowMessage('No model to export exists'))
            return
        # TumorModelData를 구성하고 파일에 저장한다.
        points = self.extract_points()
        volume_avg = self.get_average_tumor_volume()
        model = TumorModelData(points, volume_avg, layer.study_date, layer.birth_date)
        try:
            with open(filename, 'wb') as file:
                pickle.dump(model, file)
            self.event.emit(ShowMessage('Model exported'))
        except IOError as e:
            print(str(e))
            self.event.emit(ShowMessage('Could not export the model'))

    def on_add_comparison_click(self):
        """
        Add Comparison이 클릭된 경우 외부 모델을 불러오는 파일 탐색기 이벤트를 발생시킨다.
        """
        self.event.emit(PromptOpenModels())

    def on_add_comparison_result(self, filenames):
        """
        외부 모델이 저장된 파일 경로(*.tmr)들이 정해지면 파일을 읽어 대조군에 종양 모델을 추가한다.

        Args:
            filenames (str): 외부 종양 모델들이 저장된 파일(*.tmr)의 경로
        """
        tumor_models_imported = []
        for filename in filenames:
            try:
                # 각 파일(*.tmr)을 읽어 TumorModelData를 구성하고 reconstruction을 통해 mesh를 계산한다.
                with open(filename, 'rb') as file:
                    tumor_model_data: TumorModelData = pickle.load(file)
                mesh = utils.O3dUtil.reconstruct_surface(tumor_model_data.points)
                # TumorModelData과 mesh로 TumorModel을 생성하고 리스트에 추가한다.
                tumor_models_imported.append(TumorModel.from_tumor_model_data(tumor_model_data, mesh))
            except IOError as e:
                print(str(e))
                self.event.emit(ShowMessage('Could not load a model'))
        # 리스트를 촬영일자 최신순으로 정렬하고 대조군으로 지정한다.
        tumor_models_imported = sorted(tumor_models_imported, key=lambda x: x.date, reverse=True)
        self.comparison_models.set_value(tumor_models_imported)

    def on_show_growth_pattern_click(self):
        """
        Show Growth Pattern이 클릭되면 ShowGrowthPattern 이벤트를 발생시킨다.
        """
        self.event.emit(ShowGrowthPattern(self.tumor_model_list.value))
    
    def on_tumor_model_selected(self, index):
        """
        클릭된 위치에 있는 종양 모델을 선택한다.

        Args:
            index (int): 종양 모델 리스트에서 클릭된 위치
        """
        self.tumor_model_index.set_value(index)

    def extract_points(self):
        """
        현재 선택된 Series의 종양 경계점들(point cloud)을 추출하여 리턴한다.

        Returns:
            list[float]: 종양 경계점들: [x0, y0, z0, x1, y1, z1, ...]
        """
        points = []
        for _, layer_list in self.layers.value.items():
            for layer in layer_list:
                for point in layer.path:
                    points.append(point)
        return points

    def reconstruct_surface(self):
        """
        현재 선택된 series의 종양 경계점들(point cloud)을 reconstruct하여 종양의 곡면(mesh)을 계산한다.
        """
        points = self.extract_points()
        if len(points) >= 10:
            mesh = utils.O3dUtil.reconstruct_surface(points)
            self.mesh.set_value(mesh)
        else:
            self.mesh.set_value(None)
            self.event.emit(ShowMessage('Not enough vertices to build a model'))

    def clean_up_state(self):
        """
        현재 프로젝트의 상태(state)를 초기화한다.
        """
        self.current_filename.set_value(None)
        self.current_series.set_value(None)
        self.index_layer.set_value(-1)
        self.layers.set_value(dict())
        self.mesh.set_value(None)
        self.comparison_models.set_value([])
        self.tumor_model_index.set_value(0)

    def delete_series(self, series):
        """
        현재 선택된 series를 삭제한다.

        Args:
            series (str): 삭제할 series의 제목
        """
        layers = self.layers.value
        series_index = list(self.layers.value.keys()).index(series)
        del layers[series]  # series 삭제
        if len(layers) == 0:
            # 새로 선택할 series가 없으면 선택을 무효값으로 한다.
            self.current_series.set_value(None)
            self.index_layer.set_value(-1)
            self.layers.set_value(dict())
            self.mesh.set_value(None)
        else:
            # 삭제에 의해 현재 index로 이동한 series를 선택하되, 범위를 벗어난 경우 마지막 series를 선택한다.
            if series_index == len(layers):
                series_index -= 1
            new_series = self.get_series_at(layers, series_index)
            self.current_series.set_value(new_series)
            self.index_layer.set_value(0)
            self.layers.publish()
            self.mesh.set_value(None)

    def get_current_state(self):
        """
          현재 프로젝트의 상태(state)를 리턴한다. undo, redo, serialization 등에 사용된다.
        """
        layers = self.layers.value
        layers_copy = dict()    # dict의 깊은 복사가 요구됨
        for series, layer_list in layers.items():
            layers_copy[series] = []
            for layer in layer_list:
                layers_copy[series].append(Layer.from_layer(layer))
        return {
            'layers': layers_copy,                      # 모든 layer 리스트
            'series': self.current_series.value,        # 현재 선택된 series 제목
            'index_layer': self.index_layer.value       # 현재 선택된 layer index
        }
    
    def set_current_state(self, state):
        """
        프로젝트 상태를 주어진 state로 설정한다. serialization, undo, redo 등에 사용된다.

        Args:
            state (tuple): 설정할 프로젝트 상태: (layers, current_series, index_layer)
        """
        self.current_series.set_value(state['series'])
        self.index_layer.set_value(state['index_layer'])
        self.layers.set_value(state['layers'])

    def backup_undo(self):
        """
        undo 스택에 현재 상태를 백업한다.
        """
        self.undo_stack.append(self.get_current_state())

    def undo_state(self):
        """
        현재 상태를 redo 스택에 저장한 후 undo 한다.
        """
        if len(self.undo_stack) > 0:
            prev_state = self.undo_stack.pop()
            self.redo_stack.append(self.get_current_state())
            self.set_current_state(prev_state)

    def redo_state(self):
        """
        현재 상태를 undo 스택에 저장한 후 redo 한다.
        """
        if len(self.redo_stack) > 0:
            prev_state = self.redo_stack.pop()
            self.undo_stack.append(self.get_current_state())
            self.set_current_state(prev_state)

    def get_series_tumor_volume(self, series):
        """
        주어진 series의 종양 경계점들이 형성하는 곡면의 내부 부피(mm3)를 계산한다.

        Args:
            series (str): 종양의 부피(mm3)를 계산할 series의 제목

        Returns:
            float: 계산된 종양의 부피(mm3)
        """
        volume = 0
        if series in self.layers.value:
            layer_list = self.layers.value[series]
            layer_prev = None
            for layer in layer_list:
                # 각 layer의 종양 경계면의 면적을 구분구적법으로 누적하여 부피를 계산한다.
                if layer_prev is not None:
                    dh = layer_prev.get_distance(layer)
                    volume += layer.get_area() * dh
                layer_prev = layer
        return volume
    
    def get_average_tumor_volume(self):
        """
        모든 series에서 계산된 종양 부피의 평균(mm3)을 계산한다.

        Returns:
            float: 종양 부피의 평균(mm3)
        """
        volumes = []
        for series in self.layers.value:
            volume = self.get_series_tumor_volume(series)
            if volume > 0:
                volumes.append(volume)
        return sum(volumes) / len(volumes) if len(volumes) > 0 else 0
