#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (Flask, render_template, request,
        Response, flash, redirect, url_for, jsonify)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db_setup
from flask_migrate import Migrate

import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = db_setup(app)


# DONE TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    sql = text('select city, state FROM public."Venue" GROUP BY city, state ORDER BY city')
    venue_groups = db.engine.execute(sql).fetchall()

    # venue_groups = db.session.query(Venue.city, Venue.state).group_by(
    #     Venue.city, Venue.state).all()
    data = []
    for venue_group in venue_groups:
        city_name = venue_group[0]
        city_state = venue_group[1]
        sql2 = text("""select * FROM public."Venue" where city = :city_name""")
        venues = db.engine.execute(sql2, city_name = city_name).fetchall()

        # removed orm syntax in favor of raw sql as per project requirements
        # filtered = db.session.query(Venue).filter(
        #     Venue.city == city_name, Venue.state == city_state)
        group = {
            "city": city_name,
            "state": city_state,
            "venues": []
        }

        # List venues in the city/state group
        for venue in venues:
            group['venues'].append({
                "id": venue.id,
                "name": venue.name,
                # "num_shows_upcoming": len(venue.shows)
            })
        data.append(group)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form['search_term']
    # Using raw sql instead of the orm syntax as required by rubric:
    sql = text('select * FROM public."Venue" where name ilike :search_string')
    results = db.engine.execute(sql, search_string='%'+search_term+'%')
    venues = results.fetchall()
    # venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
    response = {}
    response["count"] = len(venues)
    data = []
    for venue in venues:
        current_venue = {}
        current_venue["id"] = venue.id
        current_venue["name"] = venue.name
        data.append(current_venue)

    response["data"] = data

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    sql = text("""select * from public."Venue" where id = :venue_id""") 
    venue = db.engine.execute(sql, venue_id=venue_id).fetchone()

    if venue:
        related_shows = Show.query.filter_by(venue_id=venue_id).all()
        data = {
            "id": venue_id,
            "name": venue.name,
            "genres": venue.genres.split(','),
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows(related_shows),
            "upcoming_shows": upcoming_shows(related_shows),
            "past_shows_count": past_shows_count(related_shows),
            "upcoming_shows_count": upcoming_shows_count(related_shows),
        }
    else:
        flash('An error occurred. Venue id:' +
              str(venue_id) + ' could not be found.')
        return redirect(url_for('venues'))

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
    form = VenueForm()
    if form.validate():
        try:
            tmp_genres = form.genres.data
            # using raw sql instead of ORM syntax in order
            # to meet rubric
            sql = text(
                """
                INSERT INTO public."Venue"
                (name, city, state,
                address, phone, genres,
                website, facebook_link,
                image_link, seeking_talent,
                seeking_description)
                VALUES (:name, :city, :state,
                :address, :phone, :genres,
                :website, :facebook_link,
                :image_link, :seeking_talent,
                :seeking_description
                )
                """
            )
            
            db.engine.execute(
                sql, name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=','.join(tmp_genres),
                website=form.website.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            db.session.commit()
            
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] +
                    ' was successfully listed!', 'success')
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' +
                request.form['name'] + ' could not be listed.', 'error')
            return render_template('forms/new_venue.html', form=form)
        finally:
            db.session.close()


    else:
        flash(form.errors)
        return render_template('forms/new_venue.html', form=form)

    return redirect(url_for('venues'))


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    response = True
    body = []
    try:
        venue = Venue.query.get(venue_id)
        body = {
            "id": venue.id,
            "name": venue.name
        }
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()
        if error:
            response = False
            # on error, flash error message
            flash('An error occurred. Venue id:' +
                  str(venue_id) + ' could not be removed!')
            body['error'] = error
        else:
            # on successful db delete, flash success
            flash('Venue id:' + str(venue_id) + ' was successfully removed!')
            body['response'] = response

    return jsonify(body)

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    sql = text('select id, name FROM public."Artist" ORDER BY name asc')
    names = db.engine.execute(sql)
    data = names.fetchall()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form['search_term']
    # Using raw sql instead of the orm syntax as required by rubric:
    sql = text('select * FROM public."Artist" where name ilike :search_string')
    results = db.engine.execute(sql, search_string='%'+search_term+'%')
    artists = results.fetchall()

    # artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()

    response = {}
    response["count"] = len(artists)
    data = []

    for artist in artists:
        current_artist = {}
        current_artist["id"] = artist.id
        current_artist["name"] = artist.name
        data.append(current_artist)

    response["data"] = data

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    sql = text("""select * from public."Artist" where id = :artist_id""") 
    artist = db.engine.execute(sql, artist_id=artist_id).fetchone()
    # artist = Artist.query.get(artist_id)
    if artist:
        related_shows = Show.query.filter_by(artist_id=artist_id).all()
        data = {
            "id": artist_id,
            "name": artist.name,
            "genres": artist.genres.split(','),
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows(related_shows),
            "upcoming_shows": upcoming_shows(related_shows),
            "past_shows_count": past_shows_count(related_shows),
            "upcoming_shows_count": upcoming_shows_count(related_shows),
        }
    else:
        flash('An error occurred. Artist id:' +
              str(artist_id) + ' could not be found.')
        return redirect(url_for('artists'))

    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    form.genres.data = artist.genres.split(',')
    # DONE: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    # Using raw sql instead of SQLAlchemy ORM
    # artist = Artist.query.get(artist_id)
    sql = text("""select * from public."Artist" where id = :artist_id""") 
    artist = db.engine.execute(sql, artist_id=artist_id).fetchone()    
    form = ArtistForm()

    if form.validate():
        try:
            tmp_genres = form.genres.data
            if 'seeking_venue' in request.form:
                # artist.seeking_venue = True
                seeking = True
            else:
                # artist.seeking_venue = False
                seeking = False
            sql = text("""
                UPDATE public."Artist"
                SET name = :name, city = :city, state = :state,
                phone = :phone, genres = :genres,
                website = :website, facebook_link = :facebook_link,
                image_link = :image_link, seeking_venue = :seeking_venue,
                seeking_description = :seeking_description
                WHERE id = :artist_id
                """)

            db.engine.execute(
                sql,
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=','.join(tmp_genres),
                website=form.website.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_venue=seeking,
                seeking_description=form.seeking_description.data,
                artist_id=artist_id
            )
            db.session.commit()

            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                ' was successfully udated!')

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            # on error, flash error message
            flash('An error occurred. Artist ' +
                request.form['name'] + ' could not be updated.')


        finally:
            db.session.close()             

    else:
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    # DONE: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    form.genres.data = venue.genres.split(',')

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    # Using raw sql instead of SQLAlchemy ORM
    # venue = Venue.query.get(venue_id)
    sql = text("""select * from public."Venue" where id = :venue_id""") 
    venue = db.engine.execute(sql, venue_id=venue_id).fetchone()
    form = VenueForm()
    if form.validate():

        try:
            tmp_genres = form.genres.data
            if 'seeking_talent' in request.form:
                # venue.seeking_talent = True
                seeking = True
            else:
                seeking = False
                # venue.seeking_talent = False

            sql = text("""
                UPDATE public."Venue"
                SET name = :name, city = :city, state = :state,
                address = :address, phone = :phone, genres = :genres,
                website = :website, facebook_link = :facebook_link,
                image_link = :image_link, seeking_talent = :seeking_talent,
                seeking_description = :seeking_description
                WHERE id = :venue_id
                """)
            db.engine.execute(
                sql, name = form.name.data,
                city = form.city.data,
                state = form.state.data,
                address = form.address.data,
                phone = form.phone.data,
                genres = ','.join(tmp_genres),
                website = form.website.data,
                facebook_link = form.facebook_link.data,
                image_link = form.image_link.data,
                seeking_talent = seeking,
                seeking_description = form.seeking_description.data,
                venue_id=venue_id
            )


            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] +
                ' was successfully updated!')

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            # on error, flash error message
            flash('An error occurred. Venue ' +
                request.form['name']  + ' could not be updated.')
        finally:
            db.session.close()

    else:
        flash(form.errors)
        return render_template('forms/edit_venue.html', form=form, venue=venue)

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
    # TODO: modify data to be the data object returned from db insertion
    error = False
    form = ArtistForm()
    if form.validate():
        try:
            tmp_genres = form.genres.data
            sql = text(
                """
                INSERT INTO public."Artist"
                (name, city, state,
                phone, genres,
                website, facebook_link,
                image_link, seeking_venue,
                seeking_description)
                VALUES (:name, :city, :state,
                :phone, :genres,
                :website, :facebook_link,
                :image_link, :seeking_venue,
                :seeking_description
                )
                """
            )

            db.engine.execute(
                sql,
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=','.join(tmp_genres),
                website=form.website.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                    ' was successfully listed!', 'success')

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            # DONE TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            flash('An error occured. Artist ' +
                request.form['name'] + ' Could not be listed!', 'error')

            return render_template('forms/new_artist.html', form=form)

        finally:
            db.session.close()



    else:
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)

    # on successful db insert, flash success

    return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real artists data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # shows = Show.query.all()
    # Using raw sql instead of orm syntax as per project requirement
    sql = text("""
        Select public."Show".*, 
        public."Venue".name as venue_name, 
        public."Venue".image_link as venue_image_link, 
        public."Artist".name as artist_name, 
        public."Artist".image_link as artist_image_link
        from public."Show" join public."Venue"
        on public."Show".venue_id = public."Venue".id
        join public."Artist"
        on public."Show".artist_id = public."Artist".id
        order by start_time asc  
            """)
    shows = db.engine.execute(sql).fetchall()
    data = []
    for show in shows:
        show = {
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "venue_image_link": show.venue_image_link,
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        data.append(show)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE TODO: insert form data as a new Show record in the db, instead
    error = False
    form = ShowForm()
    try:
        sql = text(
                """
                INSERT INTO public."Show"
                (venue_id, artist_id, start_time)
                VALUES (:venue_id, :artist_id, :start_time)
                """            
        )
        
        db.engine.execute(
            sql, artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )       
        db.session.commit()
        # on successful db insert, flash success        
        flash('Show was successfully listed!', 'success')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        # DONE: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.', 'error')
        return render_template('forms/new_show.html', form=form)

    finally:
        db.session.close()

    # return redirect(url_for('shows'))
    return render_template('pages/home.html')

# Functions about date calculations inspired by 
# https://github.com/AlbuquerqueJC/fyyur/blob/master/app.py
# Slightly modified. This approach was preferred instead of
# static methods on the models.

def upcoming_shows(shows):
    upcoming = []
    for show in shows:
        if show.start_time > datetime.now():
            upcoming.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    return upcoming


def upcoming_shows_count(shows):
    return len(upcoming_shows(shows))


def past_shows(shows):
    past = []
    for show in shows:
        if show.start_time < datetime.now():
            past.append({

                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    return past


def past_shows_count(shows):
    return len(past_shows(shows))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
