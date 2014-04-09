
import os
import sys
import shutil

def install_sublime_plugin(packages_path, files_to_copy, source_path=None):
    """Hardly writes plugin files to appropriate destination without possibility to add or overwrite default settings"""
    if source_path is None:
        source_path = os.path.dirname(__file__)
    for folder in files_to_copy:
        folder_to_copy = os.path.join(packages_path, folder)
        if not os.path.exists(folder_to_copy):
            os.mkdir(folder_to_copy)
        for file in files_to_copy[folder]:
            source = os.path.join(source_path, file)
            destination = os.path.join(folder_to_copy, file)
            try:
                shutil.copy(source, destination)
                print("{0} -> {1}".format(source, destination))
            except IOError:
                print("Cannot to copy file {0} to the folder {1}.".format(source, folder_to_copy))

# all files and appropriate destination directories should be listed here
FILES = {
    "JBehaveStory": [
        "JBehaveStory.tmLanguage",
        "JBehaveStory.tmTheme",
        "JBehaveStoryPlugin.py",
        "README.md"
    ],
    "User": [
        "Default (Windows).sublime-keymap",
        "Default (Linux).sublime-keymap",
        "Default (OSX).sublime-keymap",
        "JBehaveStory.sublime-settings"
    ],
}

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("""Specify path to Packages folder as first argument (mandatory)
        and path to plugin files folder as second argument (optional).""")
    elif len(sys.argv) == 2:
        install_sublime_plugin(sys.argv[1], FILES)
    elif len(sys.argv) == 3:
        install_sublime_plugin(sys.argv[1], FILES, sys.argv[2])