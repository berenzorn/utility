import os, time

path = "e:\\backup\\sqlbackup"


def flush_dir(dir):
    now = time.time()
    for f in os.listdir(dir):
        if f.endswith in (".diff", ".trn", ".nightly", ".weekly"):
            full_path = os.path.join(dir, f)
            if os.stat(full_path).st_mtime < (now - 1209600):
                if os.path.isfile(full_path):
                    os.remove(full_path)


if __name__ == '__main__':
    for i in ("\\b1", "\\b2", "\\trade", "\\unf"):
        flush_dir(path + i)
