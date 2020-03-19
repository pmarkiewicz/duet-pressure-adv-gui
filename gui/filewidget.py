from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QFileDialog, QPushButton, 
                            QVBoxLayout, QGroupBox, QGridLayout, QMessageBox, QLabel)


class FileOpenWidget(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent=parent)
        
        self.filePattern = ''
        self.title = title

        self.initUI()
    
    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        self.fileNameEdit = QLineEdit()
        grid.addWidget(self.fileNameEdit, 1, 0)

        btn = QPushButton('Open')
        btn.clicked.connect(self.openFileNameDialog)

        grid.addWidget(btn, 1, 1)
        
        self.setLayout(grid)

    def get_filename(self):
        return self.fileNameEdit.text()

    def set_filename(self, fileName):
        self.fileNameEdit.setText(fileName)

    filename = property(get_filename, set_filename)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        filter = "Excel Files (*.xlsx);;All Files (*)"
        if self.filePattern:
            filter = f'{self.title} ({self.filePattern});;{filter}'
        fileName, _ = QFileDialog.getOpenFileName(self, self.title, "", filter, options=options)
        self.set_filename(fileName)


class FileSaveWidget(FileOpenWidget):
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        filter = "Excel Files (*.xlsx);;All Files (*)"
        self.fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "", filter, options=options)
        self.fileNameEdit.setText(self.fileName)
