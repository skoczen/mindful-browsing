import optparse
from django.core.management.base import BaseCommand, CommandError
from os import makedirs
from os.path import abspath, dirname, join
from sys import argv
import urllib2

CACHE_DIR="CACHE"
MANIFEST_FILENAME = "manifest.json"

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        optparse.make_option('--force',
            action='store_true', dest='force', default=False,
            help="Force download."),
    )

    help = 'Syncs the complete STATIC_ROOT structure and files to S3 into the given bucket name.'
    args = 'bucket_name'

    can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings

        # Check for AWS keys in settings
        if not hasattr(settings, 'AWS_ACCESS_KEY_ID') or \
           not hasattr(settings, 'AWS_SECRET_ACCESS_KEY'):
           raise CommandError('Missing AWS keys from settings file.  Please' +
                     'supply both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.')
        else:
            self.AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
            self.AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY

        if not hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
            raise CommandError('Missing bucket name from settings file. Please' +
                ' add the AWS_STORAGE_BUCKET_NAME to your settings file.')
        else:
            if not settings.AWS_STORAGE_BUCKET_NAME:
                raise CommandError('AWS_STORAGE_BUCKET_NAME cannot be empty.')
        self.AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

        project_root =  abspath(dirname(argv[0]))
        makedirs(join(project_root, settings.STATIC_ROOT, CACHE_DIR))
        do_download = options.get('force')

        try:
           open(join(project_root, settings.STATIC_ROOT, CACHE_DIR, MANIFEST_FILENAME))
           print "Manifest already exists locally."
        except IOError:
            do_download = True

        if do_download:
            print "Downloading manifest..."
            u = urllib2.urlopen("%s%s/%s" % (settings.STATIC_URL, CACHE_DIR, MANIFEST_FILENAME))
            localFile = open(join(project_root, settings.STATIC_ROOT, CACHE_DIR, MANIFEST_FILENAME), 'w+')
            localFile.write(u.read())
            print "Done."
            localFile.close()
