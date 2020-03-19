import locale

from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QFileDialog, QPushButton, 
                            QVBoxLayout, QGroupBox, QGridLayout, QMessageBox, QLabel, 
                            QDoubleSpinBox, QSpinBox)
from PyQt5.QtGui import QDoubleValidator, QIntValidator


class FilamentWidget(QGroupBox):
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

        grid.addWidget(QLabel('extrusion_width'), 2, 0)
        self.extrusion_width = self.setup_small_distance(self.cfg.extrusion_width)
        grid.addWidget(self.extrusion_width, 2, 1)

        grid.addWidget(QLabel('layer_height'), 3, 0)
        self.layer_height = self.setup_small_distance(self.cfg.layer_height, step=0.05)
        grid.addWidget(self.layer_height, 3, 1)

        grid.addWidget(QLabel('filament_diameter'), 4, 0)
        self.filament_diameter = self.setup_small_distance(self.cfg.filament_diameter, max_value=5)
        grid.addWidget(self.filament_diameter, 4, 1)

        grid.addWidget(QLabel('first_layer_height'), 10, 0)
        self.first_layer_height = self.setup_small_distance(self.cfg.layer_height)
        grid.addWidget(self.first_layer_height, 10, 1)
        
        grid.addWidget(QLabel('travel_speed'), 5, 0)
        self.travel_speed = self.setup_speed(self.cfg.travel_speed)
        grid.addWidget(self.travel_speed, 5, 1)

        grid.addWidget(QLabel('first_layer_speed'), 6, 0)
        self.first_layer_speed = self.setup_speed(self.cfg.first_layer_speed)
        grid.addWidget(self.first_layer_speed, 6, 1)

        grid.addWidget(QLabel('slow_speed'), 7, 0)
        self.slow_speed = self.setup_speed(self.cfg.slow_speed)
        grid.addWidget(self.slow_speed, 7, 1)

        grid.addWidget(QLabel('fast_speed'), 8, 0)
        self.fast_speed = self.setup_speed(self.cfg.fast_speed)
        grid.addWidget(self.fast_speed, 8, 1)

        grid.addWidget(QLabel('cooling_fan_speed [0-255]'), 9, 0)
        self.cooling_fan_speed = QSpinBox()
        self.cooling_fan_speed.setRange(0, 255)
        self.cooling_fan_speed.setSingleStep(5)
        self.cooling_fan_speed.setValue(self.cfg.cooling_fan_speed)
        grid.addWidget(self.cooling_fan_speed, 9, 1)

        grid.addWidget(QLabel('extruder_temperature'), 11, 0)
        self.extruder_temperature = self.setup_temperature(self.cfg.extruder_temperature)
        grid.addWidget(self.extruder_temperature, 11, 1)

        grid.addWidget(QLabel('bed_temperature'), 12, 0)
        self.bed_temperature = self.setup_temperature(self.cfg.bed_temperature)
        grid.addWidget(self.bed_temperature, 12, 1)

        grid.addWidget(QLabel('raft_loops'), 13, 0)
        self.raft_loops = QSpinBox()
        self.raft_loops.setValue(self.cfg.raft_loops)
        self.raft_loops.setRange(5, 50)
        self.raft_loops.setSingleStep(1)
        grid.addWidget(self.raft_loops, 13, 1)

        # grid.addWidget(QLabel('name'), 0, 0)
        # self.name = QLineEdit(self.cfg.name)
        # grid.addWidget(self.name, 0, 1)

        grid.addWidget(QLabel(''), 0, 2)

        self.setLayout(grid)
        
    def setup_speed(self, value):
        widget = QSpinBox()
        widget.setRange(0, 500)
        widget.setSingleStep(5)
        widget.setSuffix(' [mm/s]')
        widget.setValue(value)

        return widget

    def setup_temperature(self, value):
        widget = QSpinBox()
        widget.setRange(0, 500)
        widget.setSingleStep(5)
        widget.setSuffix(' [°C]')
        widget.setValue(value)

        return widget

    def setup_small_distance(self, value, step = 0.01, max_value = 2):
        widget = QDoubleSpinBox()
        widget.setRange(0, max_value)
        widget.setDecimals(2)
        widget.setSingleStep(step)
        widget.setSuffix(' [mm]')
        widget.setValue(value)

        return widget