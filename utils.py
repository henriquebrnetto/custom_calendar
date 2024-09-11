from pymongo import cursor
from datetime import datetime, date


def check_email(email):
    end = False
    for s in ['.edu.br', '.com', '.com.br']:
        if email.endswith(s):
            end = True
            break
    return '@' in email and end

def check_date(d, tz = None):
    if type(d) not in [date, datetime]:
        d = datetime.strptime(d, "%d/%m/%Y").isoformat()
    
    return d

def remove_objId(object):
    if type(object) == cursor.Cursor:
        object = list(object)

    if type(object) == dict:
        object.update({'_id' : str(object['_id'])})

    if type(object) == list:
        [obj.update({'_id' : str(obj['_id'])}) if 'deleted_by' not in obj else obj.update({'_id' : str(obj['_id']), 'deleted_by._id' : str(obj['deleted_by']['_id'])}) for obj in object]

    return object