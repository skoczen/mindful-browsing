import time
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from django.conf import settings

from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from splinter.browser import Browser


@attr('e2e')
class E2ETestCase(LiveServerTestCase):
    def setUp(self, *args, **kwargs):
        super(E2ETestCase, self).setUp(*args, **kwargs)
        self.browser = Browser(settings.BROWSER)
        self.browser.cookies.delete()

    def tearDown(self, *args, **kwargs):
        self.browser.quit()
        super(E2ETestCase, self).tearDown(*args, **kwargs)

    def visit(self, url):
        try:
            url = reverse(url)
        except:
            pass
        self.browser.visit("%s%s" % (self.live_server_url, url))

    def ele(self, css_selector):
        return self.browser.find_by_css(css_selector).first

    def sleep(self, seconds):
        time.sleep(seconds)


def skip(func):
    def _(*args, **kwargs):
        raise SkipTest("Test %s is skipped" % func.__name__)
    _.__name__ = func.__name__
    return _


wip = attr("wip")
