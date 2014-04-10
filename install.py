import os
import sys
import shutil

def install_sublime_plugin(packages_path, rewrite=False):
    """Writes plugin files to appropriate destination. If rewrite is True existing files will be overwritten"""
    not_copied = []
    source_path = os.path.dirname(os.path.realpath(__file__))
    for folder in os.listdir(source_path):
        folder_to_copy = os.path.join(packages_path, folder)
        source_folder = os.path.join(source_path, folder)
        if not os.path.isdir(source_folder) or folder.startswith("."):
            continue
        if not os.path.exists(folder_to_copy):
            os.mkdir(folder_to_copy)
        for file in os.listdir(folder):
            source = os.path.join(source_folder, file)
            destination = os.path.join(folder_to_copy, file)
            file_exists = os.path.exists(destination)
            if file_exists and not rewrite:
                not_copied.append("{0} -> {1}".format(source, destination))
            if not file_exists or rewrite:
                try:
                    shutil.copy(source, destination)
                    print("{0} -> {1}".format(source, destination))
                except IOError:
                    print("Cannot copy file {0} to the folder {1}.".format(source, folder_to_copy))
    return not_copied

HELP_MESSAGE = """install.py [key] path

[key] - Command key (optional). Available keys:
    -r Overwrite existing files.
    -h Help.
path - Full path to Sublime Text Packages folder. Write this value in quotes."""

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Specify path to Packages folder as first argument. Run script with -h key for help.')
    elif sys.argv[1] == "-r":
        if len(sys.argv) == 3:
            install_sublime_plugin(sys.argv[2], True)
        else:
            print('Specify path to Packages folder as second argument. Run script with -h key for help.')
    elif sys.argv[1] == "-h":
        print(HELP_MESSAGE)
    else:
        not_copied_files = install_sublime_plugin(sys.argv[1])
        if len(not_copied_files) > 0:
            print('Following files already exist in destination. '
                  'Copy them manually or add their contents to existing files. Or run the program with -r key if you '
                  'want to replace existing files. Run script with -h key for help.')
            for not_copied in not_copied_files:
                print(not_copied)
