import sys
from pathlib import Path
import os
import shutil
import zipfile
import tarfile


DIR_PATH = ""

EXTENSIONS = {"images": ["jpeg", "png", "jpg", "svg"],
              "video": ["avi", "mp4", "mov", "mpk"],
              "documents": ["doc", "docx", "txt", "pdf", "xlsx", "pptx"],
              "audio": ["mp3", "ogg", "wav", "amr"],
              "archives": ["zip", "gz", "tar"],
              "unknown": []}


CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")


TRANS = {}


for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()


def get_folder_name():
    """
    This function create a path to the folder
    """
    if len(sys.argv) == 2:
        global DIR_PATH
        DIR_PATH = sys.argv[1]
    else:
        DIR_PATH = input("Please type a path to the folder you want to clean")


if not DIR_PATH:
    get_folder_name()


def normalize(name):
    """
    This function normalize file's name
    """
    result = ""
    try:
        for letter in name.split(".")[0]:
            if letter.lower() not in CYRILLIC_SYMBOLS and letter.lower() not in TRANSLATION and letter not in "1234567890cwxWXC":
                result += "_"
            elif letter.lower() not in CYRILLIC_SYMBOLS:
                result += letter
            else:
                result += TRANS[ord(letter)]
    except:
        return name
    result += "." + name.split(".")[1]
    return result


names_dict = {"images": [],
              "documents": [],
              "audio": [],
              "video": [],
              "archives": [],
              "unknown": []}

known_extension = set()
unknown_extension = set()


def get_and_rename_files_names(path):
    """
    This function rename files in order way 
    """
    path_obj = Path(path)
    for entry in path_obj.iterdir():
        if entry.is_file():
            try:
                for key, values in EXTENSIONS.items():
                    if str(entry).split(".")[1].lower() in values:
                        os.chdir(path_obj)
                        os.rename(entry.name, normalize(entry.name))
                        names_dict[key].append(normalize(entry.name))
                        known_extension.add(str(entry).split(".")[1].lower())
                        break
                if str(entry).split(".")[1].lower() not in known_extension:
                    os.chdir(path_obj)
                    os.rename(entry.name, normalize(entry.name))
                    names_dict["unknown"].append(normalize(entry.name))
                    unknown_extension.add(str(entry).split(".")[1].lower())
            except IndexError as e:
                names_dict["unknown"].append(entry.name)
        else:
            get_and_rename_files_names(f"{path}\{entry.name}")


get_and_rename_files_names(DIR_PATH)

FOLDER_NAMES = list([key for key, value in names_dict.items() if value])


def create_folders(path):
    """
    This function create empty folders for files we have
    """
    for key, values in names_dict.items():
        if values:
            for value in values:
                print("Path ", path, "key ", key,
                      "value ", value.split('.')[1].lower())
                os.makedirs(
                    rf"{path}\{key}\{value.split('.')[1].lower()}", exist_ok=True)


create_folders(DIR_PATH)


def remove_files(path):
    """
    This function remove files to correct directory
    """
    counter = 0
    obj_path = Path(path)
    for file in obj_path.iterdir():
        try:
            if file.is_dir():
                if file.name in FOLDER_NAMES:
                    continue
                else:
                    remove_files(f'{path}\{file.name}')
                try:
                    os.remove(file)
                except:
                    print("Folder is not empty")
            elif file.is_file():
                for key, values in names_dict.items():
                    if file.name in values:
                        print(file)
                        print(f'{DIR_PATH}\documents')
                        try:
                            shutil.move(
                                rf"{file}", rf"{DIR_PATH}\{key}\{str(file).split('.')[1].lower()}")
                        except shutil.Error:
                            os.rename(str(file), str(
                                f'{str(file).split(".")[0]}_{counter}.{str(file).split(".")[1]}'))
                            new_name = str(
                                f'{str(file).split(".")[0]}_{counter}.{str(file).split(".")[1]}')
                            shutil.move(
                                rf"{new_name}", rf"{DIR_PATH}\{key}\{str(file).split('.')[1].lower()}")
                            counter += 1
        except Exception as e:
            print(e)


def deleted_folders(path):
    """
    This func delete empty folders
    """
    obj_path = Path(path)
    for file in obj_path.iterdir():
        try:
            if file.is_dir():
                deleted_folders(f'{path}\{file.name}')
                print(file)
                os.rmdir(file)
        except:
            print("Folder is not empty")


remove_files(DIR_PATH)
deleted_folders(DIR_PATH)

existed_archives = set([value.split(".")[1]
                        for value in names_dict["archives"]])


def unpack_archives(path):
    """
    This func unpach archives
    """
    for extension in existed_archives:
        if extension == "zip":
            for file in os.listdir(rf"{path}\archives\zip"):
                data_zip = zipfile.ZipFile(rf"{path}\archives\zip\{file}", 'r')
                os.makedirs(
                    rf"{path}\archives\zip\{file.split('.')[0]}", exist_ok=True)
                data_zip.extractall(
                    path=rf"{path}\archives\zip\{file.split('.')[0]}")
        elif extension == "tar":
            try:
                for file in os.listdir(rf"{path}\archives\tar"):
                    with tarfile.open(
                            rf"{path}\archives\tar\{file}", 'r') as data_tar:
                        os.makedirs(
                            rf"{path}\archives\tar\{file.split('.')[0]}", exist_ok=True)
                        data_tar.extractall(
                            path=rf"{path}\archives\tar\{file.split('.')[0]}")
            except tarfile.ReadError as e:
                print("Something wrong with your archive:", e)


if existed_archives:
    unpack_archives(DIR_PATH)
