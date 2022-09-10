# from sqlalchemy import Column, String, Integer
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(500))
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary='shows', backref=db.backref('venues', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(500))
    seeking_description = db.Column(db.String(500))

Shows = db.Table('shows',
  db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), nullable=False, primary_key=True),
  db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), nullable=False, primary_key=True),
  db.Column('start_time', db.DateTime, nullable=True)
)