import shutil
import hashlib
from pathlib import Path


def hashgen_file(filename):
    file = open(filename, mode='rb')
    hash = hashlib.sha1()
    for buf in file.read(128):
        hash.update(str(buf).encode())
    return hash.hexdigest()


def file_list(path):
    array = [x for x in Path(path).iterdir()
             if x.is_file() and not x.name.endswith('.sha1')]
    files_without_sha1 = []
    for file in array:
        sha1filename = f"{file.name}.sha1"
        if Path(path + '\\' + file.name).exists() and not Path(path + '\\' + sha1filename).exists():
            sha1sum = hashgen_file(file)
            files_without_sha1.append(file.name)
            with open(Path(path + '\\' + sha1filename), 'w', encoding="utf8") as sha1file:
                sha1file.write(sha1sum + "  " + file.name)
    return files_without_sha1


if __name__ == '__main__':
    source = "D:\\Test"
    destination = "c:\\test"
    files_for_copy = file_list(source)
    for i in files_for_copy:
        shutil.copy(source + '\\' + i, destination)
        shutil.copy(source + '\\' + i + ".sha1", destination)

