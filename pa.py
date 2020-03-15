#!/usr/local/bin/python

from math import *
import os
from pathlib import Path

from configs import Config

CONFIG_FILE = 'duet_pressure_advance.cfg'

class GCodeGen:
    def __init__(self, printer_config, filament_config, test_config):
        self.printer_config = printer_config
        self.filament_config = filament_config
        self.test_config = test_config

        self.curr_x = printer_config.start_x + printer_config.object_width/2
        self.curr_y = printer_config.start_y
        self.curr_z = filament_config.first_layer_height

    def extrusion_volume_to_length(self, volume):
        return volume / (self.filament_config.filament_diameter ** 2 * pi * 0.25)    # 0.25 is to convert dia to radius   (R/2)^2

    def extrusion_for_length(self, length):
        return self.extrusion_volume_to_length(length * self.filament_config.extrusion_width * self.filament_config.layer_height)

    def up(self):
        self.curr_z += self.filament_config.layer_height
        print(f"G1 Z{self.curr_z:.3f}")

    def line(self, x, y, speed):
        assert speed > 0, 'speed cannot be 0'

        length = sqrt(x**2 + y**2)
        self.curr_x += x
        self.curr_y += y
        extrusion = self.extrusion_for_length(length)
        print(f"G1 X{self.curr_x:.3f} Y{self.curr_y:.3f} E{extrusion:.4f} F{speed * 60:.0f}")

    def line_rel(self, x, y, speed):
        assert speed > 0, 'speed cannot be 0'

        length = sqrt(x**2 + y**2)
        extrusion = self.extrusion_for_length(length)
        print(f"G1 X{x:.3f} Y{y:.3f} E{extrusion:.4f} F{speed * 60:.0f}")

    def move(self, x, y):
        self.curr_x += x
        self.curr_y += y
        print(f"G1 X{self.curr_x:.3f} Y{self.curr_y:.3f} F{self.filament_config.travel_speed_in_min:.0f}")

    def goto(self, x, y):
        self.curr_x = x 
        self.curr_y = y

        print(f"G1 X{self.curr_x:.3f} Y{self.curr_y:.3f}")

    def goto_current_coords(self):
        print("G1 X%.3f Y%.3f Z%.3f E1.0 F%.0f" % (self.curr_x, self.curr_y, self.curr_z, self.filament_config.travel_speed_in_min))

    def start_fan(self):
        print(f'\nM106 S{self.filament_config.cooling_fan_speed}')


class TestPrinter(GCodeGen):
    def __init__(self, printer_config, filament_config, test_config):
        super().__init__(printer_config, filament_config, test_config)


    def print_start_gcode(self):
        print(self.printer_config.start_gcode.format(test=self.test_config, filament=self.filament_config))

        
    def print_end_gcode(self):
        print(self.printer_config.end_gcode.format(filament=self.test_config))

        
    def first_layer_raft(self):
        speed = self.filament_config.first_layer_speed
        object_width = self.printer_config.object_width
        extrusion_width = self.filament_config.extrusion_width

        print('; raft layer')

        self.move(-self.printer_config.object_width / 2, 0)

        for _ in range(2):
            
            for offset_i in range(5):
                offset = offset_i * self.filament_config.extrusion_width

                self.line(object_width + offset, 0, speed)
                self.line(0, extrusion_width + offset * 2, speed)
                self.line(-object_width - offset * 2, 0, speed)
                self.line(0, -extrusion_width - offset*2, speed)
                self.line(offset, 0, speed)

                self.move(0,-extrusion_width)

            self.up()
            self.goto(self.printer_config.start_x, self.printer_config.start_y)

        print('; raft layer end')

    def raft_loops(self):
        self.goto(self.printer_config.start_x, self.printer_config.start_y)
        print('G91; relative')

        for loop in range(0, self.filament_config.raft_loops * 2, 2):
            self.line_rel(0, 
                          loop * self.filament_config.extrusion_width, 
                          self.filament_config.first_layer_speed)
            self.line_rel(self.printer_config.object_width + loop * self.filament_config.extrusion_width, 
                          0, 
                          self.filament_config.first_layer_speed)
            self.line_rel(0, 
                          (loop + 1) * -self.filament_config.extrusion_width, 
                          self.filament_config.first_layer_speed)
            self.line_rel(-self.printer_config.object_width - (loop + 1) * self.filament_config.extrusion_width, 
                          0, 
                          self.filament_config.first_layer_speed)

        print('G90; absolute')


    def print_segment(self, dir, space):
        self.line(dir * space / 2, 0, self.filament_config.fast_speed)
        self.line(dir * self.test_config.pattern_width, 0, self.filament_config.slow_speed)
        self.line(dir * space / 2, 0, self.filament_config.fast_speed)

    def print_layer(self, space):
        for _ in range(self.test_config.num_patterns):
            self.print_segment(1.0, space)

        self.line(0, self.filament_config.extrusion_width, self.filament_config.fast_speed)

        for _ in range(self.test_config.num_patterns):
            self.print_segment(-1.0, space)
        
        self.line(0, -self.filament_config.extrusion_width, self.filament_config.fast_speed)


    def print_test(self):
        segment = (self.printer_config.object_width * 1.0) / self.test_config.num_patterns
        space = segment - self.test_config.pattern_width

        for l in range(self.test_config.layers):
            
            pressure_advance = (l / (self.test_config.layers * 1.0)) * \
                (self.test_config.pressure_advance_max - self.test_config.pressure_advance_min) + \
                self.test_config.pressure_advance_min
            
            print("; layer %d, pressure advance: %.3f" %(l, pressure_advance))

            if self.test_config.show_messages:
                print(f"M117 layer {l}, pressure advance: {pressure_advance:.3f}")
            
            print(f"M572 D0 S{pressure_advance:.3f}")
            
            self.print_layer(space)

            self.up()


def generate_pa_test(printer_config, filament_config, test_config):
    printer = TestPrinter(printer_config, filament_config, test_config)


    printer.print_start_gcode()
    printer.goto_current_coords()
    printer.raft_loops()
    #printer.first_layer_raft()
    printer.start_fan()
    printer.print_test()
    printer.print_end_gcode()


if __name__ == '__main__':
    cfg_file = os.path.join(Path.home(), CONFIG_FILE)
    configurator = Configurator(cfg_file)

    printer_config = PrinterConfig()
    filament_config = FilamentConfig(printer_config)
    test_config = TestConfig()

    generate_pa_test(printer_config, filament_config, test_config)
