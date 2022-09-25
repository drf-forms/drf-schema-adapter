from copy import deepcopy

from collections import namedtuple, defaultdict
try:
    from collections import Mapping
except ImportError:
    from collections.abc import Mapping

PROPERTY = 1
GETTER = 0
MetaDataInfo = namedtuple('MetaDataInfo', ['attr', 'attr_type', 'default'])


class BaseAdapter(object):
    """
    Basic adapter that renders a dict to json with no modifications.
    """

    metadata_info = [
        MetaDataInfo('fields', GETTER, []),
    ]

    def render(self, config):
        fields = config['fields']
        adapted = []
        for field in fields:
            adapted.append(self.adapt_field(field))

        return adapted

    def render_root(self, config):
        return config

    def __call__(self, config):
        return self.render(config)

    @classmethod
    def adapt_field(cls, field):
        return field

    @classmethod
    def adapt_wizard(cls, func):
        return func


def to_html_tag(widget_type):
    if widget_type in ["checkbox", "select"]:
        return widget_type
    return "input"


class AngularFormlyAdapter(BaseAdapter):

    metadata_info = [
        MetaDataInfo('fields', GETTER, []),
        MetaDataInfo('fieldsets', GETTER, []),
    ]

    @classmethod
    def adapt_field(self, field):
        field['validation'].update({
            'label': field['ui']['label'],
            'type': field['type'],
        })

        new_field = {
            'key': field['key'],
            'read_only': field['read_only'],
            'type': to_html_tag(field['type']),
            'templateOptions': field['validation']
        }

        if 'placeholder' in field['ui']:
            new_field['templateOptions']['placeholder'] = field['ui']['placeholder']

        if 'default' in field:
            new_field['defaultValue'] = field['default']

        if 'choices' in field:
            new_field['templateOptions']['options'] = field['choices']

        return new_field

    def _render_fieldset(self, fieldset, fields_map):
        rv = []
        for field in fieldset:
            new_field = {}
            if isinstance(field, dict):
                computed_field = None
                if 'key' in field and field['key'] in fields_map:
                    computed_field = fields_map[field['key']]
            else:
                computed_field = fields_map.get(field, None)
                if computed_field is None:
                    continue

            if computed_field is not None:
                new_field = computed_field

            if isinstance(field, dict):
                field_type = field.get('type', None)
                if field_type == 'fieldset':
                    new_field['fieldGroup'] = self._render_fieldset(field.pop('fields', []), fields_map)
                template_options = new_field.get('templateOptions', {})
                template_options.update(field.get('templateOptions', {}))
                if field_type == 'fieldset' and 'label' in field:
                    template_options['title'] = field.pop('label')
                new_field.update(field)
                new_field['templateOptions'] = template_options
                if field_type == 'fieldset':
                    new_field.pop('type')

            rv.append(new_field)

        return rv

    def render(self, config):
        fields_map = {
            field['key']: field
            for field in super(AngularFormlyAdapter, self).render(config)
        }

        adapted = self._render_fieldset(deepcopy(config['fieldsets']), fields_map)
        return adapted


class EmberAdapter(BaseAdapter):
    """
    Here is an example of the expected output
        [{
            "read_only": False,
            "extra": {
                "related_model": "emberadmin/category",
                "choices": [{"foo": "bar"}]
            },
            "name": "category",
            "label": "Category",
            "widget": "foreignkey"
        }, ...]
    """

    metadata_info = [
        MetaDataInfo('fields', GETTER, []),
        MetaDataInfo('fieldsets', GETTER, []),
        MetaDataInfo('list_display', GETTER, []),
        MetaDataInfo('filter_fields', GETTER, []),
        MetaDataInfo('languages', GETTER, []),
        MetaDataInfo('ordering_fields', GETTER, []),
        MetaDataInfo('needs', GETTER, []),
        MetaDataInfo('list_editable', GETTER, []),
        MetaDataInfo('sortable_by', GETTER, []),
        MetaDataInfo('translated_fields', GETTER, []),
        MetaDataInfo('custom_actions', GETTER, []),
        MetaDataInfo('bulk_actions', GETTER, []),
        MetaDataInfo('list_actions', GETTER, []),
        MetaDataInfo('save_twice', PROPERTY, False),
        MetaDataInfo('search_enabled', PROPERTY, False),
        MetaDataInfo('conditional_formatting', PROPERTY, {}),
    ]

    def render_root(self, config):
        config['applications'] = [
            {
                'name': app['name'].replace('_', '-'),
                'models': app['models']
            } for app in config['applications']
        ]
        return config

    @classmethod
    def adapt_field(cls, field):
        TEXT_FIELDS = ['text', 'textarea', 'markdown']

        new_field = {
            'label': field.get('ui', {}).get('label', ''),
            'readonly': field.get('read_only', False),
            'extra': field.get('extra', {}),
            'name': field['key'],
            'widget': field.get('type', 'text'),
            'required': field.get('validation', {}).get('required', False),
            'translated': field.get('translated', False),
            'validations': {},
        }

        if 'choices' in field:
            new_field['extra']['choices'] = field['choices']

        if 'related_endpoint' in field:
            new_field['extra']['related_model'] = '/'.join(
                filter(bool, [field['related_endpoint'].get('app'), field['related_endpoint'].get('singular')])
            ).replace('_', '-')
        if 'placeholder' in field.get('ui', {}):
            new_field['extra']['placeholder'] = field['ui']['placeholder']

        if 'help' in field.get('ui', {}):
            new_field['extra']['help'] = field['ui']['help']

        if 'default' in field:
            new_field['extra']['default'] = field['default']

        # validators
        if field.get('validation', {}).get('required', False):
            new_field['validations']['presence'] = True
        val_max = field.get('validation', {}).get('max', None)
        val_min = field.get('validation', {}).get('min', None)
        if val_max is not None or val_min is not None:
            validator = {}
            if field['type'] in TEXT_FIELDS:
                if val_max is not None:
                    validator['maximum'] = val_max
                if val_min is not None:
                    validator['minimum'] = val_min
                new_field['validations']['length'] = validator
            elif field['type'] == 'number':
                if val_max is not None:
                    validator['lessThanOrEqualTo'] = val_max
                if val_min is not None:
                    validator['greaterThanOrEqualTo'] = val_min
                new_field['validations']['numericality'] = validator

        return new_field

    def _replace_key_with_name(self, fields):
        for i, field in enumerate(fields):
            new_field = field
            if 'key' in new_field:
                new_field['name'] = new_field.pop('key')
            if 'fields' in new_field:
                new_field['fields'] = self._replace_key_with_name(new_field['fields'])
            fields[i] = new_field
        return fields

    def render(self, config):

        config['fields'] = super(EmberAdapter, self).render(config)
        config['fieldsets'] = [{'title': None, 'fields': self._replace_key_with_name(config['fieldsets'])}]

        for i, need in enumerate(config.get('needs', [])):
            config['needs'][i] = {
                key: value.replace('_', '-')
                for key, value in need.items()
            }

        return config

    @classmethod
    def adapt_wizard(cls, func):
        func.action_kwargs['allowBulk'] = False
        func.action_kwargs['type'] = 'closureMethod'
        func.action_kwargs['method'] = '_wizard'

        return func


class ReactJsonSchemaAdapter(BaseAdapter):

    metadata_info = [
        MetaDataInfo('fields', GETTER, []),
        MetaDataInfo('fieldsets', GETTER, []),
    ]

    _schema_type_mapping = {
        'number': 'number',
        'checkbox': 'boolean',
    }

    _ui_type_mapping = {
        'email': 'email',
        'url': 'uri',
        'file': 'data-url',
        'image': 'data-url',
        'date': 'date',
        'datetime': 'date-time',
    }

    _schema_type_default = 'string'
    _ui_type_default = None

    @classmethod
    def create_type_dict_for(cls, dict_type):
        rv = defaultdict(lambda: getattr(cls, '_{}_type_default'.format(dict_type)))
        rv.update(getattr(cls, '_{}_type_mapping'.format(dict_type)))
        return rv

    @classmethod
    def adapt_field(cls, field):
        schema_type_mapping = cls.create_type_dict_for('schema')
        ui_type_mapping = cls.create_type_dict_for('ui')

        new_field = {
            'required': field['validation'].get('required', False),
            'key': field['key'],
            'schema': {
                'title': field['ui']['label'],
                'type': schema_type_mapping[field['type']]
            },
            'ui': {},
        }

        widget = ui_type_mapping[field['type']]
        if widget is not None:
            new_field['ui']['ui:widget'] = widget

        if 'choices' in field:
            new_field['schema']['enum'] = [x['value'] for x in field['choices']]
            new_field['schema']['enumNames'] = [x['label'] for x in field['choices']]

        if 'placeholder' in field['ui']:
            new_field['ui']['ui:placeholder'] = field['ui']['placeholder']

        if 'help' in field['ui']:
            new_field['schema']['description'] = field['ui']['help']

        if 'default' in field:
            new_field['schema']['default'] = field['default']

        if 'read_only' in field and field['read_only']:
            new_field['ui']['ui:readonly'] = field['read_only']

        return new_field

    def deep_update(self, orig, updater):
        for k, v in updater.items():
            if isinstance(v, Mapping):
                rv = self.deep_update(orig.get(k, {}), v)
                orig[k] = rv
            else:
                orig[k] = updater[k]
        return orig

    def update_field_by_key(self, fields, original):
        rv = None
        key = original.get('key', None)
        if key is None:
            return original

        for field in fields:
            if 'key' in field and field['key'] == key:
                rv = field
                break

        if rv is not None:
            rv = self.deep_update(rv, original)
            return rv

        return original

    def map_fieldset_schema(self, fieldset, fields, title=None):
        schema = {
            'type': 'object',
            'properties': {}
        }

        if title is not None:
            schema['title'] = title

        required = []

        if 'title' in fieldset and fieldset['title'] is not None:
            schema['title'] = fieldset['title']

        for field in fieldset.get('fields', []):
            field = self.update_field_by_key(fields, field)

            if field['required']:
                required.append(field['key'])

            if field['schema']['type'] == 'object':
                schema['properties'][field['key']] = self.map_fieldset_schema(field)
            else:
                schema['properties'][field['key']] = field['schema']

        schema['required'] = required
        return schema

    def map_fieldset_ui(self, fieldset, fields):
        ui = {}
        order = []

        for field in fieldset.get('fields', []):
            field = self.update_field_by_key(fields, field)
            order.append(field['key'])
            ui[field['key']] = field['ui']

            if field['schema']['type'] == 'object':
                ui[field['key']].update(self.map_fieldset_ui(field))

        ui['ui:order'] = order
        return ui

    def render(self, config):

        config['fields'] = super(ReactJsonSchemaAdapter, self).render(config)
        fieldsets = config.pop('fieldsets')

        try:
            schema = self.map_fieldset_schema({'fields': fieldsets}, config['fields'], fieldsets[0].get('title', None))
            ui = self.map_fieldset_ui({'fields': fieldsets}, config['fields'])
        except KeyError:
            # We are dealing with a Serializer, not an Endpoint
            schema = self.map_fieldset_schema(fieldsets[0], config['fields'], fieldsets[0].get('title', None))
            ui = self.map_fieldset_ui(fieldsets[0], config['fields'])

        config['schema'] = schema
        config['ui'] = ui

        return config
