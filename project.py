from flask import (Flask, render_template, redirect, url_for, request, jsonify,
                  flash, session as login_session, make_response)
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps
import httplib2
import json
import requests
import random
import string
import os
import sys

current_path = os.path.dirname(__file__)
sys.path.insert(0, current_path)

import crud

application = Flask(__name__)

CLIENT_ID = json.loads(
    open(current_path + '/catalog_app_client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

application.secret_key = 'P4EHYLF6LS03GPQLZOT8RP3545MO61Z7'
application.jinja_env.globals['categories'] = crud.category_all()

@application.route('/')
@application.route('/catalog')
def catalog():
    '''Main page handler'''
    # show last 9 items
    items = crud.items_latest()[:9]
    return render_template('catalog.html', items=items)


@application.route('/catalog/<category_name>/<item_name>')
def categoryItem(category_name, item_name):
    '''View item details page handler'''
    categories = crud.category_all()
    item = crud.item_byCatAndName(category_name, item_name)
    return render_template('category_item.html',
                           category_name=category_name,
                           item=item)


@application.route('/catalog/<category_name>/items')
def categoryItems(category_name):
    '''Category items page handler'''
    categories = crud.category_all()
    cat_items = crud.items_bycat(category_name)
    return render_template('category_items.html',
                           category_name=category_name,
                           items=cat_items)


@application.route('/catalog.json')
def catalogJSON():
    return jsonify(Category=[c.serialize for c in categories])


def logged_in(func):
    '''Check that user is logged in'''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin', return_url=request.path))
        else:
            return func(*args, **kwargs)
    return decorated_function


@application.route('/catalog/newitem/', methods=['GET', 'POST'])
@logged_in
def addItem():
    '''New item page handler'''
    if request.method == 'POST':
        # TODO item name constraint check should be here
        item = crud.item_add(request.form['item_name'],
                             request.form['category_select'],
                             str(login_session['user_id']),
                             request.form['item_description'])
        if item:
            flash("Item saved!")
            category_name = crud.category_byid(item.category_id).name
            return redirect(url_for('categoryItems',
                                    category_name=category_name,
                                    item_name=item.name))
        else:
            flash("Your data is not correct!")

    categories = crud.category_all()
    return render_template('edititem.html',
                           categories=categories)


@application.route('/catalog/<category_name>/<item_name>/edit/',
           methods=['GET', 'POST'])
@logged_in
def editItem(item_name, category_name):
    '''Edit item page handler'''
    itemToEdit = crud.item_byCatAndName(category_name, item_name)
    # check that user is the item creator
    if login_session['user_id'] != itemToEdit.user_id:
        flash('You are not authorized to edit this Item')
        return redirect(url_for('categoryItem', item_name=item_name,
                        category_name=category_name))
    if request.method == 'POST':
        item = crud.item_update(itemToEdit, request.form['item_name'],
                                request.form['item_description'],
                                request.form['category_select'])
        if item:
            flash("Item saved!")
            category_name = crud.category_byid(item.category_id).name
            return redirect(url_for('categoryItem',
                                    category_name=category_name,
                                    item_name=item.name))
        else:
            flash("Your data is not correct!")
    categories = crud.category_all()
    return render_template('edititem.html',
                           item_name=item_name,
                           item_description=itemToEdit.description,
                           categories=categories,
                           category_name=category_name)


@application.route('/catalog/<category_name>/<item_name>/delete/',
           methods=['GET', 'POST'])
@logged_in
def deleteItem(item_name, category_name):
    '''Delete item page handler'''
    itemToDelete = crud.item_byCatAndName(category_name, item_name)
    # check that user is the item creator
    if login_session['user_id'] != itemToDelete.user_id:
        flash('You are not authorized to delete this Item')
        return redirect(url_for('categoryItem', item_name=item_name,
                        category_name=category_name))
    if request.method == 'POST':
        crud.item_delete(itemToDelete)
        flash("item deleted!")
        return redirect(url_for('categoryItems',
                                category_name=category_name))
    else:
        return render_template('deleteitem.html',
                               item_name=item_name,
                               category_name=category_name)


@application.route('/login')
def showLogin():
    '''Login page handler'''
    # define url to return the user after login
    return_url = request.args.get('return_url')
    if return_url is None:
        return_url = request.referrer
    if return_url is None:
        return_url = '/'
    # create unique state token (anti-frogery)
    state = random_string()
    login_session['state'] = state
    return render_template('login.html', STATE=state, return_url=return_url)


@application.route('/fbconnect', methods=['POST'])
def fbconnect():
    print "login_session: " + login_session.get('state')
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open(current_path + '/fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open(current_path + '/fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    # strip expire tag from access token
    token = 'access_token=' + access_token

    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    # Added decode("utf8") To make this compatible for python 3 (udacity review)
    result = h.request(url, 'GET')[1].decode("utf8")
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)

    login_session['provider'] = 'facebook'

    # TODO  handle a case when user doesn't have an email (acceptable on FB)
    # may be store fake email id@facebook.com. but email can be added later :(
    login_session['email'] = data.get("email")
    login_session['username'] = data.get("name")
    login_session['facebook_id'] = data.get("id")

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode("utf8")
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user = crud.user_byemail(login_session["email"])
    if not user:
        user = crud.user_add(login_session['username'],
                                login_session['email'],
                                login_session['picture'])
    login_session['user_id'] = user.id

    output = ''
    output += '<h2 class="margin-bottom">Welcome, %s!</h2>' \
              % login_session['username']
    output += '<img class="user-pic" src="%s">' % login_session['picture']

    flash("You are now logged in as %s" % login_session['username'])
    return output


@application.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@application.route('/gconnect', methods=['POST'])
def gconnect():
    '''Google account login method'''
    # Validate state token
    if request.args.get('state') != login_session.get('state'):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(current_path + '/catalog_app_client_secret.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode("utf8"))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this application.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user is already
                                            connected.'''), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user = crud.user_byemail(login_session["email"])
    if not user:
        user = crud.user_add(login_session['username'],
                                login_session['email'],
                                login_session['picture'])
    login_session['user_id'] = user.id

    output = ''
    output += '<h2 class="margin-bottom">Welcome, %s!</h2>' \
              % login_session['username']
    output += '<img class="user-pic" src="%s">' % login_session['picture']

    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@application.route('/gdisconnect')
def gdisconnect():
    ''' Google user account disconnect method. Revokes gconnect token'''
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@application.route('/disconnect')
def disconnect():
    '''Logout user method'''
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for("catalog"))
    else:
        flash("You were not logged in")
        return redirect(url_for("catalog"))

def random_string(l=32):
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(l))

if __name__ == '__main__':
    application.debug = True
    application.run()
