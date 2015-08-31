from __future__ import unicode_literals


def set_dict_attrs(d, values):
    """
    Build dictionary using keys separated by dots
    :param d: dict() - origin dict
    :param values: dict() - data (with dot separated keys) which has to be added to the origin dict
    :return: dict() - final dict including the needed additional info
    """
    key = values.keys()[0]
    key_parts = key.split('.')
    if len(key_parts) > 1:
        if key_parts[:1][0] in d.keys():
            d[key_parts[:1][0]] = set_dict_attrs(d[key_parts[:1][0]],
                                                 {'.'.join(key_parts[1:]): values.values()[0]})
        else:
            d[key_parts[:1][0]] = set_dict_attrs({}, {'.'.join(key_parts[1:]): values.values()[0]})
    else:
        d[key_parts[:1][0]] = values.values()[0]
    return d


def del_dict_attrs(d, key):
    key_parts = key.split('.')
    if len(key_parts) > 1:
        d[key_parts[:1][0]] = del_dict_attrs(d[key_parts[:1][0]], '.'.join(key_parts[1:]))
    else:
        del d[key_parts[:1][0]]
    return d


def set_metadata(d, metadata):
    """
    Build conversation's metadata using the layer data schema
    :param d: dict() - Origin metadata
    :param metadata: list() - List of dictionaries for adding info
    :return: Final metadata
    """
    for data in metadata:
        d = set_dict_attrs(d, {'.'.join(data.keys()[0].split('.')[1:]): data.values()[0]})
    return d


def delete_metadata(d, keys):
    for data in keys:
        d = del_dict_attrs(d, '.'.join(data.split('.')[1:]))
    return d