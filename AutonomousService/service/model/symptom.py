from mongoengine import DynamicDocument, StringField, DateTimeField, DictField

from service.conf_reader import ConfReader
from service.model.db.abs_model import DefaultQuerySet


class SymptomActionCase(DynamicDocument):
    meta = {
        'collection': 'SymptomActionCase',
        'queryset_class': DefaultQuerySet,
        'db_alias': ConfReader().get('TAL_DATABASE', 'alias')
    }

    hash = StringField()

    tactic_id = StringField(db_field='tacticID')
    tactic = DictField(db_field='m_tactic')

    symptom_id = StringField(db_field='symptomID')
    symptom = DictField()

    actions = DictField()

    created = DateTimeField()
    updated = DateTimeField()
