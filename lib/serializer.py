from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.core.serializers.json import DjangoJSONEncoder


class JSONEncoder(DjangoJSONEncoder):
    """JSON encoder that knows how to encode data/time, decimal,
        and lazy string types.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        else:
            return super(JSONEncoder, self).default(obj)

