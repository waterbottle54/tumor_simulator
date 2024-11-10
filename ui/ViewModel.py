from PyQt5.QtCore import QObject, pyqtSignal
from datetime import date
from data.common.LiveData import *
from data.Layer import *
from data.Tumor import *
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

    event = pyqtSignal(Event)
    current_filename = MutableLiveData(None)
    current_world_position = MutableLiveData(None)

    layer_map: MutableLiveData = MutableLiveData(dict())
    series: MutableLiveData = MutableLiveData(None)
    position: MutableLiveData = MutableLiveData(0)
    layer: LiveData
    series_description: LiveData

    area: LiveData
    volume: LiveData
    mesh: MutableLiveData = MutableLiveData(None)

    tumor_model: LiveData
    comparison_models: MutableLiveData = MutableLiveData([])
    tumor_model_list: LiveData
    tumor_model_index: MutableLiveData = MutableLiveData(0)
    current_tumor_model: LiveData

    undo_stack = []
    redo_stack = []
    
    def __init__(self):
        super().__init__()

        self.layer = map3(
                    self.layer_map, self.series, self.position,
                    lambda layer_map, series, position: layer_map[series][position] 
                    if self.is_valid_selection(series, position) else None)

        self.series_description = map3(self.series, self.layer_map, self.position, 
                                       lambda series, layer_map, position: (series, len(layer_map[series]), position)
                                       if series is not None and series in layer_map else None)

        self.area = map(self.layer, lambda layer: layer.get_area() if layer is not None else 0)

        self.volume = map3(self.layer_map, self.series, self.position, lambda _, series, __: self.get_series_volume(series))

        self.tumor_model = map3(self.mesh, self.volume, self.layer,
                            lambda mesh, _, layer: TumorModel(mesh, self.get_average_volume(), layer.study_date, layer.birth_date)
                            if layer is not None else TumorModel(None, 0, date.today(), None))

        self.tumor_model_list = map2(self.tumor_model, self.comparison_models,
                                lambda tumor_model, comparison_models: [tumor_model] + comparison_models)
        
        self.current_tumor_model = map2(self.tumor_model_list, self.tumor_model_index,
                                    lambda tumor_list, index: tumor_list[index] if 0 <= index < len(tumor_list) else None)

    def is_valid_selection(self, series, position):
        layer_map = self.layer_map.value
        return series in layer_map and 0 <= position < len(layer_map[series])

    def get_series_at(self, index):
        return list(self.layer_map.value.keys())[index]
    
    def get_series_index(self, series):
        return list(self.layer_map.value.keys()).index(series)

    def on_import_click(self):
        self.event.emit(PromptDicomFiles())

    def on_import_result(self, filenames):
        if len(filenames) > 0:
            self.event.emit(ShowMessage('Importing may take 1~2 minutes'))
        else:
            self.event.emit(ShowMessage('Select a folder that directly contains DICOM files'))
            return

        layer_map = self.layer_map.value
        for filename in filenames:
            try:
                layer = Layer.from_dicom_file(filename)
            except Exception as e: 
                logging.basicConfig(filename='error.log', level=logging.DEBUG)
                logging.error(f'on_import_result: {str(e)}')
                print(str(e))
                continue
            series = layer.series
            if layer.series in layer_map:
                layer_map[series].append(layer)
            else:
                layer_map[series] = [layer]

        if len(layer_map) > 0:
            self.layer_map.publish()
            first_series = self.get_series_at(0)
            self.series.set_value(first_series)
            if len(layer_map[first_series]) > 0:
                self.position.set_value(0)

    def on_delete_layer_click(self):
        layer_map = self.layer_map.value
        series = self.series.value
        position = self.position.value
        if self.is_valid_selection(series, position):
            self.backup_undo()
            layer_map[series].pop(position)
            if len(layer_map[series]) == 0:
                self.delete_series(series)
            elif position == len(layer_map[series]):
                self.position.set_value(position - 1)
            self.layer_map.publish()

    def on_delete_series_click(self):
        series = self.series.value
        if series in self.layer_map.value:
            layer_list = self.layer_map.value[series]
            any_points = False
            for layer in layer_list:
                if len(layer.path) > 0:
                    any_points = True
                    break;
            self.event.emit(ConfirmDeleteSeries(series, any_points))

    def on_delete_series_confirm(self, series):
        if series in self.layer_map.value:
            self.backup_undo()
            self.delete_series(series)

    def on_series_change(self, series_index):
        new_series = self.get_series_at(series_index)
        self.series.set_value(new_series)
        self.position.set_value(0)
    
    def on_position_change(self, position):
        self.position.set_value(position)
        
    def on_layer_drag(self, pos_world):
        series = self.series.value
        position = self.position.value
        if self.is_valid_selection(series, position):
            self.backup_undo()
            points = self.layer_map.value[series][position].path
            if len(points) == 0:
                points.append(pos_world)
            else:
                last_point = np.array(points[-1])
                new_point = np.array(pos_world)
                if np.linalg.norm(new_point - last_point) >= 0.1:
                    points.append(pos_world)
            self.position.publish()

    def on_layer_hover(self, pos_world):
        self.current_world_position.set_value(pos_world)

    def on_layer_scroll_by(self, offset):
        series = self.series.value
        position = self.position.value
        if self.is_valid_selection(series, position + offset):
            self.position.set_value(position + offset)
        else:
            end_position = len(self.layer_map.value[series]) - 1 if offset > 0 else 0
            self.position.set_value(end_position)

    def on_layer_scroll_to(self, p):
        series = self.series.value
        if self.is_valid_selection(series, p):
            self.position.set_value(p)

    def on_layer_scroll_to_end(self):
        series = self.series.value
        end_position = len(self.layer_map.value[series]) - 1
        self.position.set_value(end_position)

    def on_reconstruct_click(self):
        self.reconstruct_surface()

    def on_new_click(self):
        if len(self.layer_map.value) > 0:
            self.event.emit(ConfirmNewFile())
        else:
            self.clean_up()

    def on_new_confirm(self):
        self.clean_up()

    def on_open_click(self):
        self.event.emit(PromptOpenFile())

    def on_open_result(self, filename):
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            self.set_current_state(data)
            self.reconstruct_surface()
            self.current_filename.set_value(filename)
        except IOError as e:
            print(str(e))
            self.event.emit(ShowMessage('Could not open the file'))

    def on_save_click(self):
        if len(self.layer_map.value) > 0:
            self.event.emit(PromptSaveFile())
        else:
            self.event.emit(ShowMessage('There are no layers'))
        
    def on_save_result(self, filename):
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
        self.event.emit(ConfirmExit())

    def on_exit_confirm(self):
        self.event.emit(TerminateApp())

    def on_clear_path_click(self):
        series = self.series.value
        position = self.position.value
        if self.is_valid_selection(series, position):
            self.backup_undo()
            layer = self.layer_map.value[series][position]
            layer.path = []
            self.layer_map.publish()

    def on_undo_click(self):
        self.undo_state()

    def on_redo_click(self):
        self.redo_state()

    def on_export_click(self):
        tumor = self.tumor_model.value
        if tumor is None:
            self.event.emit(ShowMessage('No model to export exists'))
            return
        if self.mesh.value is None:
            self.event.emit(ShowMessage('You must build model before exporting'))
            return
        self.event.emit(PromptExportModel())

    def on_export_result(self, filename):
        mesh = self.mesh.value
        layer = self.layer.value
        if mesh is None or layer is None:
            self.event.emit(ShowMessage('No model to export exists'))
            return
        points = self.extract_points()
        volume_avg = self.get_average_volume()
        model = TumorModelData(points, volume_avg, layer.study_date, layer.birth_date)
        try:
            with open(filename, 'wb') as file:
                pickle.dump(model, file)
            self.event.emit(ShowMessage('Model exported'))
        except IOError as e:
            print(str(e))
            self.event.emit(ShowMessage('Could not export the model'))

    def on_add_comparison_click(self):
        self.event.emit(PromptOpenModels())

    def on_add_comparison_result(self, filenames):
        tumor_models = []
        for filename in filenames:
            try:
                with open(filename, 'rb') as file:
                    tumor_model_data: TumorModelData = pickle.load(file)
                mesh = O3dUtil.reconstruct_surface(tumor_model_data.points)
                tumor_models.append(TumorModel.from_tumor_model_data(tumor_model_data, mesh))
            except IOError as e:
                print(str(e))
                self.event.emit(ShowMessage('Could not load a model'))
        tumor_models = sorted(tumor_models, key=lambda x: x.date, reverse=True)
        self.comparison_models.set_value(tumor_models)

    def on_show_growth_click(self):
        self.event.emit(ShowGrowthPattern(self.tumor_model_list.value))
    
    def on_model_selected(self, i):
        self.tumor_model_index.set_value(i)

    def extract_points(self):
        points = []
        for _, layer_list in self.layer_map.value.items():
            for layer in layer_list:
                for point in layer.path:
                    points.append(point)
        return points

    def reconstruct_surface(self):
        # extract all points
        points = self.extract_points()
        # build mesh object
        if len(points) >= 10:
            mesh = O3dUtil.reconstruct_surface(points)
            self.mesh.set_value(mesh)
        else:
            self.mesh.set_value(None)
            self.event.emit(ShowMessage('Not enough vertices to build a model'))

    def clean_up(self):
        self.current_filename.set_value(None)
        self.series.set_value(None)
        self.position.set_value(-1)
        self.layer_map.set_value(dict())
        self.mesh.set_value(None)
        self.comparison_models.set_value([])
        self.tumor_model_index.set_value(0)

    def delete_series(self, series):
        layer_map = self.layer_map.value
        series_index = self.get_series_index(series)
        del layer_map[series]
        if len(layer_map) == 0:
            self.series.set_value(None)
            self.position.set_value(-1)
        else:
            if series_index == len(layer_map):
                series_index -= 1
            new_series = self.get_series_at(series_index)
            self.series.set_value(new_series)
            self.position.set_value(0)
        self.layer_map.publish()
        self.mesh.set_value(None)

    def get_current_state(self):
        layer_map = self.layer_map.value
        layer_map_copy = dict()
        for series, layer_list in layer_map.items():
            layer_map_copy[series] = []
            for layer in layer_list:
                layer_map_copy[series].append(Layer.from_layer(layer))
        return {
            'layer_map': layer_map_copy,
            'series': self.series.value,
            'position': self.position.value
        }
    
    def set_current_state(self, state):
        self.series.set_value(state['series'])
        self.position.set_value(state['position'])
        self.layer_map.set_value(state['layer_map'])

    def backup_undo(self):
        self.undo_stack.append(self.get_current_state())

    def undo_state(self):
        if len(self.undo_stack) > 0:
            prev_state = self.undo_stack.pop()
            self.redo_stack.append(self.get_current_state())
            self.set_current_state(prev_state)

    def redo_state(self):
        if len(self.redo_stack) > 0:
            prev_state = self.redo_stack.pop()
            self.undo_stack.append(self.get_current_state())
            self.set_current_state(prev_state)

    def get_series_volume(self, series):
        volume = 0
        if series in self.layer_map.value:
            layer_list = self.layer_map.value[series]
            layer_prev = None
            for layer in layer_list:
                if layer_prev is not None:
                    dh = layer_prev.get_distance(layer)
                    volume += layer.get_area() * dh
                layer_prev = layer
        return volume
    
    def get_average_volume(self):
        volumes = []
        for series in self.layer_map.value:
            volume = self.get_series_volume(series)
            if volume > 0:
                volumes.append(volume)
        return sum(volumes) / len(volumes) if len(volumes) > 0 else 0
