import os


def rename_exact(directory, new_names):
    for key, value in new_names.items():
        key_path = f"{directory}\\{key}.WAV"
        new_value_path = f"{directory}\\{value}"
        if key_path != new_value_path:
            rename_gracefully(key_path, new_value_path)


def rename_all(directory, new_names):
    paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for path in paths:
        basename = os.path.basename(os.path.splitext(path)[0])
        try:
            name = basename
        except ValueError:
            continue
        try:
            name_path = f"{directory}\\{name}.WAV"
            new_value_path = f"{directory}\\{new_names[name]}"
            if name_path != new_value_path:
                rename_gracefully(path, f"{directory}\\{new_names[name]}")
        except KeyError:
            continue


def rename_similar(directory, new_names):
    paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    paths = get_similar_paths(paths)
    for key, similar_paths in paths.items():
        key_basename = os.path.basename(key)
        try:
            new_path = os.path.join(directory, new_names[key_basename])
        except KeyError:
            continue
        for path in similar_paths:
            new_value_path = f"{directory}\\{get_basename(os.path.basename(os.path.splitext(path)[0]))}.wav"
            if new_path.lower() != new_value_path.lower():
                rename_gracefully(path, new_path)


def get_basename(name):
    try:
        return name[:name.index('_')]
    except ValueError:
        pass
    return name


def rename_gracefully(src, dst):
    try:
        basename = os.path.basename(dst)
        new_dst = f"{os.path.dirname(dst)}\\{cleanse_string_for_invalid_characters(basename)}"
        os.rename(src, new_dst)
        print(f'Renamed {src} to {new_dst}')
    except FileExistsError:
        name, file_extension = os.path.splitext(dst)
        name = get_numbered_name(name)
        rename_gracefully(src, f"{name}{file_extension}")
    except:
        print(f"Could not rename {src}")


def cleanse_string_for_invalid_characters(string):
    list_of_invalid_characters = ['<', '>', ':', '"', '|', '?', '*']
    for character in list_of_invalid_characters:
        string = string.replace(character, '_')
    return string.replace('  ', ' ')


def get_numbered_name(name):
    last_letter = name[-1]
    if last_letter.isdigit():
        name, number = extract_complete_number_from_end_of_string(name)
        return f"{name}{number + 1}"
    else:
        return f"{name} 2"


def extract_complete_number_from_end_of_string(string):
    number = ''
    for index, letter in enumerate(string[::-1]):
        if not letter.isdigit():
            string = string[:-index]
            break
        number = f"{letter}{number}"
    return string, int(number)


def _rename_all_files_sequentially(directory):
    paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for path in paths:
        rename_gracefully(path, f"{os.path.dirname(path)}\\sound.wav")


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

