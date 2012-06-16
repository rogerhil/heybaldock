from functools import wraps

from django.http import HttpResponse
from django.utils import simplejson

def ajax(view_func, *args, **kwargs):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        c = view_func(request, *args, **kwargs)
        return HttpResponse(simplejson.dumps(c))
    return _wrapped_view

def required_args(*req_args):
    def _decorator(view_func, *args, **kwargs):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            reqs = []
            for arg in req_args:
                if arg not in request.POST and arg not in request.GET:
                    reqs.append(arg)
            if reqs:
                reqs = ', '.join(reqs)
                msg = "The following arguments are required: %s" % reqs
                raise Exception(msg)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return _decorator