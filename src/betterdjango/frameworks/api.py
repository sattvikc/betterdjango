from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.paginator import Paginator
from django.http import HttpResponse
import json

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class APIProvider:
    API_REGISTRY = {}

    def __init__(self):
        self.URLS = []
        self.APIS = []

    @property
    def urls(self):
        apiurls = []
        for pattern, method in self.URLS:
            apiurls.append(url(pattern, method))

        urlpatterns = patterns('', *apiurls)
        return urlpatterns, 'api', 'api'

    def discover(self):
        for app in settings.INSTALLED_APPS:
            try:
                __import__(app, globals(), locals(), ['api'], 0)
                logging.info('API(s) found for { %s }' % app)
            except Exception as e:
                logger.debug(str(e))

    def register(self, *http_methods):
        def _inner1(method):
            method_name = method.__name__
            method_app = '.'.join(method.__module__.split('.')[:-1])
            method_url = r'^%s/%s/$' % (method_app,
                method_name.replace('_', '-'))
            self.APIS.append((method_app, method_name.replace('_', '-'),
                method_url, http_methods[0]))

            def _inner2(request):
                # Check for allowed methods
                if not request.method in http_methods:
                    return HttpResponse(json.dumps({ 'status': 'METHOD_DENIED' }),
                        content_type='application/json') # TODO: Improve

                # Parse the form parameters
                if request.method == 'GET':
                    data = request.GET
                elif request.method == 'POST':
                    data = request.POST
                kwargs = {}
                for k in data:
                    if k == 'csrftoken':
                        continue
                    elif k == 'csrfmiddlewaretoken':
                        continue
                    kwargs[k] = data[k]
                paginate = hasattr(method, '_paginate')
                if paginate:
                    page_num = 1
                    if '_page_num' in kwargs:
                        page_num = kwargs.pop('_page_num')

                # Execute the API
                try:
                    request.APICONTEXT = {}
                    api_result = method(request, **kwargs)
                    result = {'status': 'OK'}
                    if not api_result is None:
                        if paginate:
                            page_size = method._page_size
                            p = Paginator(api_result, page_size)
                            result['pages'] = {}
                            result['pages']['count'] = p.num_pages
                            result['pages']['current'] = page_num
                            page = p.page(page_num)
                            result['data'] = page.object_list
                        else:
                            result['data'] = api_result

                except Exception as e:
                    result = { 'status': 'ERROR' }
                    result['exception'] = {
                        'class' : e.__class__.__name__,
                        'message': str(e)
                    }

                def default_provider(request):
                    def default(o):
                        if hasattr(o, 'json_dict'):
                            return o.json_dict(request)
                        else:
                            if not isinstance(o, str):
                                try:
                                    i = iter(o)
                                    return list(i)
                                except:
                                    pass
                            return None
                    return default
                
                return HttpResponse(json.dumps(result,
                    default=default_provider(request), sort_keys=True),
                    content_type='application/json')

            self.URLS.append((method_url, _inner2))
            return _inner2
        return _inner1

provider = APIProvider()
