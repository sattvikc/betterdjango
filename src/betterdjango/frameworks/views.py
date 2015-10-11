from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render

import json

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class ViewProvider:
    VIEW_REGISTRY = {}

    def __init__(self):
        self.URLS = []
        self.VIEWS = []

    @property
    def urls(self):
        viewurls = []
        for pattern, method in self.URLS:
            viewurls.append(url(pattern, method))

        urlpatterns = patterns('', *viewurls)
        return urlpatterns, 'view_framework', 'view_framework'

    def discover(self):
        for app in settings.INSTALLED_APPS:
            try:
                __import__(app, globals(), locals(), ['views'], 0)
                logging.info('View(s) found for { %s }' % app)
            except Exception as e:
                logger.debug(str(e))

    def register(self, urlpattern, template_name=None, content_type=None):
        def _inner1(method):
            self.VIEWS.append((urlpattern, template_name))

            def _inner2(request, *args, **kwargs):
                result = method(request, *args, **kwargs)
                if isinstance(result, dict):
                    result = render(request, template_name, result)
                if not content_type is None:
                    result['Content-Type'] = content_type
                return result

            self.URLS.append((urlpattern, _inner2))
            return _inner2
        return _inner1

provider = ViewProvider()
