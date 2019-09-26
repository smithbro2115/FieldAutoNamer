from main import process_sounds
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
import traceback
import sys
import qdarkstyle
import os
from gui import MainWindow


class Stream(QtCore.QObject):
	newText = QtCore.pyqtSignal(str)

	def write(self, text):
		self.newText.emit(str(text))


class MainUI(MainWindow.Ui_MainWindow):
	def __init__(self, parent_window: QtWidgets.QMainWindow):
		self.parent_window = parent_window
		self.setupUi(self.parent_window)
		self.directoryListWidget = DirectoryListWidget()
		self.directoryListWidget.signals.dropped.connect(self.dropped_onto_list)
		self.startPushButton.clicked.connect(self.start)
		self.processing_thread_pool = QThreadPool()
		self.processing_thread_pool.setMaxThreadCount(1)
		self.setup_additional()
		self.stream = Stream()
		self.stream.newText.connect(self.add_line_to_stdout)
		sys.stdout = self.stream

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

	@property
	def paths(self):
		paths = {}
		for i in range(self.directoryListWidget.count()):
			path = self.directoryListWidget.item(i).data(8)
			dir_name = os.path.dirname(path)
			try:
				paths[dir_name].append(path)
			except KeyError:
				paths[dir_name] = [path]
		return paths

	def __del__(self):
		try:
			sys.stdout = sys.__stdout__
		except AttributeError:
			pass

	def dropped_onto_list(self, paths):
		paths = self.get_paths(paths)
		for paths_list in paths:
			for path in paths_list:
				item = QtWidgets.QListWidgetItem(os.path.basename(path))
				item.setData(8, path)
				self.directoryListWidget.addItem(item)

	def get_paths(self, paths):
		path_list = [[]]
		for path in paths:
			if os.path.isdir(path):
				path_list.append(self.get_paths_from_directory(path))
			else:
				path_list[0].append(path)
		return path_list

	@staticmethod
	def get_paths_from_directory(directory):
		return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

	def setup_additional(self):
		self.parent_window.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
		self.centralwidget.layout().addWidget(self.directoryListWidget, 1, 0)
		self.directoryListWidget.setAcceptDrops(True)

	def add_line_to_stdout(self, string):
		string = string.replace("\n", '')
		self.stdoutTextBrowser.append(string)

	def processing_finished(self):
		if self.processing_thread_pool.activeThreadCount() <= 0:
			self.startPushButton.setEnabled(True)

	def start(self):
		self.startPushButton.setEnabled(False)
		for path_dir, paths in self.paths.items():
			worker = Worker(self.start_processing_dir, path_dir, paths)
			worker.signals.finished.connect(self.processing_finished)
			self.processing_thread_pool.start(worker)

	def start_processing_dir(self, path_dir, paths):
		string_path_dir = path_dir.replace('\\\\', '/').replace('\\', '/')
		print(f"Started processing sounds from {string_path_dir}")
		process_sounds(paths, self.reference_ending, self.filter, self.check, self.merge)


class WorkerSignals(QObject):
	finished = pyqtSignal()
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	progress = pyqtSignal(int)


class Worker(QRunnable):
	def __init__(self, fn, *args, **kwargs):
		super(Worker, self).__init__()

		# Store constructor arguments (re-used for processing)
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()

		self.interrupt = False

		# Add the callback to our kwargs
		self.kwargs['progress_callback'] = self.signals.progress

	@pyqtSlot()
	def run(self):

		# Retrieve args/kwargs here; and fire processing using them
		try:
			result = self.fn(*self.args)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			self.signals.error.emit((exctype, value, traceback.format_exc()))
		else:
			self.signals.result.emit(result)  # Return the result of the processing
		finally:
			if not self.interrupt:
				self.signals.finished.emit()  # Done


class DirectoryListSignals(QObject):
	dropped = pyqtSignal(list)


class DirectoryListWidget(QtWidgets.QListWidget):
	def __init__(self):
		super(DirectoryListWidget, self).__init__()
		self.signals = DirectoryListSignals()

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls:
			event.setDropAction(QtCore.Qt.LinkAction)
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		files = [u.toLocalFile() for u in event.mimeData().urls()]
		paths = []
		for f in files:
			paths.append(f)
		self.signals.dropped.emit(paths)


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = QtWidgets.QMainWindow()
	ui = MainUI(window)
	window.show()
	sys.exit(app.exec_())
