"""HTML DAP response

This is a simple HTML response that allows that to be analysed on the browser.
The user can select a subset of the data and download in different formats.

"""

from jinja2 import Environment, PackageLoader, ChoiceLoader
from webob import Response
from webob.dec import wsgify
from webob.exc import HTTPSeeOther
from six.moves.urllib.parse import unquote

from ..lib import BaseResponse
from ...lib import __version__


class HTMLResponse(BaseResponse):

    """A simple HTML response for browsing and downloading data."""

    __version__ = __version__

    def __init__(self, dataset, req=None):
        BaseResponse.__init__(self, dataset)
        self.headers.extend([
            ("Content-description", "dods_form"),
            ("Content-type", "text/html; charset=utf-8"),
        ])

        # our default environment; we need to include the base template from
        # pydap as well since our template extends it
        self.loaders = [
            PackageLoader("pydap.responses.html", "templates"),
            PackageLoader("pydap.wsgi", "templates"),
        ]

    @wsgify
    def __call__(self, req):
        # if request is a post we should redict to ASCII response or citation
        if req.method == "POST":                     
            if req.params['action'] == 'data':
                # If download button is pressed, we redirect to ASCII response
                return self.redirect_ascii(req)
            elif req.params['action'] == 'citation' :
                # If citation button is pressed, we redirect to citation
                return self.redirect_citation(req)                

        # check if the server has specified a render environment; if it has,
        # make a copy and add our loaders to it
        if "pydap.jinja2.environment" in req.environ:
            env = req.environ["pydap.jinja2.environment"].overlay()
            env.loader = ChoiceLoader([
                loader for loader in [env.loader] + self.loaders if loader])
        else:
            env = Environment(loader=ChoiceLoader(self.loaders))

        env.filters["unquote"] = unquote
        template = env.get_template("html.html")

        tokens = req.path_info.split("/")[1:]
        breadcrumbs = [{
            "url": "/".join([req.application_url] + tokens[:i+1]),
            "title": token,
        } for i, token in enumerate(tokens) if token]

        context = {
            "root": req.application_url,
            "location": req.path_url,
            "breadcrumbs": breadcrumbs,
            "dataset": self.dataset,
            "version": __version__,
        }

        return Response(
            body=template.render(context),
            headers=self.headers)   
        
    def get_selection(self, req):        
        selection = []
        for k in req.params:            
            if k.startswith("var1_") and req.params[k] != "--":
                name = k[5:]
                tokens = (
                    req.params[k],
                    req.params["op_%s" % name],
                    req.params["var2_%s" % name])
                selection.append("".join(tokens))
        return selection

    def get_projection(self, req):
        projection = []
        for k in req.params:
            if req.params[k] == "on":
                tokens = [k]
                i = 0
                while "%s[%d]" % (k, i) in req.params:
                    tokens.append("[%s]" % req.params["%s[%d]" % (k, i)])
                    i += 1
                projection.append("".join(tokens))
        return projection 

    def redirect_ascii(self, req):
        """Return a redirect to the ASCII response."""        
        projection = self.get_projection(req)        
        selection = self.get_selection(req)
        location = "{0}.ascii?{1}&{2}".format(
            req.path_url[:-5],
            ",".join(projection),
            "&".join(selection)).rstrip("?&")
        return HTTPSeeOther(location=location)    
    
    def redirect_citation(self, req):
        """Return a redirect to the citation response."""        
        projection = self.get_projection(req)        
        selection = self.get_selection(req)
        location = "{0}.citation?{1}&{2}".format(
            req.path_url[:-5],
            ",".join(projection),
            "&".join(selection)).rstrip("?&")
        return HTTPSeeOther(location=location)    
        
    
