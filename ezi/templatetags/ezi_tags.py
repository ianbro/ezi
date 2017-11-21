from django import template
from django.conf import settings

def ezi_js_remote(parser, token):
    return EziJSRemote()

class EziJSRemote(template.Node):
    def render(self, context):
        return "<script type=\"text/javascript\" src=\"" + settings.STATIC_URL + "/js/ezi/ezi_crud_plugin.js\"></script>"

register = template.Library()
register.tag('ezi_js', ezi_js_remote)
