import json
from flask import render_template, request
from negotiate.flask import Formatter

class TemplateFormatter(Formatter):
    def configure(self, template):
        self.template = template

    def render(self, obj):
        return render_template(self.template, **obj)

class HTMLFormatter(TemplateFormatter):
    format = 'html'
    mimetypes = ['text/html']

class JSEmbedFormatter(TemplateFormatter):
    format = 'embed.js'
    mimetypes = ['application/javascript', 'application/vnd.annotateit.annotation.embed+javascript']

class HTMLEmbedFormatter(TemplateFormatter):
    format = 'embed.html'
    mimetypes = ['text/html', 'application/vnd.annotateit.annotation.embed+html']

class JSONFormatter(Formatter):
    format = 'json'
    mimetypes = ['application/json']

    def configure(self, key=None):
        if key is None:
            self.key = lambda x: x
        elif isinstance(key, basestring):
            self.key = lambda x: x[key]
        else:
            self.key = key

    def render(self, obj):
        return json.dumps(self.key(obj), indent=None if request.is_xhr else 2)
