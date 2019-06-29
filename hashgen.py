import os
import shutil
import hashlib
from pathlib import Path


def hashgen_file(filename):
    """
    :return: file sha1 hash
    """
    hash = hashlib.sha1()
    with open(filename, mode='rb') as file:
        for buf in file.read(128000):
            hash.update(str(buf).encode())
    return hash.hexdigest()


def file_array(path, is_sha1_file):
    """
    :param path: working directory
    :param is_sha1_file: .sha1 or any other
    :return: file list
    """
    if is_sha1_file:
        return [file for file in Path(path).iterdir() if file.is_file() and file.name.endswith('.sha1')]
    else:
        return [file for file in Path(path).iterdir() if file.is_file() and not file.name.endswith('.sha1')]


def new_files(src, dst):
    """
    :return: список файлов, которые есть в обоих папках,
    и список файлов, которые есть только в source
    """
    src_array = file_array(src, False)
    dst_array = file_array(dst, False)

    dst_list = [file.name for file in dst_array]
    src_list = [file.name for file in src_array]
    for file in dst_list:
        if file in src_list:
            src_list.remove(file)
    return dst_list, src_list


def exist_files_check(src, dst, file_list):
    """
    Сверяем хэши общих файлов для source и destination.
    :return: лист файлов source,
    чей хэш изменился по сравнению с destination
    """
    src_dict = {}
    dst_dict = {}

    for file in file_list:
        with open(Path(src + '\\' + file + ".sha1"), 'r') as s:
            string = s.readline()
            src_dict[string.split(" ")[1]] = string.split(" ")[0]
        with open(Path(dst + '\\' + file + ".sha1"), 'r') as d:
            string = d.readline()
            dst_dict[string.split(" ")[1]] = string.split(" ")[0]
    diff_list = []
    for name, sha in dst_dict.items():
        if src_dict[name] != sha:
            diff_list.append(name)
    return diff_list


if __name__ == '__main__':
    """
    1 - sync mode. Стереть в source хэши, посчитать заново.
    Файлы в source, не совпадающие с destination - в лист для копирования.
    Для новых файлов которых нет в destination - Считаем хэш, пишем в лист для копирования
    2 - append mode.
    Файлы в source, не совпадающие с destination не трогаем.
    Для новых файлов которых нет в destination - Считаем хэш, пишем в лист для копирования
    3 - full sync mode
    Стереть в destination файлы, которых нет в source.
    Стереть в source хэши, посчитать заново.
    Файлы в source, не совпадающие с destination - в лист для копирования.
    Для новых файлов которых нет в destination - Считаем хэш, пишем в лист для копирования
    """

    # TODO argparse

    source = "D:\\Test"
    destination = "c:\\test"

    # 1 - sync
    # 2 - append
    # 3 - full sync
    mode = 1

    # [0] - exist, [1] - new
    # Разделили файлы в source на которых нет в destination и которые есть

    # что добавить в dest
    sl = new_files(source, destination)
    print(sl)

    for_copy = []

    # Если full sync, убираем из destination файлы
    if mode == 1 or mode == 3:
        vv = new_files(destination, source)
        print(vv)
        for x in vv[1]:
            if mode == 3:
                os.remove(Path(destination + '\\' + x))
                os.remove(Path(destination + '\\' + x + ".sha1"))
            sl[0].remove(x)

    print(sl)

    if mode == 1 or mode == 3:
        # Работаем с имеющимися там и там файлами
        # Стереть в source хэши, посчитать заново
        for x in sl[0]:
            os.remove(Path(source + '\\' + x + ".sha1"))
            sha1sum = hashgen_file(Path(source + '\\' + x))
            sha1filename = f"{x}.sha1"
            with open(Path(source + '\\' + sha1filename), 'w', encoding="utf8") as sha1file:
                sha1file.write(sha1sum + " " + x)
        # Сравниваем хэши имеющихся файлов
        dl = exist_files_check(source, destination, sl[0])

        # Файлы в source, не совпадающие с destination - в лист для копирования
        for x in dl:
            for_copy.append(x)

        print(for_copy)

    # Для новых файлов которых нет в destination
    # Считаем хэш, пишем в лист для копирования
    for x in sl[1]:
        sha1sum = hashgen_file(Path(source + '\\' + x))
        sha1filename = f"{x}.sha1"
        with open(Path(source + '\\' + sha1filename), 'w', encoding="utf8") as sha1file:
            sha1file.write(sha1sum + " " + x)
        for_copy.append(x)

    print(for_copy)

    # Пишем лист для копирования с хэшами в destination
    for i in for_copy:
        shutil.copy(source + '\\' + i, destination)
        shutil.copy(source + '\\' + i + ".sha1", destination)

