from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient
from users import *
from events import *
from auth import config

app = Flask("Custom Calendar")
CORS(app)

client = MongoClient(config["MONGODB_URL"])
db = client['customCalendar']

#--------------------------------- ROUTES ---------------------------------

#--------------------------------- HOME ---------------------------------

@app.route('/', methods=['GET'])
def home():
    return {'message' : 'Welcome :)'}, 200

#--------------------------------- LOGIN ---------------------------------

@app.route('/login', methods=['GET'])
def login():
    auth = request.authorization
    user, code = get_user(db, kwargs={'email' : auth.username, 'psswd' : hash_password(auth.password)})

    if code == 200:
        return {'message' : 'User found successfully.', "data" : user}, 200
    else:
        return {'message' : 'User not found.', "data" : user}, 400
    
#--------------------------------- USERS ---------------------------------

@app.route('/users', methods=['GET'])
@app.route('/users/<string:id>', methods=['GET'])
def read_users(id=None):
    kwargs = request.args.to_dict()
    return get_user(db, id, kwargs)

@app.route('/users', methods=['POST'])
def post_users():
    return post_user(db, request.json)

@app.route('/users/<string:id>', methods=['PUT'])
def put_users(id):
    return edit_user(db, id, request.json)

@app.route('/users/<string:id>', methods=['DELETE'])
def delete_users(id):
    user = request.authorization.username if request.authorization else None
    return del_user(db, id, user)

#--------------------------------- EVENTOS E ATIVIDADES ---------------------------------

@app.route('/events', methods=['GET'])
@app.route('/events/<string:id>', methods=['GET'])
def read_events(id=None):
    kwargs = request.args.to_dict()
    #GARANTIR QUE ESTÁ LOGADO
    user = (request.authorization.username, request.authorization.password) if request.authorization else None
    return get_events(db, user, id, kwargs)

@app.route('/events', methods=['POST'])
def post_events():
    #GARANTIR QUE ESTÁ LOGADO
    user = (request.authorization.username, request.authorization.password) if request.authorization else None
    return post_event(db, request.json, user)

@app.route('/events/<string:id>', methods=['PUT'])
def put_events(id):
    return

@app.route('/events/<string:id>', methods=['DELETE'])
def delete_events(id):
    return


if __name__ == '__main__':
    app.run(debug=True)