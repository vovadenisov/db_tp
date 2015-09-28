import re

def validate_date(date):
    if date is None:
        return None
    pattern = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}-[0-9]{2}-[0-9]{2}')
    if not pattern.match(date)
        return False
    date = date[::-1].replace('-', ':', 2)[::-1]
    return date

def validate_id(id_):
    if id_ is None:
        return None
    try:
         return int(id_)
    except ValueError:
         return False

