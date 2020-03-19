import sys
import os
from pathlib import Path
import locale

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale

from configs import Configurator
from gui.appwidget import App
from pa import generate_pa_test

CONFIG_FILE = 'duet_pressure_advance.cfg'

def generate(cfg):
    pass

if __name__ == '__main__':
    cfg_file = os.path.join(Path.home(), CONFIG_FILE)
    configurator = Configurator(cfg_file)

    #qt_locale = QLocale.system().name()
    #locale.setlocale(locale.LC_ALL, qt_locale)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = App(generate_pa_test, configurator)
    
    sys.exit(app.exec_())

    configurator.save(cfg_file)