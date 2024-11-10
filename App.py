import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QMessageBox, QFileDialog
from PyQt5.QtGui import QCloseEvent
from ViewModel import *
from LayersFragment import *
from RenderingFragment import *
from ChartDialog import *
from AboutDialog import *
from TipsDialog import *

class MainWindow(QMainWindow):

    view_model: ViewModel
    layout: QHBoxLayout
    mri_fragment: LayersFragment
    rendering_fragment: RenderingFragment
    toolbar: QToolBar

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Brain Tumor Simulator')
        self.setWindowIcon(QIcon('icons/render.png'))
        self.setGeometry(0, 0, 1200, 800)
        
        self.view_model = ViewModel()
        self.layout = QHBoxLayout()
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.setup_menu()
        self.setup_toolbar()

        self.mri_fragment = LayersFragment(self.view_model)
        self.layout.addWidget(self.mri_fragment)

        self.rendering_fragment = RenderingFragment(self.view_model)
        self.layout.addWidget(self.rendering_fragment)

        self.view_model.event.connect(self.on_event)
        self.view_model.current_filename.observe(self.update_title_bar)
        self.view_model.current_world_position.observe(self.update_status_bar)

    def setup_menu(self):

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        build_menu = menu_bar.addMenu("Build")
        analyze_menu = menu_bar.addMenu("Analyze")
        help_menu = menu_bar.addMenu("Help")

        action_new = QAction("New File", self)
        action_new.triggered.connect(self.view_model.on_new_click)
        action_new.setShortcut('Ctrl+N')
        file_menu.addAction(action_new)

        action_open = QAction("Open File", self)
        action_open.triggered.connect(self.view_model.on_open_click)
        action_open.setShortcut('Ctrl+O')
        file_menu.addAction(action_open)

        action_save = QAction("Save File", self)
        action_save.triggered.connect(self.view_model.on_save_click)
        action_save.setShortcut('Ctrl+S')
        file_menu.addAction(action_save)

        file_menu.addSeparator()

        action_exit = QAction("Exit", self)
        action_exit.triggered.connect(self.view_model.on_exit_click)
        file_menu.addAction(action_exit)

        action_import = QAction("Import DICOM Folder", self)
        action_import.triggered.connect(self.view_model.on_import_click)
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

        action_reconstruct = QAction("Build Tumor Model", self)
        action_reconstruct.triggered.connect(self.view_model.on_reconstruct_click)
        action_reconstruct.setShortcut('Ctrl+B')
        build_menu.addAction(action_reconstruct)

        action_export = QAction("Export Tumor Model (.tmr Files)", self)
        action_export.triggered.connect(self.view_model.on_export_click)
        action_export.setShortcut('Ctrl+E')
        build_menu.addAction(action_export)

        action_add_comparison = QAction("Set Comparison Models (.tmr Files)", self)
        action_add_comparison.triggered.connect(self.view_model.on_add_comparison_click)
        action_add_comparison.setShortcut('Ctrl+A')
        analyze_menu.addAction(action_add_comparison)

        action_growth = QAction("Show Growth Pattern", self)
        action_growth.triggered.connect(self.view_model.on_show_growth_click)
        action_growth.setShortcut('Ctrl+G')
        analyze_menu.addAction(action_growth)

        action_tips = QAction("Tips", self)
        action_tips.triggered.connect(self.show_tips)
        help_menu.addAction(action_tips)

        action_about = QAction("About", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)

    def setup_toolbar(self):
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        action_new = QAction("New File", self, icon=QIcon("icons/new.png"))
        action_new.triggered.connect(self.view_model.on_new_click)
        self.toolbar.addAction(action_new)

        action_open = QAction("Open File", self, icon=QIcon("icons/open.png"))
        action_open.triggered.connect(self.view_model.on_open_click)
        self.toolbar.addAction(action_open)

        action_save = QAction("Save File", self, icon=QIcon("icons/save.png"))
        action_save.triggered.connect(self.view_model.on_save_click)
        self.toolbar.addAction(action_save)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        action_import = QAction("Import DICOM Folder", self, icon=QIcon("icons/import.png"))
        action_import.triggered.connect(self.view_model.on_import_click)
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
        action_export.triggered.connect(self.view_model.on_export_click)
        self.toolbar.addAction(action_export)

        self.toolbar.addSeparator()
        self.toolbar.addSeparator()

        action_growth = QAction("Set Comparison Models", self)
        action_growth.setIcon(QIcon('icons/compare.png'))
        action_growth.triggered.connect(self.view_model.on_add_comparison_click)
        self.toolbar.addAction(action_growth)

        action_growth = QAction("Show Growth Pattern", self)
        action_growth.setIcon(QIcon('icons/chart.png'))
        action_growth.triggered.connect(self.view_model.on_show_growth_click)
        self.toolbar.addAction(action_growth)

    def on_event(self, event):
        if isinstance(event, ShowMessage):
            # display message box
            QMessageBox.information(None, "", event.message)
        elif isinstance(event, PromptOpenFile):
            # display open file dialog
            filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "BTS Files (*.bts)")
            if filename:
                self.view_model.on_open_result(filename)
        elif isinstance(event, PromptSaveFile):
            # display save file dialog
            filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "BTS Files (*.bts)")
            if filename:
                self.view_model.on_save_result(filename)
        elif isinstance(event, PromptDicomFiles):
            folder_name = QFileDialog.getExistingDirectory(self, caption='Import DICOM Folder')
            if not folder_name:
                return
            filenames = []
            for filename in os.listdir(folder_name):
                path = f'{folder_name}/{filename}'
                if os.path.isfile(path):
                    filenames.append(path)
            self.view_model.on_import_result(filenames)
        elif isinstance(event, ConfirmNewFile):
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Question)
            message_box.setText("New File?")
            message_box.setWindowTitle("Confirmation")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            choice = message_box.exec_()
            if choice == QMessageBox.StandardButton.Yes:
                self.view_model.on_new_confirm()
        elif isinstance(event, ConfirmDeleteSeries):
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
            filename, _ = QFileDialog.getSaveFileName(self, "Export Model", "", "TMR Files (*.tmr)")
            if filename:
                self.view_model.on_export_result(filename)
        elif isinstance(event, PromptOpenModels):
            filenames,  _ = QFileDialog.getOpenFileNames(self, "Set Comparison Models", "", "TMR Files (*.tmr)")
            if filenames:
                self.view_model.on_add_comparison_result(filenames)
        elif isinstance(event, ShowGrowthPattern):
            dialog = ChartDialog(self, event.tumor_models)
            dialog.exec_()
        elif isinstance(event, ConfirmExit):
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
            QApplication.quit()

    def closeEvent(self, a0: QCloseEvent) -> None:
        a0.ignore()
        self.view_model.on_exit_click()

    def update_status_bar(self, pos_world):
        if pos_world is not None:
            x, y, z = pos_world
            self.statusBar().showMessage(f'({int(x)}, {int(y)}, {int(z)})')
    
    def update_title_bar(self, filename):
        if filename is not None:
            self.setWindowTitle(f'Brain Tumor Simulator ({filename})')
        else:
            self.setWindowTitle(f'Brain Tumor Simulator')

    def show_tips(self):
        dialog = TipsDialog()
        dialog.exec_()

    def show_about(self):
        dialog = AboutDialog()
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
