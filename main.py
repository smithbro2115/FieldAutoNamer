import speech_recognition as sr
import os
import pydub
import converter

AUDIO_FILE = "Z:\\SFX Library\\bin\\Combined\\ZOOM0027_1_2_3.WAV"
AUDIO_FILE_1 = "C:\\Users\\smith\\Downloads\\Sports Human Voice Male Young Man Basketball" \
             " Announcer It's Fifty Six To Forty Five At The Half 02.wav"
# pydub.AudioSegment.ffmpeg = "D:\\Programming\\FieldAutoNamer\\ffmpeg\\ffmpeg\\bin\\ffmpeg.exe"


def get_renamed_files_dict(path, reference_number, filter_words, check_words):
    reference_file_paths = get_file_names(path, reference_number)
    for key, value in reference_file_paths.items():
        file_type = os.path.splitext(value)[1]
        audio_path = get_audio_segment(value)
        raw_text = recognize_audio(audio_path)
        if raw_text:
            processed = get_file_name_from_google_words(raw_text, filter_words, check_words)
            if processed:
                print(f'Found {value} as {processed}')
                reference_file_paths[key] = f"{processed}{file_type}"
        else:
            reference_file_paths[key] = f"{key}{file_type}"
    return reference_file_paths


def clear_cache():
    files = [os.path.join('cache', f) for f in os.listdir('cache') if os.path.isfile(os.path.join('cache', f))]
    for file in files:
        os.remove(file)


def get_file_names(path, reference_file_number):
    paths = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return get_all_reference_paths(paths, reference_file_number)


def get_all_reference_paths(paths, reference_file_number):
    reference_paths = {}
    for path in paths:
        if path.endswith(f"{reference_file_number}.WAV"):
            basename = os.path.basename(path)
            reference_paths[basename[:basename.index('_')]] = path
    return reference_paths


def rename_file(old_path, new_path):
    os.rename(old_path, new_path)


def get_first_and_last(path):
    audio = converter.AudioBuffer()
    return audio.write_for_speech(path)


def get_audio_segment(path):
    path = get_first_and_last(path)
    audio_segment = pydub.AudioSegment.from_wav(path)
    audio_segment = audio_segment.set_frame_rate(44100)
    audio_path = f"cache\\{os.path.basename(path)}"
    audio_segment.export(audio_path, format='wav')
    return audio_path


def get_correct_audio_segment_duration(audio_segment):
    if audio_segment.duration_seconds > 20:
        first_five = audio_segment[:10000]
        last_five = audio_segment[-10000:]
        audio_segment = first_five+last_five
    return audio_segment


def recognize_audio(path):
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def get_file_name_from_google_words(string, filter_words, check_words):
    filename = ''
    words = string.split()
    if check_words:
        filename = get_string_that_is_checked(words, filter_words)
    elif filter_words:
        for index, word in enumerate(words):
            filename = f"{filename} {filter_word(word, index)}"
    else:
        filename = string
    try:
        return filename.strip().title()
    except AttributeError:
        return filename


def get_string_that_is_checked(words, filter_words):
    filename = ''
    input_began = False
    last_word = ''
    for index, word in enumerate(words):
        if input_began:
            if check_if_ended(word):
                input_began = False
            else:
                processed_word = filter_word(word, index) if filter_words else word
                filename = f"{filename} {processed_word}"
        else:
            input_began = check_if_started(word, last_word)
        last_word = word
    if filename != "":
        return filename


def check_if_started(word, last_word):
    if last_word == 'this' and word == 'is' or word == 'append':
        return True
    return False


def check_if_ended(word):
    end_list = ['end', 'stop']
    if word in end_list:
        return True
    return False


def filter_word(word, index):
    filter_list = ['um', 'uh', 'em']
    filter_leading_list = ['this', 'is']
    filter_leading_index_list = [0, 1]
    if word in filter_list:
        return ''
    if word in filter_leading_list and index in filter_leading_index_list:
        return ''
    return word


print(get_renamed_files_dict('Z:\\SFX Library\\bin\\MONO\\TEST', 3, True, False))
clear_cache()

