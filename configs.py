import json

class PrinterConfig:
    '''
    General config for printer, they don't change for printer
    '''
    START_GCODE = '''
; Pressure advance test
; min pressure adv: {filament.pressure_advance_min}
; max pressure adv: {filament.pressure_advance_max}
G90
M82
M106 S0
M140 S70
M104 S238 T0
M190 S70
M109 S238 T0
G28 ; home all axes
T0 ; set active extruder to 0
;M913 Y50 ; lower Y stepper torque to 50% ;if stall detection fails for protection of mechanics
;G1 X300 Y5 F1600
;M913 Y100 ; raise Y stepper torque back to 100%
G1 Z0.4 F400
G91 ; relative
; wipe nozzle on beds edge 
G1 X-20 E10 F800;
G1 X-15 Y10 E13 F1600;
G1 X-35 E15
G92 E0; zero extruded length
G90 ; absolute
; process _R_Multimaterial-1
; layer 1, Z = 0.220
T0
G92 E0.0000 ; reset extruded length 
M83 ; relative extrusion 
    '''

    END_GCODE = '''
; END.gcode
G91 ; relative
G1 Z10 F450 ; bed clearance
G90 ; absolute
M106 S0 ; turn off part cooling fan
M104 S0 ; turn off extruder
M140 S0 ; turn off bed
M84 ; disable motors    
    '''

    def __init__(self):
        self.name = 'default printer'
        self.nozzle_dia = 0.4
        self.start_x = 50
        self.start_y = 120
        self.object_width  = 180
        self.start_gcode = self.START_GCODE
        self.end_gcode = self.END_GCODE


    def load(self, fn):
        with open(fn) as f:
            data = json.load(f)
            print(data)

    def save(self, fn):
        d = self.__dict__
        with open(fn, 'w') as f:
            json.dump(self.__dict__, f)


class FilamentConfig:
    '''
    Filament related configurations
    '''
    EXTRUSION_WITH_MULT = 1.2
    LAYER_HIGHT_MULT = 0.5

    filament_diameter = 1.75
    travel_speed      = 200
    first_layer_speed =  25
    slow_speed        =  15 # speed for the slow segments
    fast_speed        =  80 # speed for the fast segments
    cooling_fan_speed = 128
    extrusion_width = 0.42
    layer_height = 0.2

    def __init__(self, printer):
        self.extrusion_width = printer.nozzle_dia * self.EXTRUSION_WITH_MULT
        self.layer_height = printer.nozzle_dia * self.LAYER_HIGHT_MULT

    def _travel_speed_in_min(self):
        return self.travel_speed * 60

    travel_speed_in_min = property(_travel_speed_in_min)
    


class TestConfig:
    layers        = 10
    num_patterns  =  4	# how many speed changes
    pattern_width =  5	# slow speed length
    pressure_advance_min = 0.5
    pressure_advance_max = 3.0
    show_messages = False

p = PrinterConfig()
p.save('c:/temp/test1.json')
