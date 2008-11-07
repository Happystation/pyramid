import os

from webob import Response

from zope.component import queryUtility

from zope.interface import classProvides
from zope.interface import implements
from zope.deprecation import deprecated

from repoze.bfg.interfaces import ITemplateRenderer
from repoze.bfg.interfaces import ITemplateRendererFactory
from repoze.bfg.interfaces import ISettings

from repoze.bfg.templating import renderer_from_cache

from chameleon.zpt.template import PageTemplateFile

class ZPTTemplateRenderer(object):
    classProvides(ITemplateRendererFactory)
    implements(ITemplateRenderer)

    def __init__(self, path, auto_reload=False):
        try:
            self.template = PageTemplateFile(path, auto_reload=auto_reload)
        except ImportError, why:
            why = str(why)
            if 'z3c.pt' in why:
                # unpickling error due to move from z3c.pt -> chameleon
                cachefile = '%s.cache' % path
                if os.path.isfile(cachefile):
                    os.remove(cachefile)
                self.template = PageTemplateFile(path, auto_reload=auto_reload)
            else:
                raise

    def implementation(self):
        return self.template
    
    def __call__(self, **kw):
        return self.template(**kw)

ZPTTemplateFactory = ZPTTemplateRenderer
deprecated('ZPTTemplateFactory',
           ('repoze.bfg.chameleon_zpt.ZPTTemplateFactory should now be '
            'imported as repoze.bfg.chameleon_zpt.ZPTTemplateRenderer'))

def _auto_reload():
    settings = queryUtility(ISettings)
    auto_reload = settings and settings.reload_templates
    return auto_reload

def get_renderer(path):
    """ Return a callable ``ITemplateRenderer`` object representing a
    ``chameleon.zpt`` template at the package-relative path (may also
    be absolute). """
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, ZPTTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer

def get_template(path):
    """ Return a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute).  """
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, ZPTTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer.implementation()

def render_template(path, **kw):
    """ Render a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a string."""
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, ZPTTemplateRenderer,
                                   auto_reload=auto_reload)
    return renderer(**kw)

def render_template_to_response(path, **kw):
    """ Render a ``chameleon.zpt`` template at the package-relative
    path (may also be absolute) using the kwargs in ``*kw`` as
    top-level names and return a Response object with the body as the
    template result. """
    auto_reload = _auto_reload()
    renderer = renderer_from_cache(path, ZPTTemplateRenderer,
                                  auto_reload=auto_reload)
    result = renderer(**kw)
    return Response(result)

