import re

def sanitize_name(s, keywords):
    s = re.sub('\W|^(?=\d)','', s)
    if s in keywords:
        s = '_%s' % s
    assert s not in keywords, 'Name conflicts with keyword'
    return s

def unique_name(base_name, name_set):
    (name, i) = (base_name, 1)
    while name in name_set:
        (name, i) = ('%s_%d' % (base_name, i), i + 1)
    name_set.add(name)
    return name

def unique_sanitized_name(preferred_name, name_set, keywords):
    return unique_name(sanitize_name(preferred_name, keywords), name_set)
