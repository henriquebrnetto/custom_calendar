from utils import check_email, remove_objId, check_date
from auth import hash_password
from datetime import datetime
from bson import ObjectId
import bson

"""
db.users.find_one(filter={})
db.users.find({})

db.users.update_one({'_id': id}, {'$set': user})

db.users.insert_one(user)

db.users.delete_one(filter)
"""

#GET all users or by ID
def get_users(db, id=None, kwargs={}):

    try:
        filter = {'_id': ObjectId(id)} if id else {}
    except bson.errors.InvalidId:
        return {'message' : 'Invalid ID.', 'data' : []}, 400
    
    if kwargs:
        filter.update(kwargs)

    users = remove_objId(db.users.find(filter))

    if users == []:
        return {'message' : 'No user found.', 'data' : users}, 400
    else:
        return {'message' : 'Users found', 'data' : users[0] if len(users) == 1 else users}, 200
    
#POST user 
def post_user(db, user):
    mandatory_keys = {'name', 'email', 'psswd', 'birth_date', 'job_position', 'company'}

    if not mandatory_keys.issubset(set(user.keys())):
        return {"message": f"Todos os campos são obrigatórios ({', '.join(mandatory_keys - set(user.keys()))})", 'data' : user}, 400
    
    if not check_email(user['email']):
        del user['psswd']
        return {"message": "Email inválido.", 'data' : user}, 400
    
    if get_users(db, kwargs={'email' : user['email']})[1] == 200:
        del user['psswd']
        return {"message": "Email já cadastrado.", 'data' : user}, 409
    
    #BLOCO TEMPORÁRIO
    try:
        user['birth_date'] = check_date(user['birth_date'])
    except Exception as e:
        return {'message' : f'Erro {e}', 'data' : user}, 400
    #----------

    if "auth" not in user:
        user['auth'] = "user"

    new_vals = {
            "psswd" : hash_password(user['psswd']),
            "tasks" : [],
            "rec_code" : -1,
            "register_date" : datetime.today().isoformat()
        }
    
    user.update(new_vals)

    try:
        db.users.insert_one(user)
    except Exception as e:
        return {'message' : f'Erro {e}', 'data' : user}, 500

    return {'message' : 'Usuário adicionado com sucesso.', 'data' : remove_objId(user)}, 201

def del_user(db, id, logged_username=None):
    user = get_users(db, id)[0]['data']
    if user == []:
        return {"message":'User not found.', 'data' : id}, 404
    
    try:
        d_user = user.copy()
        updates = {
            '_id' : ObjectId(id),
            "psswd" : "#",
            "deleted_by" : db.users.find_one({'email' : logged_username}, {'_id' : 1, 'name' : 1}) if logged_username != None else {"_id" : "", "name" : ""},
            "deletion_date" : datetime.today().isoformat()
        }
        d_user.update(updates)

        db.users_deleted.insert_one(d_user)
        db.users.delete_one({'_id': ObjectId(id)})

    except Exception as e:
        return {"message":'Error while trying to delete user.', 'data' : user}, 400
    
    return {"message": 'User deleted successfully.', 'data' : user}, 200

def edit_user(db, id, updates):
    id = ObjectId(id)
    user, code = get_users(db, id)
    user = user['data']
    if code != 200:
        return {"message":'User not found.', 'data' : []}, 404
    try:
        if 'email' in updates:
            return {"message":'Unauthorized to update e-mail', 'data' : updates}, 400
        
        if 'psswd' in updates:
            updates['psswd'] = hash_password(updates['psswd'])

        db.users.update_one({'_id': id}, {'$set': updates})
        user.update(updates)

    except:
        return {"message":'Error while trying to update user information.', 'data' : updates}, 500
    return {"message":'User updated successfully.', 'data' : user}, 200


# ---------------------------- PAREI AQUI ----------------------------

def recovery_code(db, id, code):
    db.users.update_one({'_id': ObjectId(id)}, {"$set": {'recovery_code' : code}})
    return {'message' : 'Information updated successfully.'}, 200


def change_password(db, id, new_psswd):
    new_psswd = hash_password(new_psswd)
    filter = {'_id': ObjectId(id)}
    try:
        db.users.update_one(filter, {"$set":{'senha':new_psswd, 'recovery_code': 0}})
        return {'message': 'Password changed successfully.'}, 200
    except:
        return {'message': 'Error while trying to update password.'}, 400