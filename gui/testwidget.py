from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QFileDialog, QPushButton, 
                            QVBoxLayout, QGroupBox, QGridLayout, QMessageBox, QLabel,
                            QCheckBox, QDoubleSpinBox, QSpinBox)


class TestWidget(QGroupBox):
    def __init__(self, title, cfg, parent=None):
        super().__init__(title, parent=parent)
        
        self.cfg = cfg
        self.initUI()
    
    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        # grid.addWidget(QLabel('Min vacation limit days'), 1, 0)
        # self.vacation = QLineEdit()
        # grid.addWidget(self.vacation, 1, 1)

        grid.addWidget(QLabel('layers'), 1, 0)
        self.layers = self.setup_num(self.cfg.layers, 10, 200, 5)
        grid.addWidget(self.layers, 1, 1)

        grid.addWidget(QLabel('pattern_width'), 2, 0)
        self.pattern_width = self.setup_width(self.cfg.pattern_width)
        grid.addWidget(self.pattern_width, 2, 1)

        grid.addWidget(QLabel('pressure_advance_min'), 3, 0)
        self.pressure_advance_min = self.setup_pressure_adv(self.cfg.pressure_advance_min)
        grid.addWidget(self.pressure_advance_min, 3, 1)

        grid.addWidget(QLabel('pressure_advance_max'), 4, 0)
        self.pressure_advance_max = self.setup_pressure_adv(self.cfg.pressure_advance_max)
        grid.addWidget(self.pressure_advance_max, 4, 1)

        grid.addWidget(QLabel('num_patterns'), 5, 0)
        self.num_patterns = self.setup_num(self.cfg.num_patterns, 1, 10, 1)
        grid.addWidget(self.num_patterns, 5, 1)

        grid.addWidget(QLabel('show_messages'), 6, 0)
        self.show_messages = QCheckBox()
        self.show_messages.setCheckState(self.cfg.show_messages)
        grid.addWidget(self.show_messages, 6, 1)

        self.setLayout(grid)
        
    def setup_width(self, value):
        widget = QDoubleSpinBox()
        widget.setRange(0, 1000)
        widget.setDecimals(1)
        widget.setSingleStep(0.5)
        widget.setSuffix(' [mm]')
        widget.setValue(value)

        return widget

    def setup_pressure_adv(self, value):
        widget = QDoubleSpinBox()
        widget.setRange(0, 10)
        widget.setDecimals(1)
        widget.setSingleStep(0.1)
        #widget.setSuffix(' [mm]')
        widget.setValue(value)

        return widget

    def setup_num(self, value, min, max, step):
        widget = QSpinBox()
        widget.setRange(min, max)
        widget.setSingleStep(step)
        #widget.setSuffix(' [mm]')
        widget.setValue(value)

        return widget

    def updateConfig(self, cfg):
        cfg.layers = self.layers.value()
        cfg.num_patterns = self.num_patterns.value()
        cfg.pattern_width = self.pattern_width.value()
        cfg.pressure_advance_min = self.pressure_advance_min.value()
        cfg.pressure_advance_max = self.pressure_advance_max.value()
        cfg.show_messages = self.show_messages.checkState()