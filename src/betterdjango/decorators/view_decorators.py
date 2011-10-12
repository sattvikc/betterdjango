from django.core.urlresolvers import get_callable
from django.template import RequestContext, Template
from django.http import HttpResponse
from django.shortcuts import *

from django.template.loader import render_to_string

def template(template_name="base.html"):
    def _view(callable):
        def _deco(request, *args, **kwargs):
           template_vars = callable(request, *args, **kwargs)
           c = RequestContext(request, template_vars)
           return render_to_string(template_name, template_vars, context_instance=c)
        return _deco
    return _view

def wrap_block(block="content", wrap=None, wrap_attrs=''):
    def _view(callable):
        def _deco(request, *args, **kwargs):
           content = callable(request, *args, **kwargs)
           if wrap is None:
               return """{%% block %s %%}%s{%% endblock %%}""" % (block, content)
           else:
               return """{%% block %s %%}<%s %s>%s</%s>{%% endblock %%}""" % (block, wrap, wrap_attrs, content, wrap)
        return _deco
    return _view

def prepend_block(block="content", block_content=''):
    def _view(callable):
        def _deco(request, *args, **kwargs):
           content = callable(request, *args, **kwargs)
           return """{%% block %s %%}%s{%% endblock %%}%s""" % (block, block_content, content)
        return _deco
    return _view

def append_block(block="content", block_content=''):
    def _view(callable):
        def _deco(request, *args, **kwargs):
           content = callable(request, *args, **kwargs)
           return """%s{%% block %s %%}%s{%% endblock %%}""" % (content, block, block_content)
        return _deco
    return _view

def expand_template(template="base.html"):
    def _view(callable):
        def _deco(request, *args, **kwargs):
           content = callable(request, *args, **kwargs)
           t = Template("""{%% extends "%s" %%}%s""" % (template, content))
           c = RequestContext(request, {})
           return t.render(c)
        return _deco
    return _view

def wrap_template(template="base.html", block="content", wrap=None, wrap_attrs=''):
    def _view(callable):
        def _deco(request, *args, **kwargs):
           content = callable(request, *args, **kwargs)
           if wrap is None:
               t = Template("""{%% extends "%s" %%}{%% block %s %%}%s{%% endblock %%}""" % (template, block, content))
           else:
               t = Template("""{%% extends "%s" %%}{%% block %s %%}<%s %s>%s</%s>{%% endblock %%}""" % (template, block, wrap, wrap_attrs, content, wrap))
           c = RequestContext(request, {})
           return t.render(c)
        return _deco
    return _view

def render(*rargs, **rkwargs):
    def _view(callable):
        def _deco(request, *args, **kwargs):
           content = callable(request, *args, **kwargs)
           return HttpResponse(content, *rargs, **rkwargs)
        return _deco
    return _view


