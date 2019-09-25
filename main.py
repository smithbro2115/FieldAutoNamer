import recognizer
import converter
import renamer
import os
import argparse


def process_sounds(directory, reference_number=None, filter_words=True, check_words=False, should_merge_mics=True):
    new_names = recognizer.get_renamed_files_dict(directory, reference_number, filter_words, check_words)
    if should_merge_mics:
        converter.merge_mics(directory)
        renamer.rename_exact(directory, new_names)
    elif reference_number:
        renamer.rename_similar(directory, new_names)
    else:
        renamer.rename_all(directory, new_names)
    clear_cache()


def clear_cache():
    files = [os.path.join('cache', f) for f in os.listdir('cache') if os.path.isfile(os.path.join('cache', f))]
    for file in files:
        os.remove(file)


def convert_string_to_bool(string):
    if string.lower() == 'true':
        return True
    elif string.lower() == 'false':
        return False
    raise ValueError('Neither true nor false')


if __name__ == "__main__":
    description = "This is a script for processing sounds recorded on a Zoom recorder, it will attempt" \
                  " to auto name and combine the mics into one .wav file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--directory', '-d', help="Set the directory where the recorder files are")
    parser.add_argument('--reference_number', '-r', help="Ending characters of the files you wish to use for naming. "
                                                         "Will pick one at random if none is selected")
    parser.add_argument('--filter', '-f', help='Whether you should filter out words like "This is" from the naming. '
                                               'Enter true or false. Defaults to true')
    parser.add_argument('--check_words', '-c', help='Whether to name files only what is said after "This is".'
                                                    ' Enter true or false. Defaults to false')
    parser.add_argument('--merge', '-m', help='Whether to make a multi track wav file with'
                                              ' the files from the same take.'
                                              ' Enter true or false. Defaults to true')
    args = parser.parse_args()
    process_arguments = {'directory': args.directory, 'reference_number': args.reference_number}
    if args.filter:
        process_arguments['filter_words'] = convert_string_to_bool(args.filter)
    if args.check_words:
        process_arguments['check_words'] = convert_string_to_bool(args.check_words)
    if args.merge:
        process_arguments['should_merge_mics'] = convert_string_to_bool(args.merge)
    if args.directory:
        process_sounds(**process_arguments)
    else:
        parser.error("-d is required")
