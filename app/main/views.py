from flask import request, render_template, flash, url_for, session, redirect

from flask.ext.login import login_required, current_user
from forms import EditProfileForm
from . import main
from models import MatchMaker
from ..models import *
from config import *
from discogs_client import *
from splinter import Browser

matchmaker = MatchMaker()
d = 'd'
resp = 'resp'
me = 'me'
u = 'u'


@main.route('/')
def index():
    app = current_app._get_current_object()

    session['discogs_user_agent'] = app.config['DISCOGS_USER_AGENT']
    session['discogs_consumer_key'] = app.config['DISCOGS_CONSUMER_KEY']
    session['discogs_consumer_secret'] = app.config['DISCOGS_CONSUMER_SECRET']
    session['discogs_callback_url'] = app.config['DISCOGS_CALLBACK_URL']
    session['access_token'] = ''
    session['access_secret'] = ''

    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    while True:
        try:
            resp = d.get_authorize_url(callback_url=session['discogs_callback_url'])
            break
        except ssl.SSLError:
            print 'SSLError'
            resp = d.get_authorize_url(callback_url=session['discogs_callback_url'])

    session['request_token'] = resp[0]
    session['request_secret'] = resp[1]
    session['access_token_url'] = resp[2]

    d.set_token(session['request_token'], session['request_secret'])

    return render_template('request.html', \
                           user_agent=session['discogs_user_agent'],
                           consumer_key=session['discogs_consumer_key'],
                           consumer_secret=session['discogs_consumer_secret'],
                           request_token=session['request_token'],
                           request_secret=session['request_secret'],
                           access_token_url=session['access_token_url'])

@main.route('/request')
def discogs_request():
    app = current_app._get_current_object()

    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    resp = d.get_authorize_url(callback_url=session['discogs_callback_url'])

    session['request_token'] = resp[0]
    session['request_secret'] = resp[1]
    session['access_token_url'] = resp[2]

    d.set_token(session['request_token'], session['request_secret'])

    return render_template('request.html',
                           user_agent=session['discogs_user_agent'],
                           consumer_key=session['discogs_consumer_key'],
                           consumer_secret=session['discogs_consumer_secret'],
                           callback_url=session['discogs_callback_url'],
                           request_token=session['request_token'],
                           request_secret=session['request_secret'],
                           access_token_url=session['access_token_url'])

@main.route('/authorised')
def discogs_auth():
    app = current_app._get_current_object()
    session['oauth_token'] = request.args['oauth_token']
    session['oauth_verifier'] = request.args['oauth_verifier']
    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    d.set_token(session['request_token'], session['request_secret'])
    resp = d.get_access_token(request.args['oauth_verifier'])
    session['access_token'] = resp[0]
    session['access_secret'] = resp[1]

    me = d.identity()
    u = d.user(me.username)
    wantlist_items = matchmaker.get_wantlist_items(me)
    print 'AUTHORISED_URL'
    print 'OAUTH_TOKEN: '+session['oauth_token']
    print 'OAUTH_VERIFIER: '+session['oauth_verifier']
    print 'CONSUMER_KEY: '+session['discogs_consumer_key']
    print 'CONSUMER_SECRET: '+session['discogs_consumer_secret']
    print 'ACCESS_TOKEN: '+session['access_token']
    print 'ACCESS_SECRET: '+session['access_secret']

    return render_template('main_menu.html',
                           user_agent=session['discogs_user_agent'],
                           user = u,
                           collectionlist_url = '/',
                           wantlist_url = app.config['DISCOGS_WANTLIST_URL']+'?oauth_token='+session['oauth_token']+'&oauth_verifier='+session['oauth_verifier'],
                           wantlist_items = wantlist_items,
                           wantlist_items_len = str(len(wantlist_items)))

@main.route('/wantlist')
def discogs_wantlist():
    app = current_app._get_current_object()
    #session['oauth_verifier'] = request.args['oauth_verifier']
    #d = Client(session['discogs_user_agent'])
    #d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    #d.set_token(session['request_token'], session['request_secret'])
    #resp = d.get_access_token(request.args['oauth_verifier'])
    #session['access_token'] = resp[0]
    #session['access_secret'] = resp[1]

    #me = d.identity()
    #u = d.user(me.username)
    wantlist_items = 'wantlist_items' #matchmaker.get_wantlist_items(me)
    print 'WANTLIST_URL'
    print 'OAUTH_TOKEN: '+session['oauth_token']
    print 'OAUTH_VERIFIER: '+session['oauth_verifier']
    print 'CONSUMER_KEY: '+session['discogs_consumer_key']
    print 'CONSUMER_SECRET: '+session['discogs_consumer_secret']
    print 'ACCESS_TOKEN: '+session['access_token']
    print 'ACCESS_SECRET: '+session['access_secret']

    return render_template('wantlist.html',
                           user_agent=session['discogs_user_agent'],
                           user = u,
                           wantlist_items = wantlist_items,
                           wantlist_items_len = 'len')

@main.route('/collection')
def discogs_collection():
    return render_template('index.html')

"""
    me = d.identity()
    u = d.user(me.username)
    wantlist = me.wantlist

    # search for x number of users from 0..n
    me.userlist = ['Diognes_The_Fox', 'scientistindubwise', 'lhrecords', 'theory-x']

    return render_template('access.html',
                           user_agent=session['discogs_user_agent'],
                           user=u,
                           #consumer_key=session['discogs_consumer_key'],
                           #consumer_secret=session['discogs_consumer_secret'],
                           #callback_url=session['discogs_callback_url'],
                           #request_token=session['request_token'],
                           #request_secret=session['request_secret'],
                           #access_token=session['access_token'],
                           #access_secret=session['access_secret'],
                           #access_token_url=session['access_token_url'],
                           #matchmaker_wantlist_items=matchmaker_wantlist_items,
                           wantlist=wantlist,
                           wantlist_len=str(len(wantlist)),
                           num_users=200000)
"""
@main.route('/discogs/user/<username>')
def discogs_user(username):
    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    d.set_token(session['request_token'], session['request_secret'])

    u = d.user(username)
    inventory_len = str(len(u.inventory))
    # inventory = u.inventory
    inventory = []

    return render_template('collection.html',
                           user=u,
                           username=username,
                           )
    # inventory=inventory, \
    # inventory_len=inventory_len)


# list all sellers with the release <release_id>
@main.route('/discogs/sellers/<release_id>')
def discogs_sellers(release_id):
    u = 'http://www.discogs.com/sell/release/'
    return 'discogs_sellers ' + u + str(release_id)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)
