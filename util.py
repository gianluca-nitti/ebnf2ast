import re

def sanitize_name(s):
    return re.sub('\W|^(?=\d)','', s)

def unique_name(base_name, name_set):
    (name, i) = (base_name, 1)
    while name in name_set: # TODO move to a function...
        (name, i) = ('%s_%d' % (base_name, i), i + 1)
    name_set.add(name)
    return name

def unique_sanitized_name(preferred_name, name_set):
    return unique_name(sanitize_name(preferred_name), name_set)
