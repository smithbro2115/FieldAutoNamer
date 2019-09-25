from main import process_sounds
from PyQt5 import QtWidgets
import sys
import qdarkstyle
from gui import MainWindow


class MainUI(MainWindow.Ui_MainWindow):
	def __init__(self, parent_window: QtWidgets.QMainWindow):
		self.parent_window = parent_window
		self.setupUi(self.parent_window)
		self.directoryListWidget = DirectoryListWidget()
		self.setup_additional()

	@property
	def reference_ending(self):
		return self.referenceEndingLineEdit.text() if self.referenceEndingLineEdit.text() != "" else None

	@property
	def filter(self):
		return self.filterCheckBox.checkState()

	@property
	def merge(self):
		return self.mergeCheckBox.checkState()

	@property
	def check(self):
		return self.checkCheckBox.checkState()

	def setup_additional(self):
		self.parent_window.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
		self.centralwidget.layout().addWidget(self.directoryListWidget, 1, 0)
		self.directoryListWidget.acceptDrops()

	def start(self):
		for directory in self.directoryListWidget.items():
			process_sounds(directory, self.reference_ending, self.filter, self.check, self.merge)


class DirectoryListWidget(QtWidgets.QListWidget):
	def dragMoveEvent(self, *args, **kwargs):
		print(args, kwargs)


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = QtWidgets.QMainWindow()
	ui = MainUI(window)
	window.show()
	sys.exit(app.exec_())
