import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QMessageBox, QFileDialog
from PyQt5.QtGui import QCloseEvent
from ui.ViewModel import *
from ui.layers.LayersFragment import *
from ui.rendering.RenderingFragment import *
from ui.dialogs.ChartDialog import *
from ui.dialogs.AboutDialog import *
from ui.dialogs.TipsDialog import *

class MainWindow(QMainWindow):
    """
    프로그램의 메인 윈도우. 
    
    - 화면은 layer fragment, rendering fragment 로 구성된다.
      대부분의 기능이 fragment에 구현되어 있다. (상세: 각 class doc)
    - menubar, toolbar, status bar를 가지며 뷰모델과 연동한다.

    Attributes:
        view_model(ViewModel): 뷰모델 (poject-level)
        layout_top(QHBoxLayout): 최상위 레이아웃
        layers_fragment(LayersFragment): Layer 탐색 및 편집 UI - 화면 좌측
        rendering_fragment(RenderingFragment): 3D Tumor 렌더링 UI - 화면 우측

    Methods:
        setup_menu: 메뉴를 초기화한다. (계층도는 함수 doc 참조)
        setup_toolbar: 툴바를 초기화한다.
        on_event: 뷰모델의 이벤트를 처리한다.
        closeEvent: 메인 윈도우 닫기 이벤트를 intercept해서 뷰모델에 전달한다.
        update_status_bar: 마우스의 위치에 대응되는 실세계 좌표를 메인 윈도우 하단의 status bar에 표시한다.
        update_title_bar: 메인 윈도우의 title bar에 현재 프로젝트 파일명을 표시한다.
        show_tips: 사용법 및 주의사항이 담긴 대화상자를 띄운다.
        show_about: 프로그램 및 저작권 정보가 담긴 대화상자를 띄운다.
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Brain Tumor Simulator')
        self.setWindowIcon(QIcon('icons/render.png'))
        self.setGeometry(0, 0, 1200, 800)
        
        # 뷰모델(project-level)과 최상위 레이아웃을 생성한다.
        self.view_model = ViewModel()
        self.layout_top = QHBoxLayout()
        
        widget = QWidget()
        widget.setLayout(self.layout_top)
        self.setCentralWidget(widget)

        # Dropdown 메뉴와 툴바를 초기화한다.
        self.setup_menu()
        self.setup_toolbar()

        # LayersFragment를 생성하고 화면 좌측에 배치한다.
        self.layers_fragment = LayersFragment(self.view_model)
        self.layout_top.addWidget(self.layers_fragment)

        # RenderingFragment를 생성하고 화면 우측에 배치한다.
        self.rendering_fragment = RenderingFragment(self.view_model)
        self.layout_top.addWidget(self.rendering_fragment)

        # 뷰모델이 보낸 이벤트를 처리하고, UI(title bar, status bar)를 연결한다.
        self.view_model.event.connect(self.on_event)
        self.view_model.current_filename.observe(self.update_title_bar)
        self.view_model.current_world_position.observe(self.update_status_bar)

    def setup_menu(self):
        """
        메뉴를 초기화한다. 아래는 메뉴의 계층도와 동작이다.
        Initialize menus. Below is the hierarchy and actions of the menus.
        - 1. File
            └ New File              : 새로운 프로젝트 파일(*.bts) 생성
            └ Open File             : 기존의 프로젝트 파일(*.bts) 열기
            └ Save File             : 현재 프로젝트 파일(*.bts) 저장
            └ Exit                  : 현재 프로젝트 및 프로그램 종료
        - 2. Edit
            └ Import DICOM Folder   : dicom(*.dat)파일을 직접 포함하는 폴더로부터 dicom 데이터 불러오기
            └ Delete Layer          : 현재 관찰중인 Layer 제거하기
            └ Delete Series         : 현재 관찰중인 Series(e.g. Gd Enhanced Axial) 제거하기
            └ Undo                  : 이전 상태로 되돌리기
            └ Redo                  : 다음 상태로 다시 되돌리기
            └ Clear Path            : 마킹된 종양 경계 지우기
        - 3. Build
            └ Build Tumor Model     : 종양 3D 모델 연산 후 RenderingFragment에 표시하기
            └ Export Tumor Model    : 현재 종양 3D 모델을 (*.tmr)로 export하기
            └ Show Growth Pattern   : 시간대순으로 대조군과 현재 종양의 성장 패턴 표시하기
        - 4. Help 
            └ Tips                  : 사용법, 주의사항
            └ About                 : 프로그램 및 저작권 정보
        """

        menu_bar = self.menuBar()

        # Top-level menus
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        build_menu = menu_bar.addMenu("Build")
        analyze_menu = menu_bar.addMenu("Analyze")
        help_menu = menu_bar.addMenu("Help")

        # 1. File menus

        action_new = QAction("New File", self)
        action_new.triggered.connect(self.view_model.on_new_project_click)
        action_new.setShortcut('Ctrl+N')
        file_menu.addAction(action_new)

        action_open = QAction("Open File", self)
        action_open.triggered.connect(self.view_model.on_open_project_click)
        action_open.setShortcut('Ctrl+O')
        file_menu.addAction(action_open)

        action_save = QAction("Save File", self)
        action_save.triggered.connect(self.view_model.on_save_project_click)
        action_save.setShortcut('Ctrl+S')
        file_menu.addAction(action_save)

        file_menu.addSeparator()

        action_exit = QAction("Exit", self)
        action_exit.triggered.connect(self.view_model.on_exit_click)
        file_menu.addAction(action_exit)

        # 2. Edit menus

        action_import = QAction("Import DICOM Folder", self)
        action_import.triggered.connect(self.view_model.on_import_dicom_click)
        action_import.setShortcut('Insert')
        edit_menu.addAction(action_import)

        edit_menu.addSeparator()

        action_delete_layer = QAction("Delete Layer", self)
        action_delete_layer.triggered.connect(self.view_model.on_delete_layer_click)
        action_delete_layer.setShortcut('Ctrl+Del')
        edit_menu.addAction(action_delete_layer)

        action_delete_series = QAction("Delete Series", self)
        action_delete_series.triggered.connect(self.view_model.on_delete_series_click)
        action_delete_series.setShortcut('Shift+Del')
        edit_menu.addAction(action_delete_series)

        edit_menu.addSeparator()

        action_undo = QAction("Undo", self)
        action_undo.triggered.connect(self.view_model.on_undo_click)
        action_undo.setShortcut('Ctrl+Z')
        edit_menu.addAction(action_undo)

        action_redo = QAction("Redo", self)
        action_redo.triggered.connect(self.view_model.on_redo_click)
        action_redo.setShortcut('Ctrl+Y')
        edit_menu.addAction(action_redo)

        edit_menu.addSeparator()

        action_clear = QAction("Clear Path", self)
        action_clear.triggered.connect(self.view_model.on_clear_path_click)
        action_clear.setShortcut('Delete')
        edit_menu.addAction(action_clear)

        # Build(Model) menus

        action_reconstruct = QAction("Build Tumor Model", self)
        action_reconstruct.triggered.connect(self.view_model.on_reconstruct_click)
        action_reconstruct.setShortcut('Ctrl+B')
        build_menu.addAction(action_reconstruct)

        action_export = QAction("Export Tumor Model (.tmr files)", self)
        action_export.triggered.connect(self.view_model.on_export_model_click)
        action_export.setShortcut('Ctrl+E')
        build_menu.addAction(action_export)

        action_add_comparison = QAction("Set Comparison Models (.tmr files)", self)
        action_add_comparison.triggered.connect(self.view_model.on_add_comparison_click)
        action_add_comparison.setShortcut('Ctrl+A')
        analyze_menu.addAction(action_add_comparison)

        action_growth = QAction("Show Growth Pattern", self)
        action_growth.triggered.connect(self.view_model.on_show_growth_pattern_click)
        action_growth.setShortcut('Ctrl+G')
        analyze_menu.addAction(action_growth)

        # Help menus

        action_tips = QAction("Tips", self)
        action_tips.triggered.connect(self.show_tips)
        help_menu.addAction(action_tips)

        action_about = QAction("About", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)

    def setup_toolbar(self):
        """
        툴바를 초기화한다. 아래는 툴바 액션의 배치를 나타낸 것이다.

        || New File             | Open File     | Save File              |
        || Import DICOM Folder  | Delete Layer  | Delete Series          | Undo | Redo | Clear Path
        || Build Tumor          | Export Tumor  | *Set Comparison Models | **Show Growth Pattern

        *Set Comparison Models : 현재 종양과 대조할 대조군을 *.tmr 파일로부터 불러온다.
        **Show Growth Pattern : 현재 종양과 대조군의 시간 순 성장 패턴을 보여준다.
        """
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        action_new = QAction("New File", self, icon=QIcon("icons/new.png"))
        action_new.triggered.connect(self.view_model.on_new_project_click)
        self.toolbar.addAction(action_new)

        action_open = QAction("Open File", self, icon=QIcon("icons/open.png"))
        action_open.triggered.connect(self.view_model.on_open_project_click)
        self.toolbar.addAction(action_open)

        action_save = QAction("Save File", self, icon=QIcon("icons/save.png"))
        action_save.triggered.connect(self.view_model.on_save_project_click)
        self.toolbar.addAction(action_save)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        action_import = QAction("Import DICOM Folder", self, icon=QIcon("icons/import.png"))
        action_import.triggered.connect(self.view_model.on_import_dicom_click)
        self.toolbar.addAction(action_import)

        action_delete_layer = QAction("Delete Layer", self, icon=QIcon("icons/delete.png"))
        action_delete_layer.triggered.connect(self.view_model.on_delete_layer_click)
        self.toolbar.addAction(action_delete_layer)

        action_delete_series = QAction("Delete Series", self, icon=QIcon("icons/delete_all.png"))
        action_delete_series.triggered.connect(self.view_model.on_delete_series_click)
        self.toolbar.addAction(action_delete_series)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        action_undo = QAction("Undo", self, icon=QIcon("icons/undo.png"))
        action_undo.triggered.connect(self.view_model.on_undo_click)
        self.toolbar.addAction(action_undo)

        action_redo = QAction("Redo", self, icon=QIcon("icons/redo.png"))
        action_redo.triggered.connect(self.view_model.on_redo_click)
        self.toolbar.addAction(action_redo)

        action_clear_path = QAction("Clear Path", self, icon=QIcon("icons/clear.png"))
        action_clear_path.triggered.connect(self.view_model.on_clear_path_click)
        self.toolbar.addAction(action_clear_path)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        action_reconstruct = QAction("Build Tumor", self)
        action_reconstruct.setIcon(QIcon('icons/render.png'))
        action_reconstruct.triggered.connect(self.view_model.on_reconstruct_click)
        self.toolbar.addAction(action_reconstruct)

        action_export = QAction("Export Tumor", self)
        action_export.setIcon(QIcon('icons/export.png'))
        action_export.triggered.connect(self.view_model.on_export_model_click)
        self.toolbar.addAction(action_export)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        action_growth = QAction("Set Comparison Models", self)
        action_growth.setIcon(QIcon('icons/compare.png'))
        action_growth.triggered.connect(self.view_model.on_add_comparison_click)
        self.toolbar.addAction(action_growth)

        action_growth = QAction("Show Growth Pattern", self)
        action_growth.setIcon(QIcon('icons/chart.png'))
        action_growth.triggered.connect(self.view_model.on_show_growth_pattern_click)
        self.toolbar.addAction(action_growth)

    def on_event(self, event):
        """
        뷰모델의 이벤트를 처리한다.

        Args:
            event (ViewModel.Event): 뷰모델로부터 전달된 이벤트 객체
        """
        if isinstance(event, ShowMessage):
            # 문자열 내용이 포함된 메세지 박스를 띄운다.
            # display a message box that has text contents.
            QMessageBox.information(None, "", event.message)
        elif isinstance(event, PromptOpenFile):
            # 프로젝트 파일 열기 대화상자를 띄운다.
            # display a file dialog to open a project file.
            filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "BTS Files (*.bts)")
            if filename:
                self.view_model.on_open_project_result(filename)
        elif isinstance(event, PromptSaveFile):
            # 프로젝트 파일 저장하기 대화상자를 띄운다.
            # display a file dialog to save the current project file.
            filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "BTS Files (*.bts)")
            if filename:
                self.view_model.on_save_project_result(filename)
        elif isinstance(event, PromptDicomFiles):
            # dicom 데이터를 불러오기 위해 폴더 선택 대화상자를 띄운다. (폴더가 직접 .dat 파일을 포함해야 한다.)
            # show a folder browser to import dicom data from a selected folder (which has to contain *.dat files directly in it).
            folder_name = QFileDialog.getExistingDirectory(self, caption='Import DICOM Folder')
            if not folder_name:
                return
            filenames = []
            for filename in os.listdir(folder_name):
                path = f'{folder_name}/{filename}'
                if os.path.isfile(path):
                    filenames.append(path)
            self.view_model.on_import_dicom_result(filenames)
        elif isinstance(event, ConfirmNewFile):
            # 새 프로젝트 파일을 만들지 물어보는 대화상자를 띄운다.
            # show a message box to confirm whether or not the user wants to create a new project file.
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Question)
            message_box.setText("New File?")
            message_box.setWindowTitle("Confirmation")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            choice = message_box.exec_()
            if choice == QMessageBox.StandardButton.Yes:
                self.view_model.on_new_project_confirm()
        elif isinstance(event, ConfirmDeleteSeries):
            # 유저에게 series 삭제 여부를 묻는 대화상자를 띄운다.
            # show a message box to confirm whether or not the user wants to delete the requested series.
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Question)
            message = f"Delete {event.series} Series?"
            if event.any_point == True:
                message += "\nIt has contents in it!"
            message_box.setText(message)
            message_box.setWindowTitle("Confirmation")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            choice = message_box.exec_()
            if choice == QMessageBox.StandardButton.Yes:
                self.view_model.on_delete_series_confirm(event.series)
        elif isinstance(event, PromptExportModel):
            # 불러올 종양 모델 파일을 선택하는 대화상자를 띄운다.
            # show a file browser to prompt a tumor model file(*.tmr) to export.
            filename, _ = QFileDialog.getSaveFileName(self, "Export Model", "", "TMR Files (*.tmr)")
            if filename:
                self.view_model.on_export_model_result(filename)
        elif isinstance(event, PromptOpenModels):
            # 대조군을 형성할 종양 모델 파일들을 선택하는 대화상자를 띄운다.
            # show a file browser to prompt tumor models to be compared with the current one.
            filenames,  _ = QFileDialog.getOpenFileNames(self, "Set Comparison Models", "", "TMR Files (*.tmr)")
            if filenames:
                self.view_model.on_add_comparison_result(filenames)
        elif isinstance(event, ShowGrowthPattern):
            # 종양의 시계열적 성장 패턴 그래프를 보여주는 대화상자를 띄운다.
            # show a dialog that plots graphs on the time sequential growth pattern of the tumor models.
            dialog = ChartDialog(self, event.tumor_models)
            dialog.exec_()
        elif isinstance(event, ConfirmExit):
            # 유저에게 프로그램 종료 여부를 묻는 대화상자를 띄운다.
            # show a dialog to confirm whether or not the user wants to terminate the application.
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Question)
            message = f"Terminate the application?"
            message_box.setText(message)
            message_box.setWindowTitle("Confirmation")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            choice = message_box.exec_()
            if choice == QMessageBox.StandardButton.Yes:
                self.view_model.on_exit_confirm()
        elif isinstance(event, TerminateApp):
            # 프로그램을 종료한다.
            # terminate the application.
            QApplication.quit()

    def closeEvent(self, a0: QCloseEvent) -> None:
        """
        메인 윈도우 닫기 이벤트를 intercept 해서 뷰모델에 전달한다.

        Args:
            a0 (QCloseEvent): 윈도우 닫기 이벤트 객체
        """
        a0.ignore()
        self.view_model.on_exit_click()

    def update_status_bar(self, pos_world):
        """
        마우스의 위치에 대응되는 실세계 좌표를 메인 윈도우 하단의 status bar에 표시한다.

        Args:
            pos_world (list[float]): 실세계 좌표: [x, y, z]
        """
        if pos_world is not None:
            x, y, z = pos_world
            self.statusBar().showMessage(f'({int(x)}, {int(y)}, {int(z)})')
    
    def update_title_bar(self, filename):
        """
        메인 윈도우의 title bar에 현재 프로젝트 파일명을 표시한다.

        Args:
            filename (str): 현재 프로젝트 파일명
        """
        if filename is not None:
            self.setWindowTitle(f'Brain Tumor Simulator ({filename})')
        else:
            self.setWindowTitle(f'Brain Tumor Simulator')

    def show_tips(self):
        """
        사용법 및 주의사항이 담긴 대화상자를 띄운다.
        """
        dialog = TipsDialog()
        dialog.exec_()

    def show_about(self):
        """
        프로그램 및 저작권 정보가 담긴 대화상자를 띄운다.
        """
        dialog = AboutDialog()
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
