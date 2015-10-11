from betterdjango.frameworks.views import provider as vp
from betterdjango.frameworks.api import provider

from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

import jsbeautifier


opts = jsbeautifier.default_options()
opts.indent_size = 2
opts.preserve_newlines = False


def gen_api_hierarchy(apis):
    result = {}
    for version, version_list in apis.items():
        vkey = 'v' + version.replace('.', '_')
        result[vkey] = { 'is_namespace__': True }
        for namespace, namespace_list in version_list.items():
            n = namespace.split('.')
            d = result[vkey]
            for item in n:
                if not item in d:
                    d[item] = { 'is_namespace__': True }
                d = d[item]
            for apiname, apifunc in namespace_list.items():
                d[apiname] = { 'func': apifunc, 'version': version, 'namespace': namespace, 'apiname': apiname, 'http_method': apifunc._http_methods[0]}
    return result


@vp.register(r'^api/jqueryapi.js$', template_name='api/jqueryapi.js', )
def jquery_js(request):
    result = {}
    result['api'] = gen_api_hierarchy(provider.REGISTERED_APIS)
    c = RequestContext(request, result)
    return HttpResponse(jsbeautifier.beautify(render_to_string('api/jqueryapi.js', result, context_instance=c), opts), content_type='application/javascript')


@vp.register(r'^api/angularapi.js$', template_name='api/angularapi.js', )
def angular_js(request):
    result = {}
    result['api'] = gen_api_hierarchy(provider.REGISTERED_APIS)
    c = RequestContext(request, result)

    return HttpResponse(jsbeautifier.beautify(render_to_string('api/angularapi.js', result, context_instance=c), opts), content_type='application/javascript')
