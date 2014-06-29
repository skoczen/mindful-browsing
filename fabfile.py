from fabric.api import *
import datetime
import distutils.core
import errno
import hashlib
import json
import os
import shutil

IMAGES_SOURCE_DIR = os.path.abspath(os.path.join(os.getcwd(), "source/photos"))
SITE_BUILD_DIR = os.path.abspath(os.path.join(os.getcwd(), "build"))
SITE_SOURCE_DIR = os.path.abspath(os.path.join(os.getcwd(), "site"))
PHOTO_EXTENSIONS = ["jpg", "jpeg", "png", "gif",]
PHOTO_DATA_FILENAME = "photos.json"
TIME_BETWEEN_IMAGES = datetime.timedelta(days=2)
BASE_URL = "http://mindfulbrowsing.org/photos/"
SCP_TARGET = os.environ["SCP_TARGET"]
PHOTO_DATA_JS_PATH = os.path.abspath(os.path.join(os.getcwd(), "extension", "js", "photoInfo.js"))

def _ensure_build_directory():
    try:
        os.makedirs(SITE_BUILD_DIR)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

    try:
        os.makedirs(os.path.join(SITE_BUILD_DIR, "photos"))
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

def _file_sha(file_path):
    sha1 = hashlib.sha1()
    f = open(file_path, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()

def _datetime_to_ms_since_epoch(dt):
    return int(dt.strftime("%s")) * 1000 


def _ms_since_epoch_to_datetime(ms):
    return datetime.datetime.fromtimestamp(ms/1000)

def bundle_images():
    _ensure_build_directory()

    try:
        photo_data_file = os.path.join(os.getcwd(), SITE_BUILD_DIR, PHOTO_DATA_FILENAME,)
        photos_info = json.load(open(photo_data_file, "r"))
        next_start_date = _ms_since_epoch_to_datetime(photos_info["photos"][-1]["start_date"])
    except:
        photos_info = {
            "photos": []
        }
        next_start_date = datetime.datetime.now()

    for root, folders, files in os.walk(IMAGES_SOURCE_DIR):
        for filename in files:
            photo_dir = False
            credit = {}
            if os.path.exists(os.path.join(root, "credit.json")):
                photo_dir = True
                credit = json.load(open(os.path.join(root, "credit.json")))

            if photo_dir and any([ext in filename for ext in PHOTO_EXTENSIONS]):
                file_path = os.path.join(root, filename)
                file_sha = _file_sha(file_path)
                extension = filename.split(".")[-1]

                # Make sure it isn't already added.
                already_added = False
                for p in photos_info["photos"]:
                    if file_sha in p["url"]:
                        already_added = True
                if not already_added:
                    print "Adding %s by %s" % (filename, credit["name"])
                    sha_filename = "%s.%s" % (file_sha, extension,)
                    photos_info["photos"].append({
                        "url": "%s%s" % (BASE_URL, sha_filename),
                        "credit": credit["name"],
                        "credit_url": credit["credit_url"],
                        "start_date": _datetime_to_ms_since_epoch(next_start_date),
                        "start_date_human": next_start_date.strftime("%b %d %Y"),
                    })
                    dest_path = os.path.abspath(os.path.join(SITE_BUILD_DIR, "photos", sha_filename))
                    shutil.copyfile(file_path, dest_path)
                    next_start_date = next_start_date + TIME_BETWEEN_IMAGES


                else:
                    print "Exists: %s by %s" % (filename, credit["name"])


    # mark last update
    photos_info["last_update"] = _datetime_to_ms_since_epoch(datetime.datetime.now())

    with open(photo_data_file, "w+") as f:
        json.dump(photos_info, f, sort_keys=True, indent=4, separators=(',', ': '))
        # json.dump(photos_info, f)

    with open(PHOTO_DATA_JS_PATH, "w") as f:
        f.write("""(function() {
    var photoInfo = %s;
    window.mindfulBrowsing = window.mindfulBrowsing || {};
    window.mindfulBrowsing.photoInfo = photoInfo;
})();
""" % json.dumps(photos_info))

    print "Photos built."

def build_site():
    print "Copying site...",
    distutils.dir_util.copy_tree(SITE_SOURCE_DIR, SITE_BUILD_DIR)
    print "Done."

def deploy_site():
    local("rsync -avz -e ssh --progress %s/ %s" % (SITE_BUILD_DIR, SCP_TARGET,))

def deploy():
    bundle_images()
    build_site()
    deploy_site()
