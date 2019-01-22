import shutil, time
from pathlib import Path
from datetime import datetime

path = Path("e:\\backup")
old_day = datetime.fromtimestamp(time.time()-259200).strftime("%d.%m.%Y")
print(old_day)
list_dir = [x.relative_to('e:\\backup') for x in path.iterdir() if x.is_dir()]

for d in list_dir:
	print(str(d))

for dir in list_dir:
	if str(dir) == old_day:
		path_for_delete = str(path) + "\\" + str(dir)
		shutil.rmtree(path_for_delete, ignore_errors=True)
