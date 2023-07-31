#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists (Resource):
    def get(self):
        scientist_list = []
        for s in Scientist.query.all():
            s_dict = s.to_dict()
            s_dict.pop('missions')
            scientist_list.append(s_dict)
        
        return make_response(scientist_list, 200)\
    
    def post(self):
        data = request.get_json()
        try:
            new_scientist = Scientist(name = data['name'], field_of_study = data['field_of_study'])
            db.session.add(new_scientist)
            db.session.commit()

            return make_response(new_scientist.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Scientists, '/scientists')

class ScientistById (Resource):
    def get(self, id):
        try:
            scientist = Scientist.query.filter(id == Scientist.id).first().to_dict()
            return make_response(scientist, 200)
        except:
            return make_response({"error": "Scientist not found"}, 404)
    
    def patch(self, id):
        scientist = Scientist.query.filter(id == Scientist.id).first()
        if scientist == None:
            return make_response({"error": "Scientist not found"}, 404)
        
        try:
            data = request.get_json()
            for attr in data:
                setattr(scientist, attr, data[attr])
            db.session.commit()
            return make_response(scientist.to_dict(), 202)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
    
    def delete(self, id):
        try:
            scientist = Scientist.query.filter(id == Scientist.id).first()
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)
        
        except:
            return make_response({"error": "Scientist not found"}, 404)        

api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        return make_response([planet.to_dict() for planet in Planet.query.all()], 200)

api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_mission = Mission(name = data['name'], planet_id = data['planet_id'], scientist_id = data['scientist_id'])
            db.session.add(new_mission)
            db.session.commit()

            return make_response(new_mission.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
