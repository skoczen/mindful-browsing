from fabric.api import *
import arrow
import datetime
from datetime import date, timedelta
import distutils.core
import errno
import gzip
import hashlib
import json
import os
import shutil
import tinys3

IMAGES_SOURCE_DIR = os.path.abspath(os.path.join(os.getcwd(), "source/photos"))
SITE_BUILD_DIR = os.path.abspath(os.path.join(os.getcwd(), "build"))
SITE_SOURCE_DIR = os.path.abspath(os.path.join(os.getcwd(), "site"))
PHOTO_EXTENSIONS = ["jpg", "jpeg", "png", "gif", ]
PHOTO_DATA_FILENAME = "photos.json"
TIME_BETWEEN_IMAGES = datetime.timedelta(days=2)
BASE_URL = "https://www.mindfulbrowsing.org/photos/"
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
    return datetime.datetime.fromtimestamp(ms / 1000)


def bundle_images(force_add=False):
    if force_add == "True":
        force_add = True
    _ensure_build_directory()

    try:
        photo_data_file = os.path.join(os.getcwd(), SITE_BUILD_DIR, PHOTO_DATA_FILENAME,)
        photos_info = json.load(open(photo_data_file, "r"))
        next_start_date = _ms_since_epoch_to_datetime(photos_info["photos"][-1]["start_date"]) + TIME_BETWEEN_IMAGES
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
                if not already_added or force_add:
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


def bundle_app():
    local("zip -r mindfulbrowsing.zip extension -x '*.DS_Store'")


def deploy_site():
    local("rsync -avz -e ssh --progress %s/ %s" % (SITE_BUILD_DIR, SCP_TARGET,))


def deploy():
    bundle_images()
    bundle_app()
    build_site()
    # deploy_site()
    deploy_static()


# Via https://gist.github.com/drcongo/5714673
CDN = {
    # 'aws_cloudfront_id': 'YOUR_CLOUDFRONT_ID',
    'aws_access_key': os.environ["AWS_ACCESS_KEY_ID"],
    'aws_secret_key': os.environ["AWS_SECRET_ACCESS_KEY"],
    'aws_bucket': 'mindfulbrowsing.org',
    'aws_endpoint': 's3-us-west-1.amazonaws.com',
    'aws_sitename': 'mindfulbrowsing.org',  # use the domain name
    'static_folders': [
        'build/img',
        'build/js',
        'build/css',
    ],
    'files': [
        'build/index.html',
        'build/photos.json',
    ]
}


def deploy_static():
    """Deploys the static assets to S3"""
    if not os.path.exists('fabfile/logs'):
        os.makedirs('fabfile/logs')

    last_run = get_last_run()
    with open('fabfile/logs/static_files.log', 'a+') as files_log:
        files_log.seek(0)
        logged_files = [_.rstrip("\n") for _ in files_log.readlines()]
        print("%s static files logged." % len(logged_files))
        for folder in CDN['static_folders']:
            to_upload = len(CDN['files'])
            folder_to_s3(folder, logged_files, files_log, last_run)
            if len(CDN['files']) == to_upload:
                print('No new or modified files in %s' % folder)
        files_log.close()

    if os.path.exists('TEMP'):
        shutil.rmtree('TEMP')
    # set_last_run()
    # invalidate_cloudfront()


def get_last_run():
    pointer = os.path.join('fabfile', 'logs', 'static_times.log')
    with open(pointer, 'a+') as f:
        f.seek(0)
        times = [_.rstrip("\n") for _ in f.readlines()]
        if times:
            last = times[-1]
        try:
            l = arrow.get(last).floor('second')
        except Exception as e:
            print(e)
            l = arrow.get('1969-01-01').floor('second')

        f.close()

    print("Static last run: %s " % l)

    return l


def folder_to_s3(folder, logged_files, log, last_run):
        compressable = ['.css', '.js', '.svg']
        ignore_files = ['.DS_Store', '.gitkeep']
        ignore_dirs = ['projects']
        s3 = init_bucket()
        the_future = date.today() + timedelta(days=365 * 10)
        for path, dir, files in os.walk(folder):
            curr_dir = os.path.split(path)[1]
            for f in files:
                do_upload = False
                m = arrow.get(os.path.getmtime(os.path.join(path, f)))
                c = arrow.get(os.path.getmtime(os.path.join(path, f)))
                if os.path.join(path, f) not in logged_files:
                    if f not in ignore_files and curr_dir not in ignore_dirs:
                        print('NEW: %s' % os.path.join(path, f))
                        log.write('%s\n' % os.path.join(path, f))
                        do_upload = True

                elif m.timestamp > last_run.timestamp or c.timestamp > last_run.timestamp:
                    print('MODIFIED: %s' % os.path.join(path, f))
                    do_upload = True

                if do_upload is True:
                    if f not in ignore_files and curr_dir not in ignore_dirs:
                        headers = {'Expires': the_future}
                        foldername = os.path.split(folder)[1]
                        putpath = "%s/%s" % (foldername, os.path.relpath(os.path.join(path, f), folder))
                        print(" - Putting %s " % putpath)
                        # k = bucket.new_key(putpath)
                        # print(os.path.splitext(f)[1])
                        if os.path.splitext(f)[1] in compressable:
                            print(" Compressing %s " % f)
                            # headers['Content-Encoding'] = 'gzip'
                            # k.set_contents_from_filename(gzipit(path, f), headers=headers)
                            k = s3.upload(putpath, open(gzipit(path, f)), CDN['aws_bucket'], expires="max", public=True)
                        else:
                            # k.set_contents_from_filename(os.path.join(path, f), headers=headers)
                            k = s3.upload(putpath, open(os.path.join(path, f)), CDN['aws_bucket'], expires="max", public=True)
                        # k.make_public()
                        CDN['files'].append(putpath)


def init_bucket():
    s3 = tinys3.Connection(CDN['aws_access_key'], CDN['aws_secret_key'], tls=True)
    # s3 = boto.connect_s3(
    #     CDN['aws_access_key'], 
    #     CDN['aws_secret_key'], 
    #     is_secure=True,               # require ssl
    #     calling_format=OrdinaryCallingFormat(),
    # )
    # s3.host = CDN['aws_endpoint']
    # bucket = s3.get_bucket(CDN['aws_bucket'])
    return s3


def invalidate_cloudfront():
    conn = CloudFrontConnection(CDN['aws_access_key'], CDN['aws_secret_key'])
    print conn.create_invalidation_request(CDN['aws_cloudfront_id'], CDN['files'])
    print 'Invalidated cloudfront cache for ...\n%s' % '\n\t '.join(CDN['files'])
    CDN['files'] = []


def gzipit(path, file):
    fullpath = os.path.join(path, file)
    f_in = open(fullpath, 'rb').read()
    if not os.path.exists('TEMP'):
        os.makedirs('TEMP')
    f_out = gzip.open('TEMP/%s' % file, 'wb')
    f_out.write(f_in)
    f_out.close()
    return 'TEMP/%s' % file

