import json

class PrinterConfig:
    '''
    General config for printer, they don't change for printer
    '''
    START_GCODE = '''
; Pressure advance test
; min pressure adv: {test.pressure_advance_min}
; max pressure adv: {test.pressure_advance_max}
; filament name: {filament.name}
; 
G90
M82
M106 S0
M140 S{filament.bed_temperature}
M104 S{filament.extruder_temperature} T0
M190 S{filament.bed_temperature}
M109 S{filament.extruder_temperature} T0
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
G1 E-10 F100 ; retract
G1 Z10 F450 ; bed clearance
G90 ; absolute
M106 S0 ; turn off part cooling fan
M104 S0 ; turn off extruder
M140 S0 ; turn off bed
M84 ; disable motors    
M81 S1 ; turn off

    '''

    def __init__(self):
        self.ip_addr = None
        self.pwd = None
        self.name = 'default printer'
        self.nozzle_dia = 0.4
        self.start_x = 50
        self.start_y = 120
        self.object_width  = 180
        self.start_gcode = self.START_GCODE
        self.end_gcode = self.END_GCODE


    def load_printer(self, data):
        self.name = data['name']
        self.nozzle_dia = data['nozzle_dia']
        self.start_x = data['start_x']
        self.start_y = data['start_y']
        self.object_width = data['object_width']
        self.start_gcode = data['start_gcode']
        self.end_gcode = data['end_gcode']

    def get_printer(self):
        return self.__dict__


class FilamentConfig:
    '''
    Filament related configurations
    '''
    EXTRUSION_WITH_MULT = 1.2
    LAYER_HIGHT_MULT = 0.5

    def __init__(self, printer):
        self.extrusion_width = printer.nozzle_dia * self.EXTRUSION_WITH_MULT
        self.layer_height = printer.nozzle_dia * self.LAYER_HIGHT_MULT
        self.filament_diameter = 1.75
        self.travel_speed      = 200
        self.first_layer_speed =  25
        self.slow_speed        =  15 # speed for the slow segments
        self.fast_speed        =  80 # speed for the fast segments
        self.cooling_fan_speed = 128
        self.first_layer_height = 0.2
        self.extruder_temperature = 275
        self.bed_temperature = 115
        self.raft_loops = 3
        self.name = 'PC'

    def load_filament(self, data):
        self.extrusion_width = data['extrusion_width']
        self.layer_height = data['layer_height']
        self.filament_diameter = data['filament_diameter']
        self.travel_speed = data['travel_speed']
        self.first_layer_speed = data['first_layer_speed']
        self.slow_speed  = data['slow_speed']
        self.fast_speed  = data['fast_speed']
        self.cooling_fan_speed = data['cooling_fan_speed']
        self.first_layer_height = data['first_layer_height']
        self.extruder_temperature = data['extruder_temperature']
        self.bed_temperature = data['bed_temperature']
        self.name = data['name']

    def get_filament(self):
        return self.__dict__

    def _travel_speed_in_min(self):
        return self.travel_speed * 60

    travel_speed_in_min = property(_travel_speed_in_min)
    

class TestConfig:
    def __init__(self):
        self.layers        = 10
        self.num_patterns  =  4	# how many speed changes
        self.pattern_width =  5	# slow speed length
        self.pressure_advance_min = 0.5
        self.pressure_advance_max = 3.0
        self.show_messages = False

    def load_test(self, data):
        self.layers = data['layers']
        self.num_patterns =  data['num_patterns']
        self.pattern_width = data['pattern_width']
        self.pressure_advance_min = data['pressure_advance_min']
        self.pressure_advance_max = data['pressure_advance_max']
        self.show_messages = data['show_messages']

    def get_test(self):
        return self.__dict__

class Configurator(PrinterConfig, FilamentConfig, TestConfig):
    def __init__(self, filename=None):
        PrinterConfig.__init__(self)
        FilamentConfig.__init__(self, self)
        TestConfig.__init__(self)

        if filename:
            self.load(filename)

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.load_printer(data)
                self.load_filament(data)
                self.load_test(data)
        except Exception as ex:
            print(ex)

    def save(self, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(self.__dict__, f, indent=4)
        except Exception as ex:
            print(ex)
