import errno
import json
import os
import shutil
# The wget: wget -r -k -m https://unsplash.com/?_=1432588348980&page=

UNSPLASH_SOURCE_DIR = os.path.join(os.getcwd(), "unsplash.com")
IMPORT_DIR = os.path.join(os.getcwd(), "photos")
PROCESSED_DIR = os.path.join(os.getcwd(), "unsplash_processed")
PHOTOS_DIR = os.path.join(PROCESSED_DIR, "raw")
NEW_PHOTOS_DIR = os.path.join(PHOTOS_DIR, "new")


def make_dirs(dir):
    try:
        os.makedirs(dir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

try:
    with open(os.path.join(PROCESSED_DIR, "keep.json"), 'r') as f:
        KEEP_LIST = json.load(f)["keep"]
except:
    KEEP_LIST = []


try:
    with open(os.path.join(PROCESSED_DIR, "ignore.json"), 'r') as f:
        IGNORE_LIST = json.load(f)["ignore"]
except:
    IGNORE_LIST = []


with open(os.path.join(PROCESSED_DIR, "credits.json"), 'r') as f:
    credits = json.load(f)


with open(os.path.join(PROCESSED_DIR, "import.json"), 'r') as f:
    last_import = json.load(f)


actually_kept_filenames = []

# Copy images
print("Checking sorted images. . .",)
for root, folders, files in os.walk(NEW_PHOTOS_DIR):
        for filename in files:
            if filename not in IGNORE_LIST:
                actually_kept_filenames.append(filename)

for f_new in last_import["new"]:
    if f_new not in actually_kept_filenames:
        IGNORE_LIST.append(f_new)
    else:
        KEEP_LIST.append(f_new)

        credit = credits[f_new]
        print(credit)

        # Copy to the right spot.
        credit_json = {
            "name": credit["name"],
            "credit_url": "http://unsplash.com/%s" % credit["url"]
        }

        # Create artist directory.
        artist_path = os.path.join(IMPORT_DIR, credit["name"])
        make_dirs(artist_path)

        # Copy file in
        file_path = os.path.join(NEW_PHOTOS_DIR, f_new)
        dest_path = os.path.join(artist_path, f_new)
        shutil.copyfile(file_path, dest_path)

        # Create credit
        with open(os.path.join(artist_path, "credit.json"), 'w+') as f:
            json.dump(credit_json, f)

# Save results
with open(os.path.join(PROCESSED_DIR, "keep.json"), 'w+') as f:
    json.dump({"keep": KEEP_LIST}, f)

with open(os.path.join(PROCESSED_DIR, "ignore.json"), 'w+') as f:
    json.dump({"ignore": IGNORE_LIST}, f)
