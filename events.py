from utils import remove_objId
from auth import hash_password
from datetime import datetime
from users import get_user
from bson import ObjectId
import bson

#GET all events or by ID
def get_events(db, user, id=None, kwargs={}):

    try:
        filter = {'_id': ObjectId(id)} if id else {}
    except bson.errors.InvalidId:
        return {'message' : 'Invalid ID.', 'data' : []}, 400

    #-------------- GARANTIR QUE ESTÁ LOGADO (FAZER FUNÇÃO)

    if kwargs:
        filter.update(kwargs)

    events = remove_objId(db.events.find(filter))

    if events == []:
        return {'message' : 'No event found.', 'data' : events}, 400
    else:
        return {'message' : 'Events found', 'data' : events[0] if len(events) == 1 else events}, 200
    
#POST event 
def post_event(db, event, user):
    mandatory_keys = {'name', 'category', 'start_date', 'end_date'}

    if not mandatory_keys.issubset(set(event.keys())):
        return {"message": f"Todos os campos são obrigatórios ({', '.join(mandatory_keys - set(event.keys()))})", 'data' : event}, 400

    #GARANTIR QUE ESTÁ LOGADO (FAZER FUNÇÃO)
    user, code = get_user(db, kwargs={'email' : user[0], 'psswd' : hash_password(user[1])})
    if code != 200:
        return {"message":'Not logged in.', 'data' : event}, 400

    new_vals = {
        'owners' : {'_id' : user['data']['_id'] if 'owners' not in event else event['owners']['_id']},
        "creation_date" : datetime.today().isoformat(),
        "created_by" : {'_id' : user['data']['_id'],
                         'name' : user['data']['name']},
        "last_update" : datetime.today().isoformat()
    }
    
    event.update(new_vals)

    try:
        db.events.insert_one(event)
    except Exception as e:
        return {'message' : f'Erro {e}', 'data' : event}, 500

    return {'message' : 'Evento adicionado com sucesso.', 'data' : remove_objId(event)}, 201

def del_event(db, id, logged_username=None):

    event = get_events(db, id)[0]['data']
    if event == []:
        return {"message":'event not found.', 'data' : id}, 404
    
    try:
        d_event = event.copy()
        updates = {
            '_id' : ObjectId(id),
            "psswd" : "#",
            "deleted_by" : db.events.find_one({'email' : logged_username}, {'_id' : 1, 'name' : 1}) if logged_username != None else {"_id" : "", "name" : ""},
            "deletion_date" : datetime.today().isoformat()
        }
        d_event.update(updates)

        db.events_deleted.insert_one(d_event)
        db.events.delete_one({'_id': ObjectId(id)})

    except Exception as e:
        return {"message":'Error while trying to delete event.', 'data' : event}, 400
    
    return {"message": 'Event deleted successfully.', 'data' : event}, 200

def edit_event(db, id, updates):
    id = ObjectId(id)
    event, code = get_events(db, id)
    event = event['data']
    if code != 200:
        return {"message":'Event not found.', 'data' : []}, 404
    
    if 'created_by' in updates or 'creation_date' in updates or 'last_update' in updates:
        return {"message":'You cannot change the creation data of an event.', 'data' : event}, 400

    try:
        updates['last_update'] = datetime.today().isoformat()
        db.events.update_one({'_id': id}, {'$set': updates})
        event.update(updates)

    except:
        return {"message":'Error while trying to update event information.', 'data' : updates}, 500
    return {"message":'Event updated successfully.', 'data' : event}, 200