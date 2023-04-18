def extract_value(json_obj, path):
    keys = path.split('.')
    current = json_obj
    for key in keys:
        try:
            current = current[key]
        except (KeyError, TypeError):
            return None
    return current

def check_value(json_obj, path, expected):
    """ check_value(json_obj, "abels.en.value", "pippo") """
    return extract_value(json_obj, path) == expected

def extract_datavalue(j):
    """ extract_datavalue(J['claims']['P214'][0]) """
    try:
        if check_value(j, 'mainsnak.snaktype', 'novalue'):
            return None
        elif check_value(j, 'mainsnak.datatype', 'external-id'):
            return extract_value(j, 'mainsnak.datavalue.value')
        elif check_value(j, 'mainsnak.datatype', 'wikibase-item'):
            return extract_value(j, 'mainsnak.datavalue.value.id')
        elif check_value(j, 'mainsnak.datatype', 'time'):
            return extract_value(j, 'mainsnak.datavalue.value.time')
        else:
            print("extract_datavalue error")
            print(j['mainsnak'])
            exit(0) 
    except (KeyError, TypeError):
        # can happen instance of is not a valid qualifier for ....
        print(j["id"])
        print(j['mainsnak'])
        return None
