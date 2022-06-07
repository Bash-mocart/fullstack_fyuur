from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#------------------------------- ---------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



class Show(db.Model):
    __tablename__ = 'Show'
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime)
    venues = db.relationship('Venue', back_populates="artists", cascade='all,  delete-orphan', single_parent=True)
    artists = db.relationship('Artist', back_populates="venues", cascade='all, delete-orphan', single_parent=True)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120)) 
    genres = db.Column(db.ARRAY(db.String()))
    venue_image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_description= db.Column(db.String()) 
    seeking_talent= db.Column(db.Boolean, default=False)
    artists= db.relationship("Show", lazy=True, back_populates='venues')
    
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model): 
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_description= db.Column(db.String())
    seeking_venue= db.Column(db.Boolean, default=False)
    venues= db.relationship("Show", lazy=True, back_populates='artists')
    
    
   


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
