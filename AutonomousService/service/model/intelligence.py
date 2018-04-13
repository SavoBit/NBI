from mongoengine import DynamicDocument, StringField, ObjectIdField

from service.conf_reader import ConfReader
from service.model.db.abs_model import DefaultQuerySet


class IntelligenceModel(DynamicDocument):
    meta = {
        'collection': 'models',
        'queryset_class': DefaultQuerySet,
        'db_alias': ConfReader().get('INTELLIGENCE_DATABASE', 'alias')
    }

    _id = ObjectIdField(db_field='_id')
    uuid = StringField(db_field='id')
