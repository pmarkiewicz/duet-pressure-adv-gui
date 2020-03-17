#!/usr/local/bin/python

import math
import os
from pathlib import Path

from configs import Configurator

CONFIG_FILE = 'duet_pressure_advance.cfg'

class GCodeGen:
    def __init__(self, config):
        self.cfg = config

    def extrusion_volume_to_length(self, volume):
        return volume / (self.cfg.filament_diameter ** 2 * math.pi * 0.25)    # 0.25 is to convert dia to radius   (R/2)^2

    def extrusion_for_length(self, length):
        return self.extrusion_volume_to_length(length * self.cfg.extrusion_width * self.cfg.layer_height)

    def up(self):
        return f"G1 Z{self.cfg.layer_height:.3f}"

    def line(self, x: float, y: float, speed: float) -> str:
        assert speed > 0, 'speed cannot be 0'

        length = math.sqrt(x**2 + y**2)
        extrusion = self.extrusion_for_length(length)
        return f"G1 X{x:.3f} Y{y:.3f} E{extrusion:.4f} F{speed * 60:.0f}"

    def goto(self, x: float, y: float) -> str:
        return f"G1 X{x:.3f} Y{y:.3f} F{self.cfg.travel_speed_in_min:.0f}"
        
    def goto_xyz(self, x: float, y: float, z: float) -> str:
        return f"G1 X{x:.3f} Y{y:.3f} Y{z:.3f} F{self.cfg.travel_speed_in_min:.0f}"

    def start_fan(self):
        return f'M106 S{self.cfg.cooling_fan_speed} ; start fan'

    def relative_moves(self):
        return 'G91; relative'

class TestPrinter(GCodeGen):
    def __init__(self, cfg):
        super().__init__(cfg)


    def start_gcode(self) -> [str]:
        s = self.cfg.start_gcode.format(test=self.cfg, filament=self.cfg)
        return s.split('\n')
        
    def end_gcode(self) -> [str]:
        s = self.cfg.end_gcode.format(filament=self.cfg)
        return s.split('\n')

    def raft_loops(self):
        result = ['; Raft start']

        result.append(self.goto(self.cfg.start_x, self.cfg.start_y))
        result.append(self.relative_moves())

        for loop in range(0, self.cfg.raft_loops * 2, 2):
            result.append(self.line(0, 
                          loop * self.cfg.extrusion_width, 
                          self.cfg.first_layer_speed))
            result.append(self.line(self.cfg.object_width + loop * self.cfg.extrusion_width, 
                          0, 
                          self.cfg.first_layer_speed))
            result.append(self.line(0, 
                          (loop + 1) * -self.cfg.extrusion_width, 
                          self.cfg.first_layer_speed))
            result.append(self.line(-self.cfg.object_width - (loop + 1) * self.cfg.extrusion_width, 
                          0, 
                          self.cfg.first_layer_speed))

        result.append('G90; absolute')
        result.append('; Raft end')

        return result


    def get_segment_rel(self, dir: float) -> list:
        segment = (self.cfg.object_width * 1.0) / self.cfg.num_patterns
        space = segment - self.cfg.pattern_width
        
        result = []

        result.append(self.line(dir * space / 2, 0, self.cfg.fast_speed))
        result.append(self.line(dir * self.cfg.pattern_width, 0, self.cfg.slow_speed))
        result.append(self.line(dir * space / 2, 0, self.cfg.fast_speed))

        return result


    def generate_layer(self) -> []:
        result = []

        to_right = self.get_segment_rel(1.0)
        to_left = self.get_segment_rel(-1.0)

        for _ in range(self.cfg.num_patterns):
            result += to_right

        result.append(self.line(0, -self.cfg.extrusion_width, self.cfg.fast_speed))

        for _ in range(self.cfg.num_patterns):
            result += to_left
        
        result.append(self.line(0, self.cfg.extrusion_width, self.cfg.fast_speed))

        return result


    def get_test(self):
        pressure_step = (self.cfg.pressure_advance_max - self.cfg.pressure_advance_min) + self.cfg.pressure_advance_min
        layer = self.generate_layer()

        result = [self.relative_moves()]

        for l in range(self.cfg.layers):
            pressure_advance = (l / (self.cfg.layers * 1.0)) * pressure_step
            
            result.append("; layer %d, pressure advance: %.3f" %(l, pressure_advance))

            if self.cfg.show_messages:
                result.append(f"M117 layer {l}, pressure advance: {pressure_advance:.3f}")
            
            result.append(f"M572 D0 S{pressure_advance:.3f}")
            
            result += layer

            result.append(self.up())

        result.append('G90; abs')

        return result


    def goto_start(self):
        return [self.goto(self.cfg.start_x, self.cfg.start_y)]

def generate_pa_test(cfg):
    printer = TestPrinter(cfg)

    gcode = []
    gcode += printer.start_gcode()
    gcode += printer.goto_start()
    gcode += printer.raft_loops()
    gcode.append(printer.start_fan())
    gcode += printer.goto_start()
    gcode += printer.get_test()
    gcode += printer.end_gcode()

    return gcode


if __name__ == '__main__':
    cfg_file = os.path.join(Path.home(), CONFIG_FILE)
    configurator = Configurator(cfg_file)

    gcode = generate_pa_test(configurator)

    s = '\n'.join(gcode)
    with open('test.gcode', 'w') as f:
        f.write(s)

    configurator.save(cfg_file)
