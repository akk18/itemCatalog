from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from functools import wraps
import random
import string
app = Flask(__name__)

from sqlalchemy import asc, desc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Genre, Movie, engine
import database_setup as db

import time

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog'

# Create anti-forgery state token
def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('show_login'))
        return function(*args, **kwargs)
    return decorated_function

# Home page with recently added movies
@app.route('/')
@app.route('/genre')
def main_page():
    """Main page. Show game genres and most recently added Titles."""
    genres = db.get_all_genre()
    movies = session.query(Movie).order_by(desc(Movie.id)).limit(10)

    return render_template(
        'latest_movies.html',
        genres=genres,
        movies=movies
        )

#Display all movies in a genre
@app.route('/genre/<int:genre_id>/')
def show_genre(genre_id):
    """Specific genre page.  Shows all titles."""
    genres = db.get_all_genre()
    genre = db.get_genre(genre_id)
    movies = session.query(Movie).filter_by(genre_id=genre.id).order_by(asc(Movie.name))
    return render_template(
        'genre.html',
        genres=genres,
        genre=genre,
        movies=movies
        )

# Display all movie in a specific genre
@app.route('/genre/<int:genre_id>/<int:movie_id>/')
def show_movie(genre_id, movie_id):
    #Specific movie page. Shows desc.
    genres = db.get_all_genre()
    genre = db.get_genre(genre_id)
    movie = db.get_movie(movie_id)
    return render_template(
        'movie.html',
        genres=genres,
        genre=genre,
        movie=movie
        )

# Create a route for adding new movie function here
@app.route(
    '/genre/new/',
    defaults={'genre_id': None},
    methods=['GET', 'POST']
    )
@app.route(
    '/genre/new/<int:genre_id>/',
    methods=['GET', 'POST']
    )
@login_required
def new_movie(genre_id):
    #Add new movie page.  Requires logged in status.

    genres = db.get_all_genre()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        genre = request.form['genre']
        field_vals = {}

        user_id = login_session['user_id']

        if name and description and genre != "None":
            print 'received inputs'
            flash('New movie added!')
            genre_id = db.get_genre_id(genre)
            new_movie = db.create_movies(
                name,
                description,
                genre_id,
                user_id
                )
            return redirect(url_for(
                'show_movie',
                genre_id=genre_id,
                movie_id=new_movie.id
                )
            )
        elif genre == "None":
            flash('Must enter a genre.')
        else:
            field_vals['default_genre'] = genre
            flash('Invalid input! Must enter values.')

        field_vals['input_name'] = name
        field_vals['input_description'] = description
        return render_template('new_movie.html', genres=genres, **field_vals)
    else:
        if genre_id:
            genres_name = db.get_genre(genre_id).name
            return render_template('new_movie.html', genres=genres, default_genre=genres_name)
        else:
            return render_template('new_movie.html', genres=genres)
			
# Create a route for editing movie function here

@app.route(
    '/genre/<int:genre_id>/<int:movie_id>/edit/',
    methods=['GET', 'POST']
    )
@login_required
def edit_movie(genre_id, movie_id):
    #Edit movie page. User must have created the movie to edit.

    genres = db.get_all_genre()
    genre = db.get_genre(genre_id)
    movie = db.get_movie(movie_id)
    user_id = login_session['user_id']

    if movie.user_id != user_id:
        return redirect(url_for('main_page'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        genre = request.form['genre']

        field_vals = {}

        if name and description:
            flash('Item edited!')
            db.edit_movie(movie, name, description, db.get_genre_id(genre))

            time.sleep(1)
            return redirect(url_for(
                'show_movie',
                genre_id=genre_id,
                movie_id=movie_id
                )
            )
        else:
            field_vals['default_genre'] = genre
            flash('Invalid input! Must enter values.')

        field_vals['input_name'] = name
        field_vals['input_description'] = description
        return render_template('new_movie.html', genres=genres, **field_vals)
    else:
        return render_template(
            'edit_movie.html',
            genre_id=genre_id,
            movie_id=movie_id,
            genres=genres,
            input_name=movie.name,
            input_description=movie.description,
            default_genre=genre.name
            )

# Create a route for delete movie function here
@app.route(
    '/genre/<int:genre_id>/<int:movie_id>/delete/',
    methods=['GET', 'POST']
    )
@login_required
def delete_movie(genre_id, movie_id):
    """Delete movie page.  User must have created movie to delete."""

    genre = db.get_genre(genre_id)
    movie = db.get_movie(movie_id)

    user_id = login_session['user_id']

    if movie.user_id != user_id:
        return redirect(url_for('main_page'))

    if request.method == 'POST':
        delete_confirmation = request.form['delete']

        if delete_confirmation == 'yes':
            db.delete_movie(movie)
            flash('Item entry deleted.')
        return redirect(url_for('show_genre', genre_id=genre.id))
    else:
        return render_template(
            'delete_movie.html',
            genre=genre,
            movie=movie
            )


# Login functions and handling
@app.route('/login')
def show_login():
    """Login page"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)




# Google plus login 
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Google Plus sign in."""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'appligenreion/json'
        return response

    code = request.data  # one-time code from server

    try:
        # Upgrades auth code into credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'appligenreion/json'
        return response

    access_token = credentials.access_token

    # Checking validity of access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}'.format(token=access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'appligenreion/json'

    gplus_id = credentials.id_token['sub']

    # Verifies access_token is for intended user
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('Token\'s user ID doesn\'t match given user ID.'), 401)
        response.heads['Content-Type'] = 'appligenreion/json'
        return response

    # Verifies access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('Token\'s client ID does not match app\'s.'), 401)
        print 'Token\'s client ID does not match app\'s.'
        response.headers['Content-Type'] = 'appligenreion/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected'), 200)
        response.headers['Content-Type'] = 'appligenreion/json'
        return response

    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {
        'access_token': credentials.access_token,
        'alt': 'json'
        }
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = db.get_user_id(login_session['email'])

    if user_id is None:
        user_id = db.create_user(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('You are now logged in as {name}'.format(name=login_session['username']))
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Google logout.  Pairs with universal disconnect function."""
    access_token = login_session.get('access_token')
    print 'In gdisconnect, access token is {token}'.format(token=access_token)
    print 'User name is: '
    print login_session.get('username')

    if access_token is None:
        print 'Access token is None'
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'appligenreion/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token={token}'.format(token=access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'appligenreion/json'
        return response


# Delete user session
@app.route('/disconnect')
def disconnect():
    
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        del login_session['user_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']

        flash('You have been successfully logged out.')
    else:
        flash('You were not logged in.')

    return redirect(url_for('main_page'))


# JSON APIs.
@app.route('/genre/JSON')
def genre_json():
    genre = session.query(Genre).all()
    return jsonify(Categories=[genre.serialize for genre in genre])


@app.route('/genre/<int:genre_id>/JSON')
def genre_movies_json(genre_id):
    movie_list = db.get_movies(genre_id)
    genre = db.get_genre(genre_id)
    return jsonify(Genre=genre.name, Items=[movie.serialize for movie in movie_list])


@app.route('/genre/<int:genre_id>/<int:movie_id>/JSON')
def movie_json(genre_id, movie_id):
    movie = db.get_movies(movie_id)
    return jsonify(Item=movie.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
