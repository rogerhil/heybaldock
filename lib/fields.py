import pickle

from django.utils import simplejson as json
from django.db.models import TextField
from lib.serializer import JSONEncoder


class PickleField(TextField):
    """For saving in (restoring from) the database objects encoded with CPickle.
    Pickled strings are converted to unicode with 'latin1' encoding to properly handle
    mix of latin1 and unicode code in database models stored as utf-8. Example of such mix:
    >>> s = u'The mydeco Forum has landed - and you can win \xa325!'
    >>> PickleField._loads(PickleField._dumps(s)) == s
    True
    """

    @staticmethod
    def _loads(data):
        return pickle.loads(data.encode('latin1')) if data else None

    @staticmethod
    def _dumps(obj):
        return pickle.dumps(obj).decode('latin1')

    def contribute_to_class(self, cls, name):
        super(PickleField, self).contribute_to_class(cls, name)

        def get_object(model_instance):
            data = getattr(model_instance, self.attname, '')
            return PickleField._loads(data)
        setattr(cls, 'get_%s_object' % self.name, get_object)

        def set_object(model_instance, obj):
            # we need to store unicode in django models, that later will be stored
            # in the database with utf-8 encoding
            return setattr(model_instance, self.attname, PickleField._dumps(obj))
        setattr(cls, 'set_%s_object' % self.name, set_object)


class JSONField(TextField):
    """Field to save/load objects as JSON.
    Note: PickleField saves and restores same data, but JSONField not so smart, for example
    it can't restore datetime, Decimal and other complex types.
    For migration purposes this field also able to restore data encoded with PickleField, but
    saves data always as json.
    >>> from datetime import datetime
    >>> data = {'name': u'Win \xa325!', 'when': datetime(2010, 11, 17, 10, 1, 1), 'what': 10.1}
    >>> raw = JSONField._dumps(data)
    >>> raw
    '{"what": 10.1, "when": "2010-11-17 10:01:01", "name": "Win \\\\u00a325!"}'
    >>> restored_data = JSONField._loads(raw)
    >>> restored_data
    {'what': 10.1, 'when': '2010-11-17 10:01:01', 'name': u'Win \\xa325!'}
    >>> JSONField._loads(PickleField._dumps(data)) # check backward compatibility
    {'what': 10.1, 'when': datetime.datetime(2010, 11, 17, 10, 1, 1), 'name': u'Win \\xa325!'}
    """

    @staticmethod
    def _loads(data):
        if data:
            if data[0] == '(': # old pickle data
                return PickleField._loads(data)
            else:                       # json data
                return json.loads(data)

    @staticmethod
    def _dumps(obj):
        return json.dumps(obj, cls=JSONEncoder)

    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)
        cache_field = '_%s_object' % self.name

        def get_object(model_instance):
            if not hasattr(model_instance, cache_field):
                setattr(model_instance, cache_field,
                        JSONField._loads(getattr(model_instance, self.attname, '')))
            return getattr(model_instance, cache_field)
        setattr(cls, 'get_%s_object' % self.name, get_object)

        def set_object(model_instance, obj):
            return setattr(model_instance, self.attname, JSONField._dumps(obj))
        setattr(cls, 'set_%s_object' % self.name, set_object)