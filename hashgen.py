import os
import hashlib
import argparse
import shutil
import logging
from pathlib import Path


def file_array(path):
    return [file for file in Path(path).iterdir()
            if file.is_file() and not file.name.endswith('.sha1')]


def hashgen_file(filename, buffsize, quiet, log):
    filehash = hashlib.sha1()
    if not quiet:
        print(f"Generating hash for: {filename}")
    if log:
        logging.debug(f"Generating hash for: {filename}")
    with open(filename, mode='rb') as file:
        while True:
            try:
                buffer = file.read(buffsize)
            except MemoryError:
                print("Not enough memory.")
                logging.error("Not enough memory.")
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
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--append", action="store_true", help="Hash & copy new files only. Default")
    group.add_argument("-s", "--sync", action="store_true", help="Hash & copy new and changed files")
    parser.add_argument("-d", "--delete", action="store_true", help="Sync & delete old files in destination")
    parser.add_argument("-nc", "--nocopy", action="store_true", help="No copy, just hash source files")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-b", type=int, dest="buffer", metavar=" BUFFER", help="Buffer size in MB", default=100)
    parser.add_argument("-l", type=str, dest="log", metavar=" LOG", help="Write output to log file")
    args = parser.parse_args()
    if args.log:
        logging.basicConfig(filename=args.log, filemode='a', format='%(asctime)s %(message)s',
                            datefmt='%m.%d.%Y %H:%M:%S', level=logging.DEBUG)
    if args.buffer <= 0:
        args.buffer = 1
    buffer_size = args.buffer * 1024**2

    if not args.sync:
        args.append = True

    if args.log:
        logging.debug("-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-")
        logging.debug(f"args.source={args.source}, args.destination={args.destination}")
        logging.debug(f"args.append={args.append}, args.sync={args.sync}, args.nocopy={args.nocopy}")
        logging.debug(f"args.delete={args.delete}, args.quiet={args.quiet}, args.buffer={args.buffer}")

    if(Path(args.source).exists()) and (Path(args.destination).exists()):
        # 0 - files in src and dst, 1 - new in src, 2 - not in src
        source_list = new_files(args.source, args.destination)
    else:
        print("No such source or destination folder.")
        if args.log:
            logging.error("No such source or destination folder.")
        raise SystemExit(0)

    if not args.nocopy:
        if not args.quiet:
            if source_list[1]:
                print("\nNew files in source: ")
                for i in source_list[1]:
                    print(i)
        if args.log:
            if source_list[1]:
                logging.debug("")
                logging.debug("New files in source:")
                for i in source_list[1]:
                    logging.debug(f"{i}")

    for_copy = []
    if args.sync:
        if source_list[2]:
            if not args.quiet:
                print("\nFiles that are not in the source: ")
                for x in source_list[2]:
                    print(x)
                if args.delete:
                    print("\nRemoving these files...")
            if args.log:
                logging.debug("")
                logging.debug("Files that are not in the source:")
                for x in source_list[2]:
                    logging.debug(f"{x}")
                if args.delete:
                    logging.debug("")
                    logging.debug("Removing these files...")

            for x in source_list[2]:
                if args.delete:
                    try:
                        os.remove(Path(f"{args.destination}\\{x}"))
                        os.remove(Path(f"{args.destination}\\{x}.sha1"))
                    except FileNotFoundError:
                        pass
                source_list[0].remove(x)
    if args.sync:
        if not args.quiet:
            print()
        if args.log:
            logging.debug("")
        for x in source_list[0]:
            try:
                os.remove(Path(f"{args.source}\\{x}.sha1"))
            except FileNotFoundError:
                pass
            sha1_write(args.source, x, buffer_size, args.quiet, args.log)

        dest_list = exist_files_check(args.source, args.destination, source_list[0],
                                      buffer_size, args.quiet, args.log)
        if dest_list:
            for x in dest_list:
                for_copy.append(x)

    if args.append:
        if not args.quiet:
            print()
        if args.log:
            logging.debug("")
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
            logging.debug("")
        for x in for_copy:
            if not args.quiet:
                print(f"Copying file {x}")
            if args.log:
                logging.debug(f"Copying file {x}")
            shutil.copy(f"{args.source}\\{x}", args.destination)
            shutil.copy(f"{args.source}\\{x}.sha1", args.destination)
        # logging.debug("")
