import os
import shutil
import hashlib
import argparse
from pathlib import Path


def hashgen_file(filename):
    hash = hashlib.sha1()
    if not args.quiet:
        print(f"Generating hash for: {filename}")
    with open(filename, mode='rb') as file:
        while True:
            buffer = file.read(524288000)
            hash.update(buffer)
            if not buffer:
                break
    return hash.hexdigest()


def file_array(path, is_sha1_file):
    if is_sha1_file:
        try:
            return [file for file in Path(path).iterdir() if file.is_file() and file.name.endswith('.sha1')]
        except FileNotFoundError:
            return False
    else:
        try:
            return [file for file in Path(path).iterdir() if file.is_file() and not file.name.endswith('.sha1')]
        except FileNotFoundError:
            return False


def new_files(src, dst):
    """
    :return: files list that are in both folders
         and files list that are only in source
    """
    src_array = file_array(src, False)
    dst_array = file_array(dst, False)

    try:
        dst_list = [file.name for file in dst_array]
        src_list = [file.name for file in src_array]
    except TypeError:
        return False

    for file in dst_list:
        if file in src_list:
            src_list.remove(file)
    return dst_list, src_list


def exist_files_check(src, dst, file_list):
    """
    Checking hashes of shared file_list for source and destination.
    :return: files list in source whose hash is different from destination
    """
    src_dict = {}
    dst_dict = {}

    for file in file_list:
        try:
            with open(Path(f"{src}\\{file}.sha1"), 'r') as s:
                string = s.readline()
                src_dict[string.split("  ")[1]] = string.split("  ")[0]
            with open(Path(f"{dst}\\{file}.sha1"), 'r') as d:
                string = d.readline()
                dst_dict[string.split("  ")[1]] = string.split("  ")[0]
        except FileNotFoundError:
            return False

    diff_list = []
    for name, sha in dst_dict.items():
        if src_dict[name.rstrip()] != sha:
            diff_list.append(name)
    return diff_list


if __name__ == '__main__':
    """
    1 - sync mode. Erase hashes in source, calc again.
    Files in the source that don't match the destination - put into copy list.
    New files that are not in the destination - calc the hash, put into copy list.
    2 - append mode.
    Files in the source that don't match the destination - do not touch.
    New files that are not in the destination - calc the hash, put into copy list.
    3 - full sync mode
    Sync mode + Delete files in the destination that are not in the source.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("-s", "--sync", action="store_true", help="Hash & copy new and changed files")
    parser.add_argument("-a", "--append", action="store_true", help="Hash & copy new files only. Default.")
    parser.add_argument("-f", "--fullsync", action="store_true", help="Full sync source and destination")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    if not args.sync and not args.append and not args.fullsync:
        args.append = True

    print()
    if(Path(f"{args.source}")) and (Path(f"{args.destination}")):
        sl = new_files(args.source, args.destination)
    else:
        print("Path is not found")
        sl = False

    if sl:
        if not args.quiet:
            if sl[1]:
                print("New files in source: ")
                for i in sl[1]:
                    print(i)
                print()

        for_copy = []

        if args.sync or args.fullsync:
            vv = new_files(args.destination, args.source)
            if len(vv[1]):
                if not args.quiet:
                    print("Files that are not in the source: ")
                    for x in vv[1]:
                        print(x)
                    print()
            for x in vv[1]:
                if args.fullsync:
                    if not args.quiet:
                        print("Removing these files...")
                        print()
                    try:
                        os.remove(Path(f"{args.destination}\\{x}.sha1"))
                        os.remove(Path(f"{args.destination}\\{x}"))
                    except FileNotFoundError:
                        pass
                sl[0].remove(x)

        if args.sync or args.fullsync:
            for x in sl[0]:
                os.remove(Path(f"{args.source}\\{x}.sha1"))
                sha1sum = hashgen_file(Path(f"{args.source}\\{x}"))
                with open(Path(f"{args.source}\\{x}.sha1"), 'w', encoding="utf8") as sha1file:
                    sha1file.write(sha1sum + "  " + x)
            dl = exist_files_check(args.source, args.destination, sl[0])
            for x in dl:
                for_copy.append(x)

        for x in sl[1]:
            sha1sum = hashgen_file(Path(f"{args.source}\\{x}"))
            with open(Path(f"{args.source}\\{x}.sha1"), 'w', encoding="utf8") as sha1file:
                sha1file.write(sha1sum + "  " + x)
            for_copy.append(x)

        print()
        for x in for_copy:
            if not args.quiet:
                print(f"Copying file {x}")
            shutil.copy(f"{args.source}\\{x}", args.destination)
            shutil.copy(f"{args.source}\\{x}.sha1", args.destination)

