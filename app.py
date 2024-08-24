from flask import Flask, request
from flask_cors import CORS
from dotenv import dotenv_values
from pymongo import MongoClient
from users import *
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
    ret = '' #check_class(auth.username, auth.password, db)
    
    if ret != None:
        return {'message' : 'User found successfully.', "data" : ret}, 200
    else:
        return {'message' : 'User not found.', "data" : ret}, 400
    
#--------------------------------- USERS ---------------------------------

@app.route('/users', methods=['GET'])
@app.route('/users/<string:id>', methods=['GET'])
def read_users(id=None):
    kwargs = request.args.to_dict()
    return get_users(db, id, kwargs)

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
    return

@app.route('/events', methods=['POST'])
def post_events():
    return

@app.route('/events/<string:id>', methods=['PUT'])
def put_events(id):
    return

@app.route('/events/<string:id>', methods=['DELETE'])
def delete_events(id):
    return


if __name__ == '__main__':
    app.run(debug=True)