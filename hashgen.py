import os
import shutil
import hashlib
from pathlib import Path


def hashgen_file(filename):
    file = open(filename, mode='rb')
    hash = hashlib.sha1()
    for buf in file.read(128000):
        hash.update(str(buf).encode())
    return hash.hexdigest()


def file_array(path, sha1):
    if sha1:
        return [x for x in Path(path).iterdir() if x.is_file() and x.name.endswith('.sha1')]
    else:
        return [x for x in Path(path).iterdir() if x.is_file() and not x.name.endswith('.sha1')]


# def file_list(path):
#     array = file_array(path, False)
#     files_without_sha1 = []
#     for file in array:
#         sha1filename = f"{file.name}.sha1"
#         if Path(path + '\\' + file.name).exists() and not Path(path + '\\' + sha1filename).exists():
#             sha1sum = hashgen_file(file)
#             files_without_sha1.append(file.name)
#             with open(Path(path + '\\' + sha1filename), 'w', encoding="utf8") as sha1file:
#                 sha1file.write(sha1sum + " " + file.name)
#     return files_without_sha1


# def del_sha1(path):
#     array = file_array(path, True)
#     for x in array:
#         os.remove(Path(path) + "\\" + x)


# def file_check(src, dest):
#     # src_array = file_array(src, True)
#     dest_array = file_array(dest, True)
#
#     src_dict = {}
#     dst_dict = {}
#     # for x in src_array:
#     #     with open(Path(src + '\\' + x.name), 'r') as s:
#     #         string = s.readline()
#     #         src_dict[string.split(" ")[1]] = string.split(" ")[0]
#     for x in dest_array:
#         try:
#             with open(Path(src + '\\' + x.name), 'r') as s:
#                 string = s.readline()
#                 src_dict[string.split(" ")[1]] = string.split(" ")[0]
#         except FileNotFoundError:
#             pass
#         with open(Path(dest + '\\' + x.name), 'r') as d:
#             string = d.readline()
#             print(string)
#             dst_dict[string.split(" ")[1]] = string.split(" ")[0]
#     print(src_dict)
#     print(dst_dict)
#     diff_list = []
#     for name, sha in dst_dict.items():
#         try:
#             if src_dict[name] != sha:
#                 diff_list.append(name)
#                 os.remove(Path(src + '\\' + name + ".sha1"))
#         except KeyError:
#             pass
#     return diff_list


def new_files(src, dest):
    src_array = file_array(src, False)
    dest_array = file_array(dest, False)

    dest_list = [x.name for x in dest_array]
    src_list = [x.name for x in src_array]
    for x in dest_list:
        if x in src_list:
            src_list.remove(x)
    return dest_list, src_list


def exist_files_check(src, dest, f_list):
    src_dict = {}
    dst_dict = {}

    for x in f_list:
        with open(Path(src + '\\' + x + ".sha1"), 'r') as s:
            string = s.readline()
            src_dict[string.split(" ")[1]] = string.split(" ")[0]
        with open(Path(dest + '\\' + x + ".sha1"), 'r') as d:
            string = d.readline()
            dst_dict[string.split(" ")[1]] = string.split(" ")[0]
    diff_list = []
    for name, sha in dst_dict.items():
        if src_dict[name] != sha:
            diff_list.append(name)
    return diff_list


if __name__ == '__main__':
    source = "D:\\Test"
    destination = "c:\\test"

    # [0] - exist, [1] - new
    # Разделили файлы в source на которых нет в destination и которые есть
    sl = new_files(source, destination)

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
    for_copy = []
    for x in dl:
        for_copy.append(x)

    # Для новых файлов которых нет в destination
    # Считаем хэш, пишем в лист для копирования
    for x in sl[1]:
        sha1sum = hashgen_file(Path(source + '\\' + x))
        sha1filename = f"{x}.sha1"
        with open(Path(source + '\\' + sha1filename), 'w', encoding="utf8") as sha1file:
            sha1file.write(sha1sum + " " + x)
        for_copy.append(x)

    # Пишем лист для копирования с хэшами в destination
    for i in for_copy:
        shutil.copy(source + '\\' + i, destination)
        shutil.copy(source + '\\' + i + ".sha1", destination)

# TODO копировать только новые файлы (append)
# TODO удалять файлы в destination, которые удалены в source (full-sync)
