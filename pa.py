#!/usr/local/bin/python

from math import *

from configs import PrinterConfig, FilamentConfig, TestConfig

def extrusion_volume_to_length(volume, filament_config):
    return volume / (filament_config.filament_diameter ** 2 * pi * 0.25)    # 0.25 is to convert dia to radius   (R/2)^2

def extrusion_for_length(length, filament_config):
    return extrusion_volume_to_length(length * filament_config.extrusion_width * filament_config.layer_height, filament_config)

def up(layer_height):
    global curr_z
    curr_z += layer_height
    print(f"G1 Z{curr_z:.3f}")

def line(x, y, speed, filament_config):
    assert speed > 0, 'speed cannot be 0'

    length = sqrt(x**2 + y**2)
    global curr_x, curr_y
    curr_x += x
    curr_y += y
    extrusion = extrusion_for_length(length, filament_config)
    print(f"G1 X{curr_x:.3f} Y{curr_y:.3f} E{extrusion:.4f} F{speed * 60:.0f}")
        

def move(x, y, filament_config):
    global curr_x, curr_y
    curr_x += x
    curr_y += y
    print(f"G1 X{curr_x:.3f} Y{curr_y:.3f} F{filament_config.travel_speed_in_min:.0f}")


def goto(x, y, printer_config):
    global curr_x, curr_y
    curr_x = x #+ printer_config.offset_x
    curr_y = y #+ printer_config.offset_y

    print(f"G1 X{curr_x:.3f} Y{curr_y:.3f}")

def first_layer_raft(printer_config, filament_config):

    print('; raft layer')

    move(-printer_config.object_width / 2, 0, filament_config)

    for l in range(2):
        
        for offset_i in range(5):
            offset = offset_i * filament_config.extrusion_width

            line(printer_config.object_width + offset, 0, filament_config.first_layer_speed, filament_config)
            line(0, filament_config.extrusion_width + offset * 2, filament_config.first_layer_speed, filament_config)
            line(-printer_config.object_width - offset * 2, 0, filament_config.first_layer_speed, filament_config)
            line(0, -filament_config.extrusion_width - offset*2, filament_config.first_layer_speed, filament_config)
            line(offset, 0, filament_config.first_layer_speed, filament_config)
            
            move(0,-filament_config.extrusion_width, filament_config)

        up(filament_config.layer_height)
        goto(printer_config.start_x, printer_config.start_y, printer_config)

    print('; raft layer end')

printer_config = PrinterConfig()
filament_config = FilamentConfig(printer_config)
test_config = TestConfig()


layer0_z = filament_config.layer_height

print(printer_config.start_gcode.format(filament=test_config))

curr_x = printer_config.start_x + printer_config.object_width/2
curr_y = printer_config.start_y
curr_z = layer0_z

# goto z height
print("G1 X%.3f Y%.3f Z%.3f E1.0 F%.0f" % (curr_x, curr_y, curr_z, filament_config.travel_speed * 60))
        
first_layer_raft(printer_config, filament_config)

print(f'\nM106 S{filament_config.cooling_fan_speed}\n')

segment = (printer_config.object_width * 1.0) / test_config.num_patterns
space = segment - test_config.pattern_width

for l in range(test_config.layers):
    
    pressure_advance = (l / (test_config.layers * 1.0)) * (test_config.pressure_advance_max - test_config.pressure_advance_min) + test_config.pressure_advance_min
    
    print("; layer %d, pressure advance: %.3f" %(l, pressure_advance))

    if test_config.show_messages:
        print(f"M117 layer {l}, pressure advance: {pressure_advance:.3f}")
    
    print(f"M572 D0 S{pressure_advance:.3f}")
    
    for i in range(test_config.num_patterns):
        line(space/2, 0, filament_config.fast_speed, filament_config)
        line(test_config.pattern_width, 0, filament_config.slow_speed, filament_config)
        line(space / 2, 0, filament_config.fast_speed, filament_config)
    
    line(0, filament_config.extrusion_width, filament_config.fast_speed, filament_config)

    for i in range(test_config.num_patterns):
        line(-space / 2, 0, filament_config.fast_speed, filament_config)
        line(-test_config.pattern_width, 0, filament_config.slow_speed, filament_config)
        line(-space/2, 0, filament_config.fast_speed, filament_config)
    
    line(0, -filament_config.extrusion_width, filament_config.fast_speed, filament_config)
    up(filament_config.layer_height)

print(printer_config.end_gcode)
