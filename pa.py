#!/usr/local/bin/python

# extrusion parameters (mm)
NOZZLE_DIA = 0.4
extrusion_width   = NOZZLE_DIA * 1.2 # typical: nozzleDiameter * 1.2 (f.e. a 0.4mm nozzle should be set to 0.48mm extrusion width in slicers)
layer_height      = NOZZLE_DIA * 0.5 # max: 50% of your extrusion_width
filament_diameter = 1.75 # manufacturers typically sell 1.73-1.74mm filament diameter (always lower than 1.75 to prevent cloggs) tested with many brands

# print speeds (mm/s)
travel_speed      = 200
first_layer_speed =  25
slow_speed        =  15 # speed for the slow segments
fast_speed        =  80 # speed for the fast segments
cooling_fan_speed = 128 # from 0 to 255

# calibration object dimensions (mm)
layers        = 200
object_width  = 180
num_patterns  =  4	# how many speed changes
pattern_width =  5	# slow speed length

# pressure advance gradient (s)
pressure_advance_min = 0.5
pressure_advance_max = 3.0

# center of print bed (mm)
# needed to position this print in the middle of your print bed
# If you are not sure about this: Take a look into your slicer. Normally you will see the origin (center) visualized as xyz-axis
# f.e. I have a 285x220mm bed, my printers origin is at X0, Y0 (front left corner), so the offset value you would need for X are 285/2.0 = 142.5
offset_x = 140.0
offset_y = 120.0

layer0_z = layer_height

# put your typical start.gcode here, if you use a custom start gcode via your slicing software
# Python tipp: to type in a continuous command over multiple lines you can use a backslash '\'
# general tipp: to output a 'new line' after your gcode command use '\n' which is the representation of the new line byte sequence
# in short: use '\n\' after each line of your regular start.gcode command
try:
    print('; START.gcode\n\
G90\n\
M82\n\
M106 S0\n\
M140 S70\n\
M104 S238 T0\n\
M190 S70\n\
M109 S238 T0\n\
G28 ; home all axes\n\
T0 ; set active extruder to 0\n\
;M913 Y50 ; lower Y stepper torque to 50% ;if stall detection fails for protection of mechanics\n\
;G1 X300 Y5 F1600;\n\
;M913 Y100 ; raise Y stepper torque back to 100%\n\
G1 Z0.4 F400;\n\
G91 ; relative\n\
; wipe nozzle on beds edge \n\
G1 X-20 E10 F800;\n\
G1 X-15 Y10 E13 F1600;\n\
G1 X-35 E15;\n\
G92 E0; zero extruded length\n\
G90 ; absolute\n\
; process _R_Multimaterial-1\n\
; layer 1, Z = 0.220\n\
T0\n\
G92 E0.0000 ; reset extruded length \n\
')
except:
    print(' !!! your start.gcode is faulty, check correct format')
    exit()

print('\nM83 ; relative extrusion for this python script\n')


from math import *


def extrusion_volume_to_length(volume):
    return volume / (filament_diameter * filament_diameter * pi * 0.25)

def extrusion_for_length(length):
    return extrusion_volume_to_length(length * extrusion_width * layer_height)

curr_x = offset_x
curr_y = offset_y
curr_z = layer0_z

# goto z height
print("G1 X%.3f Y%.3f Z%.3f E1.0 F%.0f" % (curr_x, curr_y, curr_z, travel_speed * 60))

def up():
    global curr_z
    curr_z += layer_height
    print("G1 Z%.3f" % curr_z)

def line(x,y,speed):
    length = sqrt(x**2 + y**2)
    global curr_x, curr_y
    curr_x += x
    curr_y += y
    if speed > 0:
        print("G1 X%.3f Y%.3f E%.4f F%.0f" % (curr_x, curr_y, extrusion_for_length(length), speed * 60))
    else:
        print("G1 X%.3f Y%.3f F%.0f" % (curr_x, curr_y, travel_speed * 60))

def goto(x,y):
    global curr_x, curr_y
    curr_x = x + offset_x
    curr_y = y + offset_y
    print("G1 X%.3f Y%.3f" %(curr_x, curr_y))

def first_layer_raft():

    print('; raft layer')

    line(-object_width/2,0,0)

    for l in range(2):
        
        for offset_i in range(5):
            offset = offset_i * extrusion_width
            line(object_width+offset,0,first_layer_speed)
            line(0,extrusion_width+offset*2,first_layer_speed)
            line(-object_width-offset*2,0,first_layer_speed)
            line(0,-extrusion_width-offset*2,first_layer_speed)
            line(offset,0,first_layer_speed)
            line(0,-extrusion_width,0)
        up()
        goto(-object_width/2,0)

    print('; raft layer end')
        
first_layer_raft()

print('\nM106 S{}\n'.format(cooling_fan_speed))

segment = (object_width*1.0) / num_patterns
space = segment - pattern_width

for l in range(layers):
    
    pressure_advance = (l / (layers * 1.0)) * (pressure_advance_max-pressure_advance_min) + pressure_advance_min;
    
    print("; layer %d, pressure advance: %.3f" %(l, pressure_advance))
    print("M117 layer %d, pressure advance: %.3f" %(l, pressure_advance))
    
    print("M572 D0 S%.3f" % pressure_advance)
    
    for i in range(num_patterns):
        line(space/2, 0, fast_speed)
        line(pattern_width, 0, slow_speed)
        line(space/2, 0, fast_speed)
    
    line(0,extrusion_width,fast_speed)

    for i in range(num_patterns):
        line(-space/2, 0, fast_speed)
        line(-pattern_width, 0, slow_speed)
        line(-space/2, 0, fast_speed)
    
    line(0,-extrusion_width,fast_speed)
    up()

print('; END.gcode\n\
G91 ; relative\n\
G1 Z10 F450 ; bed clearance\n\
G90 ; absolute\n\
M106 S0 ; turn off part cooling fan\n\
M104 S0 ; turn off extruder\n\
M140 S0 ; turn off bed\n\
M84 ; disable motors\n')
