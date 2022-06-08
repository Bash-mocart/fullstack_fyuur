#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import os
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  flash,
  redirect,
  url_for
)
import logging
from logging import Formatter, FileHandler

from sqlalchemy import(
  null,
  desc,
)
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

def show(artist=False, artist_id=null, venue=False, venue_id=null, past=False, incoming=null):
  if artist and past:
    shows_query= Show.query.join(Venue).with_entities(Venue.id, Venue.name, Venue.venue_image_link, Show.start_time).filter(Show.artist_id==artist_id, Show.start_time<datetime.now()).all()
    print("artist")
    return shows_query
  elif artist and incoming:
    shows_query= Show.query.join(Venue).with_entities(Venue.id, Venue.name, Venue.venue_image_link, Show.start_time).filter(Show.artist_id==artist_id, Show.start_time>datetime.now()).all()
    return shows_query
  elif venue and past:
     shows_query= Show.query.join(Artist).with_entities(Artist.id, Artist.name, Artist.image_link, Show.start_time).filter(Show.venue_id==venue_id, Show.start_time<datetime.now()).all()
     print('venue')
     return shows_query
  elif venue and incoming:
    shows_query= Show.query.join(Artist).with_entities(Artist.id, Artist.name, Artist.image_link, Show.start_time).filter(Show.venue_id==venue_id, Show.start_time>datetime.now()).all()
    print('incoming venue')
    return shows_query




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
  venues = Venue.query.order_by(desc(Venue.created)).limit(10).all()
  artists = Artist.query.order_by(desc(Artist.created)).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues(): 
  data=[]
  error = False
  try:
    states = Venue.query.with_entities(Venue.state, Venue.city).group_by(Venue.city, Venue.state).all()
    for state in states:
      states_dict = {}
      states_dict['venues'] = []
      states_dict['state'] = state[0]
      states_dict['city'] = state[1]
      venues = Venue.query.filter_by(city=states_dict['city'], state=states_dict['state']).all()
      for ven in venues:
        venue = {}
        venue['id'] = ven.id
        venue['name'] = ven.name
        shows = []
        for show in ven.artists:
          if show.start_time < datetime.now():
            shows.append(show)
          else:
            pass
        venue['num_upcoming_show'] = len(shows)
        states_dict['venues'].append(venue)
      data.append(states_dict)
  except:
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  flash_message(error=error, success="Venues loaded successfully", fail='Venues could not be loaded')
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
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
  data = {}
  try:
    venue=Venue.query.get(venue_id)
    data['id']= venue.id
    data['name'] = venue.name
    data['genres'] = venue.genres
    data['address'] = venue.address
    data['city'] = venue.city
    data['state'] = venue.state
    data['phone'] = venue.phone
    data['website'] = venue.website_link
    data['facebook_link'] = venue.facebook_link
    data['seeking_talent'] = venue.seeking_talent
    data['seeking description'] = venue.seeking_description
    data['image_link'] = venue.venue_image_link
    data["past_shows"]= []
    data['upcoming_shows'] = []

    shows_query_past= show(venue=True, venue_id=venue_id, past=True )
    shows_query_incoming= show(venue=True, venue_id=venue_id, incoming=True )
    for artist in shows_query_past:
      dict = {}
      dict['artist_id']= artist[0]
      dict['artist_name']= artist[1]
      dict['artist_image_link']= artist[2]
      dict['start_time'] = str(artist[3])
      data["past_shows"].append(dict)

    for artist in shows_query_incoming:
      dict = {}
      dict['artist_id']= artist[0]
      dict['artist_name']= artist[1]
      dict['artist_image_link']= artist[2]
      dict['start_time'] = str(artist[3])
      data['upcoming_shows'].append(dict)
    
    data["past_shows_count"]= len(data['past_shows'])
    data["upcoming_shows_count"]= len(data['upcoming_shows'])
  except:
    print(sys.exc_info())
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
    return render_template('pages/home.html')
  else:
    for value in form.errors.values():
      for val in value:
        flash(val)
    return render_template('forms/new_venue.html', form=form)
  

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

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  error= False
  
  data=Artist.query.all()
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
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

  shows_query_past= show(artist=True, artist_id=artist_id, past=True )
  shows_query_incoming= show(artist=True, artist_id=artist_id, incoming=True )
    
  for venue in shows_query_past:
    dict = {}
    dict['venue_id']= venue[0]
    dict['venue_name']= venue[1]
    dict['venue_image_link']= venue[2]
    dict['start_time'] = str(venue[3])
    data["past_shows"].append(dict)

  for venue in shows_query_incoming:
    dict = {}
    dict['venue_id']= venue[0]
    dict['venue_name']= venue[1]
    dict['venue_image_link']= venue[2]
    dict['start_time'] = str(venue[3])
    data['upcoming_shows'].append(dict)
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
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist=Artist.query.get(artist_id)
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
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    for value in form.errors.values():
        for val in value:
          flash(val)
    return render_template('forms/edit_artist.html', form=form, artist=artist)
 

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


  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form)
  venue=Venue.query.get(venue_id)
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
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    for value in form.errors.values():
        for val in value:
          flash(val)
    return render_template('forms/edit_venue.html', form=form, venue=venue)
 
 
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
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
      return render_template('pages/home.html')
    else:
      flash('Artist ' + request.form['name'] + ' was not successfully listed! E be like say you too broke' )
      return render_template('forms/new_artist.html', form=form)
    
  else:
    for value in form.errors.values():
      for val in value:
        flash(val)
    return render_template('forms/new_artist.html', form=form)

  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
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
  error=False
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
  return render_template('pages/home.html')

@app.errorhandler(400)
def not_found_error(error):
    return render_template('errors/404.html'), 400

@app.errorhandler(401)
def server_error(error):
    return render_template('errors/500.html'), 401

@app.errorhandler(403)
def server_error(error):
    return render_template('errors/500.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(422)
def not_found_error(error):
    return render_template('errors/404.html'), 422

@app.errorhandler(405)
def not_found_error(error):
    return render_template('errors/404.html'), 405

@app.errorhandler(409)
def not_found_error(error):
    return render_template('errors/404.html'), 409




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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

 