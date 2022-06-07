#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, Response, flash, redirect, url_for, request
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_wtf import Form
from datetime import datetime
from models import app, db, Venue, Artist, Show
import json

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# boolean values for database bool
def seeking_bool(attribute):
    if attribute== 'y':
      return True
    else:
      return False

def flash_message(error,success,fail):
  if error==True:
    return flash(fail)
  else:
    return flash(success)

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
  data=[]
  error = False
  try:
    states = db.session.query(Venue.city, Venue.state).group_by(Venue.city).group_by(Venue.state).all()
    for state in states:
      states_dict = {}
      states_dict['city'] = state[0]
      states_dict['state'] = state[1]
      states_dict['venues'] = []
      venues = Venue.query.filter_by(city=states_dict['city'], state=states_dict['state']).all()
      for venue in venues:
        states_dict['venues'].append({ 
          'id' : venue.id,
          'name' : venue.name,
          "num_upcoming_shows": len([show for show in venue.artists if show.start_time < datetime.now()]),
        })
      data.append(states_dict)
  except:
    error=True
    print(sys.exc_info)
  finally:
    db.session.close()
  flash_message(error=error, success="Venues loaded successfully", fail='Venues could not be loaded')
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  error = False
  try:
    search_term=request.form.get('search_term', '')
    response=Venue.query.filter(Venue.name.ilike("%"+search_term+"%")).all()
  except:
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  flash_message(error=error, success="Venues search successfully results will appear soon", fail='Venues search could not be loaded')
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = {}# TODO: replace with real venue data from the venues table, using venue_id
  try:
    venue=Venue.query.get(venue_id)
    data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address":venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.venue_image_link,
  }
    data["past_shows"]= []
    data['upcoming_shows'] = []

    artists= Show.query.filter(Show.venue_id==venue_id)
    for artist in artists:
      dict = {}
      date_now=datetime.now()
      if date_now > artist.start_time:
        dict['artist_id']= artist.artists.id
        dict['artist_name']= artist.artists.name
        dict['artist_image_link']= artist.artists.image_link
        dict['start_time'] = str(artist.start_time)
        data["past_shows"].append(dict)
      else:
        dict['artist_id']= artist.artists.id
        dict['artist_name']= artist.artists.name
        dict['artist_image_link']= artist.artists.image_link
        dict['start_time'] = str(artist.start_time)
        data['upcoming_shows'].append(dict)
    
    data["past_shows_count"]= len(data['past_shows'])
    data["upcoming_shows_count"]= len(data['upcoming_shows'])
  except:
    print(sys.exc_info)
  finally:
    db.session.close()
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
   
  form = VenueForm(request.form)
  if form.validate():
    flash('Validation successful')
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state= request.form.get('state')
      address= request.form.get('address')
      phone= request.form.get('phone')
      genres= request.form.getlist('genres')
      venue_image_link= request.form.get('image_link')
      facebook_link= request.form.get('facebook_link')
      website_link= request.form.get('website_link')
      seeking_description= request.form.get('seeking_description')
      seeking_talent= request.form.get('seeking_talent')

      new_venue = Venue(name=name, 
        city=city, 
        state=state,
        address=address,
        phone=phone,
        genres=genres,
        venue_image_link=venue_image_link,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_description=seeking_description,
        seeking_talent=seeking_bool(seeking_talent)
      )
    
      db.session.add(new_venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    flash_message(error=error, success="Venue created successfully", fail='Venues could not be created')
  else:
    flash("Validation not successful check your inputs well")
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error=False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  flash_message(error=error, success="Venue deleted successfully", fail='Venues could not be deleted')

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  error= False
  
  data=Artist.query.all()
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  try:
    search_term=request.form.get('search_term', '')
    response=Venue.query.filter(Artist.name.ilike("%"+search_term+"%")).all()
  except:
    print(sys.exc_info)
  finally:
    db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data= { }
  artist=Artist.query.get(artist_id)
  data['id']= artist_id
  data['name']= artist.name
  data['genres'] = artist.genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website']= artist.website_link
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist.seeking_venue
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
  data['past_shows'] = [ ]
  data['upcoming_shows'] = [ ]
  for show in artist.venues:
    show_dict = {}
    if  show.start_time < datetime.now():
      show_dict['venue_id'] = show.venues.id
      show_dict['venue_name'] = show.venues.name
      show_dict['venue_image_link'] = show.venues.venue_image_link
      show_dict['start_time'] = str(show.start_time)
      data['past_shows'].append(show_dict)
    else:
      show_dict['venue_id'] = show.venues.id
      show_dict['venue_name'] = show.venues.name
      show_dict['venue_image_link'] = show.venues.venue_image_link
      show_dict['start_time'] = str(show.start_time)
      data['upcoming_shows'].append(show_dict)

  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  form = ArtistForm(
    city= artist.city,
    facebook_link= artist.facebook_link,
    genres = artist.genres,
    image_link = artist.image_link,
    name = artist.name,
    phone = artist.phone,
    seeking_description = artist.seeking_description,
    seeking_venue = artist.seeking_venue,
    state = artist.state,
  )
  
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm(request.form)
  if form.validate():
    flash('Validation successful')
    try:
      name= request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_venue = request.form.get('seeking_venue')
      seeking_description = request.form.get('seeking_description')

      update_artist = Artist.query.get(artist_id)
      update_artist.name = name
      update_artist.city = city
      update_artist.state = state
      update_artist.phone = phone
      update_artist.image_link = image_link
      update_artist.genres = genres
      update_artist.facebook_link = facebook_link
      update_artist.website_link = website_link
      update_artist.seeking_venue = seeking_bool(seeking_venue)
      update_artist.seeking_description = seeking_description
      db.session.add(update_artist)
      db.session.commit()
    except:
      error=True
      print(sys.exc_info())
      db.session.rollback()
    finally:
      db.session.close()
    flash_message(error=error, success="Artist updated successfully", fail='Artist could not be updated')
  else:
    flash("Validation not successful check your inputs well")
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(
    name= venue.name,
    city= venue.city,
    state= venue.state,
    address= venue.address,
    phone= venue.phone,
    image_link= venue.venue_image_link,
    genres= venue.genres,
    facebook_link= venue.facebook_link,
    website_link = venue.website_link,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description
  )


  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm(request.form)
  if form.validate():
    flash('Validation successful')
    try:
      name= request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      website_link = request.form.get('website_link')
      seeking_talent = request.form.get('seeking_talent')
      seeking_description = request.form.get('seeking_description')
  
      
      update_venue = Venue.query.get(venue_id)
      update_venue.name = name
      update_venue.city = city
      update_venue.state = state
      update_venue.phone= phone
      update_venue.venue_image_link= image_link
      update_venue.genres = genres
      update_venue.facebook_link = facebook_link
      update_venue.website_link = website_link
      update_venue.seeking_talent = seeking_bool(seeking_talent)
      update_venue.seeking_description = seeking_description
      db.session.add(update_venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
    flash_message(error=error, success="Venue edited successfully", fail='Venue could not be edited')
  else:
    flash("Validation not successful check your inputs well")
 
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
  # TODO: insert form data as a new Venue record in the db, instead

  # body = {}
  error = False
  form = ArtistForm(request.form)
  if form.validate():
    flash('Validation successful')
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state =  request.form.get('state')
      phone= request.form.get('phone')
      genres= request.form.getlist('genres')
      venue_image_link= request.form.get('image_link')
      facebook_link= request.form.get('facebook_link')
      website_link= request.form.get('website_link')
      seeking_description= request.form.get('seeking_description')
      seeking_venue= request.form.get('seeking_venue')

      new_artist = Artist(
        name=name, 
        city=city, 
        state=state,
        phone=phone,
        genres=genres,
        image_link=venue_image_link,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_description=seeking_description,
        seeking_venue=seeking_bool(seeking_venue)
      )
    
      db.session.add(new_artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if error==False:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      flash('Artist ' + request.form['name'] + ' was not successfully listed! E be like say you too broke' )
  else:
    flash("Validation not successful check your inputs well") 
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  shows= Show.query.all()
  for show in shows:
    show_dict = {}
    show_dict['venue_id'] = show.venues.id
    show_dict['venue_name'] = show.venues.name
    show_dict['artist_name'] = show.artists.name
    show_dict['artist_id']= show.artists.id
    show_dict['artist_image_link'] = show.artists.image_link
    show_dict['start_time'] = str(show.start_time)
    data.append(show_dict)

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
  error=False
  # body = {}
  form = ShowForm(request.form)
  if form.validate():
    flash('Validation successful')
    try:
      venue_id = request.form.get('venue_id')
      artist_id = request.form.get('artist_id')
      start_time = request.form.get('start_time')
      show_venue= Venue.query.get(venue_id)
      show_artist= Artist.query.get(artist_id)
      new_show = Show(start_time=start_time)
      new_show.artists = show_artist
      new_show.venues = show_venue
      db.session.add(new_show)
      db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    flash_message(error=error, success="Show created successfully", fail='Show could not be created')
  else:
    flash("Validation not successful check your inputs well") 
  # on successful db insert, flash success
 
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
