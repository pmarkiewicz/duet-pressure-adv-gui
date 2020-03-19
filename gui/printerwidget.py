from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QFileDialog, QPushButton, 
                            QVBoxLayout, QGroupBox, QGridLayout, QMessageBox, QLabel,
                            QDoubleSpinBox)


class PrinterWidget(QGroupBox):
    def __init__(self, title, cfg, parent=None):
        super().__init__(title, parent=parent)
        
        self.cfg = cfg
        self.initUI()
    
    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel('ip_addr'), 1, 0)
        self.ip_addr = QLineEdit()
        grid.addWidget(self.ip_addr, 1, 1)

        grid.addWidget(QLabel('pwd'), 2, 0)
        self.pwd = QLineEdit()
        grid.addWidget(self.pwd, 2, 1)

        # grid.addWidget(QLabel('name'), 3, 0)
        # self.name = QLineEdit()
        # grid.addWidget(self.name, 3, 1)

        grid.addWidget(QLabel('nozzle_dia'), 4, 0)
        self.nozzle_dia = QDoubleSpinBox()
        self.nozzle_dia.setRange(0.2, 2)
        self.nozzle_dia.setDecimals(2)
        self.nozzle_dia.setSingleStep(0.05)
        self.nozzle_dia.setSuffix(' [mm]')
        self.nozzle_dia.setValue(self.cfg.nozzle_dia)
        grid.addWidget(self.nozzle_dia, 4, 1)

        grid.addWidget(QLabel('start_x'), 5, 0)
        self.start_x = self.setup_pos(self.cfg.start_x)
        grid.addWidget(self.start_x, 5, 1)

        grid.addWidget(QLabel('start_y'), 6, 0)
        self.start_y = self.setup_pos(self.cfg.start_y)
        grid.addWidget(self.start_y, 6, 1)

        grid.addWidget(QLabel('object_width'), 7, 0)
        self.object_width = self.setup_pos(self.cfg.object_width)
        grid.addWidget(self.object_width, 7, 1)

        self.setLayout(grid)

    def setup_pos(self, value):
        widget = QDoubleSpinBox()
        widget.setRange(0, 1000)
        widget.setDecimals(2)
        widget.setSingleStep(5)
        widget.setSuffix(' [mm]')
        widget.setValue(value)

        return widget
