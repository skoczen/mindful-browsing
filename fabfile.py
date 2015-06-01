from fabric.api import *
import boto
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from boto.cloudfront import CloudFrontConnection
import datetime
import distutils.core
import email
import errno
import random
import hashlib
import json
import mimetypes
import os
import shutil
import time


IMAGES_SOURCE_DIR = os.path.abspath(os.path.join(os.getcwd(), "source/photos"))
SITE_BUILD_DIR = os.path.abspath(os.path.join(os.getcwd(), "build"))
SITE_SOURCE_DIR = os.path.abspath(os.path.join(os.getcwd(), "site"))
PHOTO_EXTENSIONS = ["jpg", "jpeg", "png", "gif", ]
PHOTO_DATA_FILENAME = "photos.json"
TIME_BETWEEN_IMAGES = datetime.timedelta(days=2)
BASE_URL = "http://www.mindfulbrowsing.org/photos/"
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
        import traceback; traceback.print_exc();
        # photos_info = {
        #     "photos": []
        # }
        next_start_date = datetime.datetime.now()

    all_photos = []

    for root, folders, files in os.walk(IMAGES_SOURCE_DIR):
        for filename in files:
            photo_dir = False
            credit = {}
            if os.path.exists(os.path.join(root, "credit.json")):
                photo_dir = True
                credit = json.load(open(os.path.join(root, "credit.json")))
                credit["filename"] = filename
                credit["root"] = root
                all_photos.append(credit)

    random.shuffle(all_photos)
    for credit in all_photos:
        if photo_dir and any([ext in credit["filename"] for ext in PHOTO_EXTENSIONS]):
            file_path = os.path.join(credit["root"], credit["filename"])
            file_sha = _file_sha(file_path)
            extension = credit["filename"].split(".")[-1]

            # Make sure it isn't already added.
            already_added = False
            for p in photos_info["photos"]:
                if file_sha in p["url"]:
                    already_added = True
            if not already_added or force_add:
                print "Adding %s by %s" % (credit["filename"], credit["name"])
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
                print "Exists: %s by %s" % (credit["filename"], credit["name"])

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


def deploy_static():
    """
    Sync Static to S3
    ================

    Scans all files in build folder and
    uploads them to S3 with the same directory structure.

    This command can optionally do the following but it is off by default:
    * gzip compress any CSS and Javascript files it finds and adds the appropriate
      'Content-Encoding' header.
    * set a far future 'Expires' header for optimal caching.

    Note: This script requires the Python boto library and valid Amazon Web
    Services API keys.

    Required variables:
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_STORAGE_BUCKET_NAME = ''

    Command options are:
      -p PREFIX, --prefix=PREFIX
                            The prefix to prepend to the path on S3.
      --gzip                Enables gzipping CSS and Javascript files.
      --expires             Enables setting a far future expires header.
      --force               Skip the file mtime check to force upload of all
                            files.

    TODO:
    * Make FILTER_LIST an optional argument

    """
    c = SyncCommand()
    c.handle()

class SyncCommand(object):

    # Extra variables to avoid passing these around
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_STORAGE_BUCKET_NAME = 'mindfulbrowsing.org'
    DIRECTORY = ''
    FILTER_LIST = ['.DS_Store',]
    GZIP_CONTENT_TYPES = (
        'text/css',
        'application/javascript',
        'application/x-javascript'
    )

    upload_count = 0
    skip_count = 0

    args = 'bucket_name'

    can_import_settings = True

    def handle(self, *args, **options):
        self.DIRECTORY = "build"

        self.verbosity = 1
        self.prefix = ''
        self.do_gzip = True
        self.do_expires = True
        self.do_force = False

        # Now call the syncing method to walk the STATIC_ROOT directory and
        # upload all files found.
        self.sync_s3()

        print
        print "%d files uploaded." % (self.upload_count)
        print "%d files skipped." % (self.skip_count)

    def sync_s3(self):
        """
        Walks the media directory and syncs files to S3
        """
        bucket, key = self.open_s3()
        os.path.walk(self.DIRECTORY, self.upload_s3,
            (bucket, key, self.AWS_STORAGE_BUCKET_NAME, self.DIRECTORY))

    def compress_string(self, s):
        """Gzip a given string."""
        import cStringIO, gzip
        zbuf = cStringIO.StringIO()
        zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
        zfile.write(s)
        zfile.close()
        return zbuf.getvalue()

    def open_s3(self):
        """
        Opens connection to S3 returning bucket and key
        """
        conn = boto.connect_s3(
            self.AWS_ACCESS_KEY_ID,
            self.AWS_SECRET_ACCESS_KEY,
            is_secure=True,
            calling_format=OrdinaryCallingFormat() 
        )
        try:
            bucket = conn.get_bucket(self.AWS_STORAGE_BUCKET_NAME)
        except boto.exception.S3ResponseError:
            bucket = conn.create_bucket(self.AWS_STORAGE_BUCKET_NAME)
        return bucket, boto.s3.key.Key(bucket)

    def upload_s3(self, arg, dirname, names):
        """
        This is the callback to os.path.walk and where much of the work happens
        """
        bucket, key, bucket_name, root_dir = arg # expand arg tuple

        if root_dir == dirname:
            return # We're in the root media folder

        # Later we assume the STATIC_ROOT ends with a trailing slash
        # TODO: Check if we should check os.path.sep for Windows
        if not root_dir.endswith('/'):
            root_dir = root_dir + '/'

        for file in names:
            headers = {}

            if file in self.FILTER_LIST:
                continue # Skip files we don't want to sync

            filename = os.path.join(dirname, file)
            if os.path.isdir(filename):
                continue # Don't try to upload directories

            file_key = filename[len(root_dir):]
            if self.prefix:
                file_key = '%s/%s' % (self.prefix, file_key)

            # Check if file on S3 is older than local file, if so, upload
            if not self.do_force:
                s3_key = bucket.get_key(file_key)
                if s3_key:
                    s3_datetime = datetime.datetime(*time.strptime(
                        s3_key.last_modified, '%a, %d %b %Y %H:%M:%S %Z')[0:6])
                    local_datetime = datetime.datetime.utcfromtimestamp(
                        os.stat(filename).st_mtime)
                    if local_datetime < s3_datetime:
                        self.skip_count += 1
                        if self.verbosity > 1:
                            print "File %s hasn't been modified since last " \
                                "being uploaded" % (file_key)
                        continue

            # File is newer, let's process and upload
            if self.verbosity > 0:
                print "Uploading %s..." % (file_key)

            content_type = mimetypes.guess_type(filename)[0]
            if content_type:
                headers['Content-Type'] = content_type
            file_obj = open(filename, 'rb')
            file_size = os.fstat(file_obj.fileno()).st_size
            filedata = file_obj.read()
            if self.do_gzip:
                # Gzipping only if file is large enough (>1K is recommended) 
                # and only if file is a common text type (not a binary file)
                if file_size > 1024 and content_type in self.GZIP_CONTENT_TYPES:
                    filedata = self.compress_string(filedata)
                    headers['Content-Encoding'] = 'gzip'
                    if self.verbosity > 1:
                        print "\tgzipped: %dk to %dk" % \
                            (file_size/1024, len(filedata)/1024)
            if self.do_expires:
                # HTTP/1.0
                headers['Expires'] = '%s GMT' % (email.Utils.formatdate(
                    time.mktime((datetime.datetime.now() +
                    datetime.timedelta(days=365*2)).timetuple())))
                # HTTP/1.1
                headers['Cache-Control'] = 'max-age %d' % (3600 * 24 * 365 * 2)
                if self.verbosity > 1:
                    print "\texpires: %s" % (headers['Expires'])
                    print "\tcache-control: %s" % (headers['Cache-Control'])

            try:
                key.name = file_key
                key.set_contents_from_string(filedata, headers, replace=True)
                key.make_public()
            except boto.s3.connection.S3CreateError, e:
                print "Failed: %s" % e
            except Exception, e:
                print e
                raise
            else:
                self.upload_count += 1

            file_obj.close()

