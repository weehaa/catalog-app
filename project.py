from flask import Flask, render_template, redirect, url_for, request, jsonify,\
                  flash
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps
import crud
import random
import string

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('catalog_app_client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


@app.route('/')
@app.route('/catalog')
def catalog():
    '''Main page handler'''
    categories = crud.category_all()
    # show last 9 items
    items = crud.items_latest()[:9]
    return render_template('catalog.html',
                           categories=categories, items=items)


@app.route('/catalog/<category_name>/<item_name>')
def categoryItem(category_name, item_name):
    '''View item details page handler'''
    item = crud.item_byCatAndName(category_name, item_name)
    return render_template('category_item.html',
                           category_name=category_name,
                           item=item)


@app.route('/catalog/<category_name>/items')
def categoryItems(category_name):
    '''Category items page handler'''
    categories = crud.category_all()
    cat_items = crud.items_bycat(category_name)
    return render_template('category_items.html',
                           categories=categories,
                           category_name=category_name,
                           items=cat_items)


@app.route('/catalog.json')
def catalogJSON():
    pass
    categories = crud.category_all()
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


@app.route('/catalog/newitem/', methods=['GET', 'POST'])
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


@app.route('/catalog/<category_name>/<item_name>/edit/',
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


@app.route('/catalog/<category_name>/<item_name>/delete/',
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


@app.route('/login')
def showLogin():
    '''Login page handler'''
    # define url to return the user after login
    return_url = request.args.get('return_url')
    if not return_url:
        return_url = unicode(request.referrer)
    if not return_url:
        return_url = '/'
    # create unique state token (anti-frogery)
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, return_url=return_url)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''Google account login method'''
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('catalog_app_client_secret.json',
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
    result = json.loads(h.request(url, 'GET')[1])
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

    # Verify that the access token is valid for this app.
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
    user_id = crud.user_byemail(data["email"]).id
    if not user_id:
        user_id = crud.user_add(login_session['username'],
                                login_session['email'],
                                login_session['picture']).id
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '''" style = "width: 300px; height: 300px; border-radius: 150px;
                 -webkit-border-radius: 150px;-moz-border-radius: 150px;">'''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
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
@app.route('/disconnect')
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

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
