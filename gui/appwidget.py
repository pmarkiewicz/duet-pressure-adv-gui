from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QFileDialog, QPushButton, 
                            QVBoxLayout, QGroupBox, QGridLayout, QMessageBox, QLabel, 
                            QTabWidget, QButtonGroup, QFileDialog)

from .filewidget import FileOpenWidget, FileSaveWidget

from .printerwidget import PrinterWidget
from .filamentwidget import FilamentWidget
from .testwidget import TestWidget
from .gcodewidget import GCodeWidget

class App(QWidget):

    def __init__(self, process_func, configurator):
        super().__init__()
        self.process_func = process_func

        self.configuration = configurator
        self.title = 'Pressure adv test'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 300
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        self.filamentwidget = FilamentWidget("F", self.configuration, self)
        self.printerwidget = PrinterWidget('P', self.configuration, self)
        self.testwidget = TestWidget('T', self.configuration, self)
        self.startcodewidget = GCodeWidget('GS', self.configuration.start_gcode, self)
        self.endcodewidget = GCodeWidget('GE', self.configuration.end_gcode, self)
        tabs = QTabWidget()
        tabs.addTab(self.testwidget, 'Test Cfg')
        tabs.addTab(self.filamentwidget, 'Filament Cfg')
        tabs.addTab(self.printerwidget, 'Printer Cfg')
        tabs.addTab(self.startcodewidget, 'Start GCode')
        tabs.addTab(self.endcodewidget, 'End GCode')

        layout.addWidget(tabs)


        buttons = QGroupBox('actions', self)
        bgrid = QGridLayout()
        bgrid.setSpacing(10)
        buttons.setLayout(bgrid)

        generate = QPushButton('Generate')
        generate.clicked.connect(self.createFile)
        bgrid.addWidget(generate, 1, 0)

        send = QPushButton('Send')
        send.clicked.connect(self.updateConfiguration)
        bgrid.addWidget(send, 1, 1)

        layout.addWidget(buttons)
        self.setLayout(layout)

        self.show()
    
    def updateConfiguration(self):
        self.filamentwidget.updateConfig(self.configuration)
        self.printerwidget.updateConfig(self.configuration)
        self.testwidget.updateConfig(self.configuration)
        self.startcodewidget.updateConfig(self.configuration, 'start_gcode')
        self.endcodewidget.updateConfig(self.configuration, 'end_gcode')

    def openFileSaveDialog(self):
        options = QFileDialog.Options()
        filter = "Excel Files (*.gcode);;All Files (*)"
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "", filter, options=options)
        
        return fileName

    def createFile(self):
        self.updateConfiguration()
        fileName = self.openFileSaveDialog()
        gcode = self.process_func(self.configuration)
        s = '\n'.join(gcode)
        with open(fileName, 'w') as f:
            f.write(s)

