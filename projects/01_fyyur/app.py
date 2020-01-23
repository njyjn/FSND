#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import load_only
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import config
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  genres = db.Column(db.ARRAY(db.String(120)))
  website = db.Column(db.String(120))
  sticky_title = db.Column(db.String(120))
  sticky_message = db.Column(db.String(120))
  artists = db.relationship('Show', back_populates="venue")

  def __repr__(self):
    return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String(120)))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  website = db.Column(db.String(120))
  sticky_title = db.Column(db.String(120))
  sticky_message = db.Column(db.String(120))
  venues = db.relationship('Show', back_populates='artist')

class Show(db.Model):
  __tablename__ = 'shows'

  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
  start_time = db.Column(db.DateTime, primary_key=True)
  artist = db.relationship('Artist', back_populates='venues')
  venue = db.relationship('Venue', back_populates='artists')
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if not isinstance(value, datetime):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  q = Venue.query
  areas = q.distinct(Venue.city, Venue.state).options(load_only('city', 'state')).order_by('state','city').all()
  for area in areas:
    venues = (
      q.add_columns(Venue.id, Venue.name, func.count(Show.venue_id).label('num_upcoming_shows'))
        .join(Show, and_(Venue.id==Show.venue_id, Show.start_time >= func.now()), full=True)
        .group_by(Venue.id)
        .filter(Venue.city==area.city, Venue.state==area.state).order_by(Venue.name)
        .all()
    )
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venues
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  results = (Venue.query.filter(or_(
    Venue.name.ilike(f'%{search_term}%'),
    Venue.city.ilike(f'%{search_term}%'),
    Venue.state.ilike(f'%{search_term}%')
    ))
    .add_columns(Venue.id, Venue.name, Venue.city, Venue.state,func.count(Show.venue_id).label('num_upcoming_shows'))
    .join(Show, and_(Venue.id==Show.venue_id, Show.start_time >= func.now()), full=True)
    .group_by(Venue.id).all()
  )
  response={
    "count": len(results),
    "data": results
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter(Venue.id==venue_id).first()
  if venue is None:
    flash('Venue not found!')
    abort(404)
  q = Show.query.filter(Show.venue_id==venue_id)
  upcoming_shows = (q
    .filter(Show.start_time >= func.now())
    .all()
  )
  past_shows = (q
    .filter(Show.start_time < func.now())
    .all()
  )
  return render_template('pages/show_venue.html', venue=venue, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'], 
    phone = request.form['phone'],
    genres = request.form.getlist('genres'),
    website = request.form['website'],
    facebook_link = request.form['facebook_link']
  )
  try:
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  data = venue
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    abort(500)
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  resp = {}
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    resp['ok'] = not error
  if not error:
    flash('Venue ' + venue.name + ' was successfully deleted!')
  else:
    flash('An error occurred. Venue could not be deleted.')
    abort(500)
  return jsonify(resp)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue is None:
    flash('Venue not found')
    abort(404)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue_id=venue_id)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    Venue.query.filter(Venue.id==venue_id).update({
      'name': request.form['name'],
      'city': request.form['city'],
      'state': request.form['state'],
      'address': request.form['address'],
      'phone': request.form['phone'],
      'genres': request.form.getlist('genres'),
      'website': request.form['website'],
      'facebook_link': request.form['facebook_link']
    })
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    abort(500)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  results = (Artist.query.filter(or_(
    Artist.name.ilike(f'%{search_term}%')
  )).all()
  )
  response={
    "count": len(results),
    "data": results
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.filter(Artist.id==artist_id).first()
  if artist is None:
    flash('Artist not found!')
    abort(404)
  q = Show.query.filter(Show.artist_id==artist_id)
  upcoming_shows = (q
    .filter(Show.start_time >= func.now())
    .all()
  )
  past_shows = (q
    .filter(Show.start_time < func.now())
    .all()
  )
  return render_template('pages/show_artist.html', artist=artist, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist is None:
    flash('Artist not found')
    abort(404)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist_id=artist_id)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    Artist.query.filter(Artist.id==artist_id).update({
      'name': request.form['name'],
      'city': request.form['city'],
      'state': request.form['state'],
      'phone': request.form['phone'],
      'genres': request.form.getlist('genres'),
      'website': request.form['website'],
      'facebook_link': request.form['facebook_link']
    })
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    abort(500)

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  artist = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    genres = request.form.getlist('genres'),
    website = request.form['website'],
    facebook_link = request.form['facebook_link']
  )
  try:
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  data = artist
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
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

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
