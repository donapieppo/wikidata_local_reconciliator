import re

def extract_year_from_wikidata_date(date):
    if date:
        a = date.split('-')
        if len(a) > 0:
            return(a[0])
        else:
            return(False)
    else:
        return(False)

def split_names(names, separator=None):
    huntington_library = re.search('(\w+)\s*,\s*(\w+).*\d*.*', names)
    if separator:
        return(names.split(separator))

    if huntington_library:
        return([huntington_library[2] + " " + huntington_library[1]])
    if re.search(",", names):
        return(names.split(','))
    elif re.search(" e ", names):
        return(names.split(' e '))
    else:
        return(names.split(','))

def update_if_different(db, new_hash, creator):
    updated = False
    
    if creator.name != new_hash['label']: 
        print(f"INCOHERENT name -{creator.name}- != -{new_hash['name']}-")
        creator.name = new_hash['label']
        updated = True

    if 'viaf_id' in new_hash and str(new_hash['viaf_id']) != str(creator.viaf_id):
        print(f"INCOHERENT viaf {creator.viaf_id} != {new_hash['viaf_id']}")
        creator.viaf_id = new_hash['viaf_id']
        updated = True

    db.session.commit()
    return(updated)
