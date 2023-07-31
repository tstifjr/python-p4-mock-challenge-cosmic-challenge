from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates = 'planet', cascade = 'all, delete-orphan')
    scientists = association_proxy('missions', 'scientist')

    # Add serialization rules
    serialize_rules = ('-missions', '-scientists')


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    field_of_study = db.Column(db.String, nullable = False)

    # Add relationship
    missions = db.relationship('Mission', back_populates = 'scientist', cascade = 'all, delete-orphan')
    planets = association_proxy('missions', 'planet')

    # Add serialization rules
    serialize_rules = ('-missions.scientist', )

    # Add validation
    @validates('name')
    def validates_name (self, key, given_name):
        if not given_name:
            raise ValueError ('no name given')

        return given_name

    @validates('field_of_study')
    def validates_field_of_study (self, key, given_field_of_study):
        if not given_field_of_study:
            raise ValueError ('no field_of_study given')

        return given_field_of_study


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable = False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable = False)

    # Add relationships
    scientist = db.relationship ('Scientist', back_populates = 'missions')
    planet = db.relationship ('Planet', back_populates = 'missions')
    
    # Add serialization rules
    serialize_rules = ('-scientist.missions', '-planet.missions')
    # Add validation
    
    @validates('name')
    def validates_name (self, key, given_name):
        if not given_name:
            raise ValueError ('no name given')

        return given_name
    
    @validates('scientist_id')
    def validates_scientist_id (self, key, given_scientist_id):
        if not given_scientist_id:
            raise ValueError ('no scientist_id given')

        return given_scientist_id

    @validates('planet_id')
    def validates_planet_id (self, key, given_planet_id):
        if not given_planet_id:
            raise ValueError ('no planet_id given')

        return given_planet_id
# add any models you may need.
