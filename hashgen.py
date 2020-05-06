import os
import hashlib
import argparse
import shutil
from pathlib import Path


def file_array(path):
    return [file for file in Path(path).iterdir()
            if file.is_file() and not file.name.endswith('.sha1')]

def hashgen_file(filename, buffsize, quiet, log):
    filehash = hashlib.sha1()
    if not quiet:
        print(f"Generating hash for: {filename}")
    if log:
        with open("hashgen.log", 'a') as log:
            log.write(f"Generating hash for: {filename}\n")
    with open(filename, mode='rb') as file:
        while True:
            try:
                buffer = file.read(buffsize)
            except MemoryError:
                print("Not enough memory.")
                with open("hashgen.log", 'a') as log:
                    log.write("Not enough memory.\n")
                raise SystemExit(0)
            filehash.update(buffer)
            if not buffer:
                break
    return filehash.hexdigest()

def new_files(src, dst):
    """
    :return: files list that are in both folders,
    files only in source and only in destination
    """
    src_array = file_array(src)
    dst_array = file_array(dst)
    src_list = [file.name for file in src_array]
    dst_list = [file.name for file in dst_array]
    sd_diff = sorted(list(set(src_list) - set(dst_list)))
    ds_diff = sorted(list(set(dst_list) - set(src_list)))
    # 0 - files in src and dst, 1 - new in src, 2 - not in src
    return dst_list, sd_diff, ds_diff

def sha1_write(path, name, buffer, quiet, log):
    sha1sum = hashgen_file(Path(f"{path}\\{name}"), buffer, quiet, log)
    with open(Path(f"{path}\\{name}.sha1"), 'w', encoding="utf8") as sha1file:
        sha1file.write(f"{sha1sum}   {name}")  # ← 3 spaces!
    return sha1sum

def exist_files_check(src, dst, file_list, buffer, quiet, log):
    """
    Checking hashes in shared file_list for source and destination.
    :return: files list in source whose hash is different from destination
    OR if file in destination has no hash.
    """
    def dict_mount(path, name, buffer, quiet, log, need_update):
        try:
            with open(Path(f"{path}\\{name}.sha1"), 'r') as s:
                string = s.readline()
        except FileNotFoundError:
            return sha1_write(path, name, buffer, quiet, log) if need_update else 0
        return string.split("   ")[0]  # ← 3 spaces!

    src_dict = {}
    dst_dict = {}
    for file in file_list:
        src_dict[file] = dict_mount(src, file, buffer, quiet, log, True)
        dst_dict[file] = dict_mount(dst, file, buffer, quiet, log, False)

    diff_list = [name for name, sha1 in dst_dict.items() if src_dict[name.rstrip()] != sha1]
    return diff_list


if __name__ == '__main__':
    """
    1 - append mode.
    New files that are not in the destination - calc the hash, put into copy list.
    2 - sync mode. Erase hashes in source, calc again.
    Append mode +
    Modified files in the source compared to the destination - put into copy list.
    Files in the destination without hash - put file in the source into copy list.
    3 - full sync mode. Erase hashes in source, calc again.
    Sync mode +
    Delete files in the destination that are not in the source.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--append", action="store_true", help="Hash-copy new files only. Default.")
    group.add_argument("-s", "--sync", action="store_true", help="Hash-copy new and changed files")
    group.add_argument("-f", "--fullsync", action="store_true", help="Full sync source and destination")
    group.add_argument("-nc", "--nocopy", action="store_true", help="No sync, just hash source files")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-l", "--log", action="store_true", help="Write output to log file")
    parser.add_argument("-b", type=int, dest="buffer", metavar=" BUFFER", help="Buffer size in MB", default=100)
    args = parser.parse_args()

    if args.buffer <= 0:
        args.buffer = 1
    buffer_size = args.buffer * 1024**2

    if not args.sync and not args.fullsync:
        args.append = True

    if args.log:
        with open("hashgen.log", 'a') as log:
            log.write("\n----------\n")
            log.write("New run...\n")


    if(Path(args.source).exists()) and (Path(args.destination).exists()):
        # 0 - files in src and dst, 1 - new in src, 2 - not in src
        source_list = new_files(args.source, args.destination)
    else:
        print("No such source or destination folder.")
        if args.log:
            with open("hashgen.log", 'a') as log:
                log.write("No such source or destination folder.\n")
        raise SystemExit(0)

    if not args.nocopy:
        if not args.quiet:
            if source_list[1]:
                print("\nNew files in source: ")
                for i in source_list[1]:
                    print(i)
        if args.log:
            if source_list[1]:
                with open("hashgen.log", 'a') as log:
                    log.write("\nNew files in source: \n")
                    for i in source_list[1]:
                        log.write(f"{i}\n")


    for_copy = []
    if args.sync or args.fullsync:
        if source_list[2]:
            if not args.quiet:
                print("\nFiles that are not in the source: ")
                for x in source_list[2]:
                    print(x)
                if args.fullsync:
                    print("\nRemoving these files...")
            if args.log:
                with open('hashgen.log', 'a') as log:
                    log.write("\nFiles that are not in the source: \n")
                    for x in source_list[2]:
                        log.write(f"{x}\n")
                    if args.fullsync:
                        log.write("\nRemoving these files...\n")
            for x in source_list[2]:
                if args.fullsync:
                    try:
                        os.remove(Path(f"{args.destination}\\{x}"))
                        os.remove(Path(f"{args.destination}\\{x}.sha1"))
                    except FileNotFoundError:
                        pass
                source_list[0].remove(x)
    if args.sync or args.fullsync:
        if not args.quiet:
            print()
        if args.log:
            with open("hashgen.log", 'a') as log:
                log.write("\n")
        for x in source_list[0]:
            try:
                os.remove(Path(f"{args.source}\\{x}.sha1"))
            except FileNotFoundError:
                pass
            sha1_write(args.source, x, buffer_size, args.quiet, args.log)
        dest_list = exist_files_check(args.source, args.destination, source_list[0], buffer_size, args.quiet, args.log)
        if dest_list:
            for x in dest_list:
                for_copy.append(x)

    if args.append and not args.quiet:
        print()
    if args.append and args.log:
        with open("hashgen.log", 'a') as log:
            log.write("\n")
    if args.nocopy:
        # this one + [1] -> all files in source
        for x in sorted(list(set(source_list[0]) - set(source_list[2]))):
            sha1_write(args.source, x, buffer_size, args.quiet, args.log)
    for x in source_list[1]:
        sha1_write(args.source, x, buffer_size, args.quiet, args.log)
        for_copy.append(x)

    if not args.nocopy:
        if not args.quiet:
            print()
        if args.log:
            with open("hashgen.log", 'a') as log:
                log.write("\n")
        for x in for_copy:
            if not args.quiet:
                print(f"Copying file {x}")
            if args.log:
                with open('hashgen.log', 'a') as log:
                    log.write(f"Copying file {x}\n")
            shutil.copy(f"{args.source}\\{x}", args.destination)
            shutil.copy(f"{args.source}\\{x}.sha1", args.destination)
