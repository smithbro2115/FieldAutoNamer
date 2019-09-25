import soundfile
import time
import numpy as np
import os


class AudioConverter:
	CHUNK_SIZE = 1024
	VOLUME_PERCENTAGE = 100

	def __init__(self):
		self.sound_file = None
		self.buffer = []
		self.path = None
		self.sound_info = None
		self.finished = False
		self.loaded = False
		self.chunk_set = False
		self.processes = []

	def ready(self):
		return len(self.buffer) > 0

	# def buffer_loop(self):
	# 	while True:
	# 		while self.sound_file and len(self.buffer) < 50 and not self.finished:
	# 			self.set_buffer()
	# 			self.loaded = True
	# 		time.sleep(.03)

	def get_section(self, length, start):
		if start < 0:
			start = self.sound_info.duration + start
		self.seek(start*1000)
		chunk = self.sound_info.samplerate*length
		return self.pad_sound(self.sound_file.read(chunk))

	def get_sound_data(self):
		chunk = self.sound_info.frames
		return self.pad_sound(self.sound_file.read(chunk))

	def write_for_speech(self, path):
		self.stop()
		self.load(path)
		if self.sound_info.duration <= 20:
			data = self.get_sound_data()
		else:
			first_ten = self.get_section(10, 0)
			last_ten = self.get_section(10, -10)
			data = np.concatenate((first_ten, last_ten))
		return self.save_data(f"cache\\{os.path.basename(path)}", data)

	def save_data(self, path, data):
		soundfile.write(path, data, self.sound_info.samplerate)
		return path

	def load(self, path):
		self.finished = False
		self.path = path
		self.sound_file = soundfile.SoundFile(path)
		self.sound_info = soundfile.info(path)

	# def set_buffer(self):
	# 	data = self.get_correct_amount_of_channels(self.get_selected_channels(self.sound_file.read(self.CHUNK_SIZE)))
	# 	padded_data = self.pad_sound(data)
	# 	data_with_effects = padded_data, self.processes
	# 	data_at_correct_volume = self.set_volume(data_with_effects)
	# 	self.buffer.append(data_at_correct_volume)

	def seek(self, goto):
		"""
		Set read from frame
		:param goto:
			should be in milliseconds
		"""
		goto_frame = int(self.sound_info.samplerate * (goto / 1000))
		self.buffer = []
		try:
			self.sound_file.seek(goto_frame)
		except RuntimeError:
			self.sound_file.seek(self.sound_info.frames-1)

	def stop(self):
		self.sound_file = None
		self.chunk_set = False
		self.buffer = []

	def pad_sound(self, data):
		data_chunk_size = data.shape[0]
		if 0 < data_chunk_size < self.CHUNK_SIZE:
			data = np.pad(data, [(0, self.CHUNK_SIZE - data_chunk_size), (0, 0)], mode='constant')
			self.finished = True
		return data

	# def get_buffer(self, outdata, frames, time, status):
	# 	outdata[:] = self.buffer.pop(0)
	# 	if self.finished and len(self.buffer) == 0:
	# 		self.end_callback()

	def sum_to_mono(self, data):
		sound_data = np.ndarray(buffer=np.average(data, axis=1), shape=(data.shape[0], 1))
		return sound_data

	# def get_selected_channels(self, data):
	# 	if len(self.PLAY_INDIVIDUAL_CHANNELS) > 0:
	# 		return self._get_selected_channels_from_play_channels(data)
	# 	return data
	#
	# def _get_selected_channels_from_play_channels(self, data):
	# 	channels = self.get_individual_channels(data)
	# 	selected_channels = np.ndarray((data.shape[0], 0))
	# 	for channel_number in self.PLAY_INDIVIDUAL_CHANNELS:
	# 		try:
	# 			selected_channels = np.concatenate((selected_channels, channels[channel_number-1]), axis=1)
	# 		except IndexError:
	# 			continue
	# 	return selected_channels

	@staticmethod
	def get_individual_channels(data):
		sound_data = np.hsplit(data, data.shape[1])
		return sound_data


class AudioMerger:
	CHUNK_SIZE = 1024000

	def merge(self, paths, output):
		sound_files = self.get_sound_files(paths)
		self.check_frames_are_the_same(sound_files)
		self.write_to_file(sound_files, output)

	def write_to_file(self, sound_files, output):
		reference_sound_file = sound_files[0]
		while reference_sound_file.tell() < len(reference_sound_file):
			channels = self.merge_data_channels(self.get_sound_files_data(sound_files))
			try:
				with soundfile.SoundFile(output, mode='r+') as file:
					file.seek(0, soundfile.SEEK_END)
					file.write(channels)
			except RuntimeError:
				with soundfile.SoundFile(output, mode='w', samplerate=reference_sound_file.samplerate,
										 channels=channels.shape[1]) as file:
					file.seek(0, soundfile.SEEK_END)
					file.write(channels)

	def get_sound_files_data(self, sound_files):
		data_list = []
		for sound_file in sound_files:
			data = sound_file.read(self.CHUNK_SIZE)
			try:
				data_channels = self.get_individual_channels(data)
				for data in data_channels:
					data_list.append(np.ndarray.flatten(data))
			except IndexError:
				data_list.append(data)
		return data_list

	@staticmethod
	def merge_data_channels(data_list):
		channels = np.ndarray((data_list[0].shape[0], 0))
		for data in data_list:
			channels = np.concatenate((channels, data[:, None]), axis=1)
		return channels

	def pad_sound(self, data):
		data_chunk_size = data.shape[0]
		if 0 < data_chunk_size < self.CHUNK_SIZE:
			data = np.pad(data, [(0, self.CHUNK_SIZE - data_chunk_size), (0, 0)], mode='constant')
		return data

	@staticmethod
	def check_frames_are_the_same(sound_files):
		frames = sound_files[0].frames
		for sound_file in sound_files:
			if sound_file.frames != frames:
				raise RuntimeError

	@staticmethod
	def get_sound_files(paths):
		sound_files = []
		for path in paths:
			sound_file = soundfile.SoundFile(path)
			sound_files.append(sound_file)
		return sound_files

	@staticmethod
	def clean_up_array(data):
		new_data = []
		for value in data[0]:
			new_data.append(value[0])
		return np.ndarray(new_data)

	@staticmethod
	def get_individual_channels(data):
		sound_data = np.hsplit(data, data.shape[1])
		return sound_data


def merge_mics(directory):
	paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
	similar_paths = get_similar_paths(paths)
	for key, value in similar_paths.items():
		if len(value) > 1:
			print(f'Merging {key}')
			merger = AudioMerger()
			merger.merge(value, f"{key}.WAV")


def get_similar_paths(paths):
	similar = {}
	for path in paths:
		try:
			beginning = path[:path.index('_')]
		except ValueError:
			continue
		try:
			similar[beginning].append(path)
		except KeyError:
			similar[beginning] = [path]
	return similar


# audio_merger = AudioMerger()
# audio_merger.merge(["Z:\\SFX Library\\bin\\ZOOM0006_1.WAV", "Z:\\SFX Library\\bin\\ZOOM0006_2.WAV"],
# 						"Z:\\SFX Library\\bin\\ZOOM0006.WAV")
# audio_buffer.load("Z:\\SFX Library\\bin\\MONO\\TEST\\ZOOM0023_3.WAV")
# audio_buffer.get_ten_seconds(-10)
