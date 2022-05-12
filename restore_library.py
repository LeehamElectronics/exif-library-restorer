# from win32_setctime import setctime
# from exif import Image
def load_json():
    global library_db
    with open(conf_dir) as f:
        library_db = json.load(f)

# to modify time modified: setctime("my_file.txt", 1561675987.509)
# to modify time created: os.utime("a2.py",(1330712280, 1330712292))