from datetime import datetime
import shutil
import os

local_path = "f:\\sqlbackup"

unc_path = "//pdc/backup/sqlbackup"


def copy_dir(dir, add):
    unc_add = "/" + add[1:]
    for f in os.listdir(dir):
        if f.endswith in (".diff", ".trn", ".weekly", ".nightly"):
            full_path = os.path.join(dir, f)
            if os.path.isfile(full_path):
                time_now = datetime.now()
                text_str = time_now.strftime('%d-%m-%Y %H:%M:%S') + \
                           " Copying " + f + " ---> " + unc_path + unc_add + "\n"
                with open("copy_sql_bckp.log", 'a') as file:
                    file.write(text_str)
                shutil.copy2(full_path, unc_path + unc_add)


if __name__ == '__main__':
    for i in ("\\b1", "\\b2", "\\trade", "\\unf"):
        copy_dir(local_path + i, i)
