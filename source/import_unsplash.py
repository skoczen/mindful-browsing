import errno
import json
import os
import shutil

# To Use:
# 1. Run wget until it finishes:
#       wget -r -k -m https://unsplash.com/?_=1432588348980&page=
# 2. run import_unsplash.py
# 3. delete any photos from the "new" folder you don't want to keep.
# 4. run process_sorted_photos.py
# 5. run fab bundle_images / fab deploy like normal!


UNSPLASH_SOURCE_DIR = os.path.join(os.getcwd(), "unsplash.com")
PHOTOS_DIR = os.path.join(UNSPLASH_SOURCE_DIR, "photos")
PROCESSED_DIR = os.path.join(os.getcwd(), "unsplash_processed",)
TARGET_DIR = os.path.join(PROCESSED_DIR, "raw")


def make_dirs(dir):
    try:
        os.makedirs(dir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

make_dirs(PROCESSED_DIR)
make_dirs(TARGET_DIR)
make_dirs(os.path.join(TARGET_DIR, "keep"))
make_dirs(os.path.join(TARGET_DIR, "new"))


try:
    with open(os.path.join(PROCESSED_DIR, "keep.json"), 'r') as f:
        KEEP_LIST = json.load(f)["keep"]
except:
    KEEP_LIST = []


try:
    with open(os.path.join(PROCESSED_DIR, "ignore.json"), 'r') as f:
        IGNORE_LIST = json.load(f)["ignore"]
except:
    IGNORE_LIST = [".DS_Store", "photos.jpg"]

filenames = []
new_filenames = []
credits = {}


# Copy images
print("Copying images. . .",)
for root, folders, files in os.walk(PHOTOS_DIR):
        for filename in files:
            if filename not in IGNORE_LIST:
                file_name = "%s.jpg" % root.split("/")[-1]
                if file_name not in IGNORE_LIST:
                    file_path = os.path.join(root, filename)
                    if filename in KEEP_LIST:
                        dest_path = os.path.join(TARGET_DIR, "keep", file_name)
                    else:
                        dest_path = os.path.join(TARGET_DIR, "new", file_name)
                        new_filenames.append(file_name)

                    shutil.copyfile(file_path, dest_path)
                    filenames.append(file_name)
                    print("Copied %s" % file_name)

            else:
                print("Ignored %s" % filename)


# Create one crazy html file for parsing
all_html = ""

for root, folders, files in os.walk(UNSPLASH_SOURCE_DIR):
        for filename in files:
            # print(root)
            # print(root, filename, folders)
            # print(len(root.split("/")))
            if len(root.split("/")) <= 8 and ".DS" not in filename:
            # if "photos" not in root and "download" not in root and "photos" not in filename:
                with open(os.path.join(root, filename), 'r') as f:
                    contents = f.read()
                    if "ShowStatusBar" in contents:
                        print("\n\n\n YO, %s is weird" % filename)
                    all_html = all_html + "\n%s" % contents
                    print("Adding %s") % filename

with open(os.path.join(PROCESSED_DIR, "all.html"), 'w+') as f:
    f.write(all_html)

for f in filenames:
    slug = "href=\"/photos/%s/download\">Download</a>" % f.split(".")[0]
    # print(slug)
    index = all_html.find(slug)
    if index == -1:
        slug = "href=\"/photos/%s/download\" target=\"_blank\">Download</a>" % f.split(".")[0]
        index = all_html.find(slug)
        if index == -1:
            print "missing %s" % slug
            break

    # <a href="/photos/5iPhUVPYWsw/download" targauet="_blank">Download</a> / 
    # By <a href="/garrett_vc">Garrett Carroll</a>
    next_a = all_html.find("</a>", index+1)
    close_a = all_html.find("</a>", next_a+1)

    start = '</a> / By <a href="/'
    credit_str = all_html[next_a+len(start):close_a].strip().replace("\n", "")
    parts = credit_str.split('">')
    url = parts[0]
    name = parts[1]
    credit = {
        "name": name.title(),
        "url": url,
        "image_name": f,
    }
    credits[f] = credit

with open(os.path.join(PROCESSED_DIR, "import.json"), 'w+') as f:
    json.dump({"all": filenames, "new": new_filenames}, f)

with open(os.path.join(PROCESSED_DIR, "credits.json"), 'w+') as f:
    json.dump(credits, f)

with open(os.path.join(PROCESSED_DIR, "keep.json"), 'w+') as f:
    json.dump({"keep": KEEP_LIST}, f)

with open(os.path.join(PROCESSED_DIR, "ignore.json"), 'w+') as f:
    json.dump({"ignore": IGNORE_LIST}, f)
