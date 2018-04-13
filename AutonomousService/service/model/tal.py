from mongoengine import DynamicDocument

from service.conf_reader import ConfReader
from service.model.db.abs_model import DefaultQuerySet


class Tal(DynamicDocument):
    meta = {
        'collection': 'Tal',
        'queryset_class': DefaultQuerySet,
        'db_alias': ConfReader().get('TAL_DATABASE', 'alias')
    }
