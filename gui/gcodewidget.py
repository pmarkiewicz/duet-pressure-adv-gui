 
from PyQt5.QtWidgets import (QPlainTextEdit, QVBoxLayout, QGroupBox)
from PyQt5.QtGui import QTextDocument

class GCodeWidget(QGroupBox):
    def __init__(self, title, text, parent=None):
        super().__init__(title, parent=parent)
        
        self.initUI(text)
    
    def initUI(self, gcode):
        grid = QVBoxLayout()
        grid.setSpacing(10)

        #text_doc = QTextDocument()
        #text_doc.setPlainText(gcode)
        self.text = QPlainTextEdit()
        self.text.setPlainText(gcode)
        #self.text.setDocument(text_doc)
        grid.addWidget(self.text)

        self.setLayout(grid)

    def updateConfig(self, cfg, fieldname):
        setattr(cfg, fieldname, self.text.toPlainText())