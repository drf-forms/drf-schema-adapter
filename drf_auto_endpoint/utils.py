def get_validation_attrs(instance_field):
    rv = {}

    attrs_to_validation = {
        'min_length': 'min',
        'max_length': 'max',
        'min_value': 'min',
        'max_value': 'max'
    }
    for attr_name, validation_name in attrs_to_validation.items():
        if getattr(instance_field, attr_name, None):
            rv[validation_name] = getattr(instance_field, attr_name)

    return rv

