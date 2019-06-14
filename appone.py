#!/usr/bin/env python3
from flask import Flask, render_template, url_for, request,redirect, flash, jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Genre, Movie, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
import requests
import httplib2

app = Flask(__name__)

CLIENT_ID = json.loads(
   open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Movie Database" 

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    login_session['provider'] = 'google'

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = redirect(url_for('showGenre'))
        flash("You are now logged out.")
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/')
@app.route('/genre')
def showGenre():
    genre = session.query(Genre).all()
    return render_template('genre.html', genre=genre)

@app.route('/genre/<int:genre_id>/movie')
def showMovie(genre_id):
	genre_name = session.query(Genre).filter_by(id = genre_id).one()
	movie = session.query(Movie).filter_by(genre_id = genre_id).all()
	return render_template('movie.html', movie = movie, genre_name = genre_name, genre_id = genre_id)
	
@app.route('/genre/<int:movie_id>/description')	
def showDescription(movie_id):
	movie = session.query(Movie).filter_by(id = movie_id).one()
	type = session.query(Genre).filter_by(id = movie.genre_id).one()
	return render_template('desc.html', movie = movie, type = type)

@app.route('/movie/<int:genre_id>/new/', methods=['GET', 'POST'])
def newMovie(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newMovie = Movie(name=request.form['name'], rating = request.form['rating'], description = request.form['description'], genre_id = genre_id,user_id = login_session['user_id'])
        session.add(newMovie)
        session.commit()
        flash("new movie is created!!")
        return redirect(url_for('showMovie', genre_id = genre_id ))
    else:
        return render_template('newMovie.html')

@app.route('/movie/<int:movie_id>/edit/', methods=['GET', 'POST'])
def editMovie(movie_id):
    editedMovie = session.query(
        Movie).filter_by(id=movie_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedMovie.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            editedMovie.name = request.form['name']
        if request.form['rating']:
            editedMovie.rating = request.form['rating']
        if request.form['description']:
            editedMovie.description = request.form['description']
            flash("movie is edited!!")
            return redirect(url_for('showMovie', genre_id = editedMovie.genre_id))
    else:
        return render_template('editMovie.html', movie=editedMovie) 
							   
@app.route('/movie/<int:movie_id>/delete/', methods=['GET', 'POST'])
def deleteMovie(movie_id):
    movieToDelete = session.query(
        Movie).filter_by(id=movie_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if movieToDelete.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        session.delete(movieToDelete)
        session.commit()
        flash("movie is deleted!!")
        return redirect(url_for('showGenre'))
    else:
        return render_template('deleteMovie.html', movie=movieToDelete)
@app.route('/genre/JSON')
def genreJSON():
    items = session.query(Genre).all()
    return jsonify(Movies=[i.serialize for i in items])			   
							   
@app.route('/genre/<int:genre_id>/movie/JSON')
def movieJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(Movie).filter_by(
        genre_id=genre_id).all()
    return jsonify(Movies=[i.serialize for i in items])			   
							   							   
if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
#    app.debug = True
    app.run(host='0.0.0.0', port=5000)							   