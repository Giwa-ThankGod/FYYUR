#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

# TODO: implement any missing fields, as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  venue = Venue.query.all()
  return render_template('pages/venues.html', areas=venue);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
  response={
    "count": data.count(),
    "data": data,
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  venue = Venue.query.get(venue_id)
  past_show = []
  upcoming_show = []

  past_shows = db.session.query(Show).join(Venue).\
    filter(Show.venue_id==venue_id).\
      filter(Show.start_time<datetime.now()).all()

  upcoming_shows = db.session.query(Show).join(Venue).\
  filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()

  for info in past_shows:
    show = {
      "artist_id": info.artist.id,
      "artist_name": info.artist.name,
      "artist_image_link": info.artist.image_link,
      "start_time": str(info.start_time)
    }
    past_show.append(show)

  for info in upcoming_shows:
    show = {
      "venue_id": info.venue.id,
      "venue_name": info.venue.name,
      "venue_image_link": info.venue.image_link,
      "start_time": str(info.start_time)
    }
    upcoming_show.append(show)
  # print(venue.genres)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(","),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_venue,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
    
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    form = VenueForm(request.form)

    venue_name=request.form['name']
    venue = Venue(
      name= form.name.data,
      city= form.city.data,
      state= form.state.data,
      address= form.address.data,
      phone= form.phone.data,
      genres= form.genres.data,
      facebook_link= form.facebook_link.data,
      image_link= form.image_link.data,
      website_link= form.website_link.data,
      seeking_venue= form.seeking_talent.data,
      seeking_description= form.seeking_description.data,
    )
    db.session.add(venue)
    db.session.commit()
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Venue ' + venue_name + ' was successfully listed!')
  except Exception as err:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + venue_name + ' could not be listed. Error: {}'.format(err))
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.filter_by(id=venue_id).delete()  
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  artist = Artist.query.all()
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
  response={
    "count": data.count(),
    "data": data,
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  artist = Artist.query.get(artist_id)
  past_show = []
  upcoming_show = []

  past_shows = db.session.query(Show).join(Venue).\
    filter(Show.artist_id==artist_id).\
      filter(Show.start_time<datetime.now()).all()

  upcoming_shows = db.session.query(Show).join(Venue).\
  filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()

  for info in past_shows:
    show = {
      "venue_id": info.venue.id,
      "venue_name": info.venue.name,
      "venue_image_link": info.venue.image_link,
      "start_time": str(info.start_time)
    }
    past_show.append(show)

  for info in upcoming_shows:
    show = {
      "venue_id": info.venue.id,
      "venue_name": info.venue.name,
      "venue_image_link": info.venue.image_link,
      "start_time": str(info.start_time)
    }
    upcoming_show.append(show)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(","),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj = artist)
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    artist.genres=request.form.getlist('genres')
    artist.facebook_link=request.form['facebook_link']
    artist.image_link=request.form['image_link']
    artist.website_link=request.form['website_link']
    artist.seeking_venue=request.form['seeking_venue']
    artist.seeking_description=request.form['seeking_description']
    
    db.session.commit()
  except:
    db.session.rollback()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj = venue)
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  # print(request.form.getlist('genres'))

  try:
    venue = Venue.query.get(venue_id)
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.state=request.form['state']
    venue.address=request.form['address']
    venue.phone=request.form['phone']
    venue.genres=request.form.getlist('genres')
    venue.facebook_link=request.form['facebook_link']
    venue.image_link=request.form['image_link']
    venue.website_link=request.form['website_link']
    venue.seeking_venue=request.form['seeking_venue']
    venue.seeking_description=request.form['seeking_description']
    
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  try:
    # TODO: insert form data as a new Venue record in the db, instead
    artist_name = request.form['name']
    artist = Artist(
      name=artist_name,
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      website_link=request.form['website_link'],
      seeking_venue=request.form['seeking_venue'],
      seeking_description=request.form['seeking_description'],
      )
    db.session.add(artist)
    db.session.commit()
    # artist_data = Artist.query.all()
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for dataa in shows:
    info = {
        "venue_id": dataa.venue.id,
        "venue_name": dataa.venue.name,
        "artist_id": dataa.artist.id,
        "artist_name": dataa.artist.name,
        "artist_image_link": dataa.artist.image_link,
        "start_time": str(dataa.start_time),
    }
    data.append(info)

  
  # for venue in venues:
  #   


  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except Exception as err:
    db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed. Error: {}'.format(err))
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
