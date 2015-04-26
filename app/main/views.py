from flask import current_app, request, render_template, flash, url_for, session, redirect, jsonify
from flask_oauth import OAuth
from flask.ext.login import login_required, current_user
from forms import EditProfileForm
from . import main
from ..models import *
from discogs_client import *

# from selenium.webdriver.chrome.options import Options
from splinter import Browser
# from splinter.driver.zopetestbrowser import ZopeTestBrowser

import logging
import urllib2
import simplejson
import re

fela = Fela()


@main.route('/')
def index():
    
    login_block = u'\
    <form action="https://www.discogs.com/login?nologin=1&return=%2Fmy%3F" id="login_form" class="form_block" method="post">\
        <input type="text" value="" name="username" id="username" autocapitalize="off" autocorrect="off" class="field_large" tabindex="1" autofocus />\
        <input type="password" name="password" id="password" value="" class="field_large" size="20" tabindex="2" />\
        <button type="submit" name="Action.Login" class="button button_green button_large full_width" tabindex="3">Log In</button>'
    
    form_block = u'\
    <form action="" method="post" class="form_block" id="oauth_form_block"> \n\
        <fieldset class="button_space"> \n\
            <input type="hidden" name="oauth_token" value="XOlzFKjDiJEFVzyQvhBXOxGeLBZzwFzUGLKuNNZt" /> \n\
            <button type="submit" class="button button_green">Authorize</button> \n\
        </fieldset> \n\
    </form>'
    
    app = current_app._get_current_object()
    
    session['discogs_user_agent'] = app.config['DISCOGS_USER_AGENT']
    session['discogs_consumer_key'] = app.config['DISCOGS_CONSUMER_KEY']
    session['discogs_consumer_secret'] = app.config['DISCOGS_CONSUMER_SECRET']
    session['discogs_callback_url'] = app.config['DISCOGS_CALLBACK_URL']
    session['access_token'] = ''
    session['access_secret'] = ''
    
    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    resp = d.get_authorize_url(callback_url=session['discogs_callback_url'])
    
    session['request_token'] = resp[0]
    session['request_secret'] = resp[1]
    session['access_token_url'] = resp[2]
    
    d.set_token(session['request_token'], session['request_secret'])
    
    return render_template('request.html', \
                            user_agent=session['discogs_user_agent'], \
                            consumer_key=session['discogs_consumer_key'], \
                            consumer_secret=session['discogs_consumer_secret'], \
                            callback_url=session['discogs_callback_url'], \
                            request_token=session['request_token'], \
                            request_secret=session['request_secret'], \
                            access_token=session['access_token'], \
                            access_secret=session['access_secret'], \
                            access_token_url=session['access_token_url'], \
                            wantlist=fela.wantlist, \
                            userlist=fela.userlist, \
                            collection=fela.collection, \
                            name=fela.name)
    """
    return render_template('index.html', \
                            user_agent = session['discogs_user_agent'], \
                            consumer_key = session['discogs_consumer_key'], \
                            consumer_secret = session['discogs_consumer_secret'], \
                            callback_url = session['discogs_callback_url'], \
                            request_token = session['request_token'], \
                            request_secret = session['request_secret'])
    """
    
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
    
    return render_template('request.html', \
                            user_agent=session['discogs_user_agent'], \
                            consumer_key=session['discogs_consumer_key'], \
                            consumer_secret=session['discogs_consumer_secret'], \
                            callback_url=session['discogs_callback_url'], \
                            request_token=session['request_token'], \
                            request_secret=session['request_secret'], \
                            access_token=session['access_token'], \
                            access_secret=session['access_secret'], \
                            access_token_url=session['access_token_url'])

@main.route('/access')
def discogs_access():
    
    app = current_app._get_current_object()
    
    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    d.set_token(session['request_token'], session['request_secret'])
    
    chrome = Browser('chrome')
    # phantomjs = Browser('phantomjs')
    
    # with phantomjs as browser:
    with chrome as browser:
        # Visit URL
        url = 'https://www.discogs.com/login?return_to=%2F'
        # url = session['access_token_url']
        print '[1] browser.visit url: ' + url
        browser.visit(url)
        url = browser.url
        print '\n[2] browser.url: ' + url
        print '[2] browser.title: ' + browser.title
        print '[2] browser.fill username: ' + app.config['DISCOGS_USERNAME']
        print '[2] browser.fill password: ' + app.config['DISCOGS_PASSWORD']
        browser.fill('username', app.config['DISCOGS_USERNAME'])
        browser.fill('password', app.config['DISCOGS_PASSWORD'])
        login_button_name = 'Action.Login'
        login_button = browser.find_by_name(login_button_name)
        if login_button:
            print '[2] button.click: ' + login_button_name
            login_button.click()
            auth_url = session['access_token_url']
            browser.visit(auth_url)
            print '\n[3] browser.visit ' + auth_url
            print '[3] browser.title: ' + browser.title
            print '[3] browser.url: ' + browser.url
            print '\n[4] browser.title: ' + browser.title
            print '[4] browser.url: ' + browser.url
            auth_form_id = 'oauth_form_block'
            auth_form = browser.find_by_id(auth_form_id)
            if auth_form:
                print '[4] auth_form found'
                auth_input = browser.find_by_name('oauth_token')
                if auth_input:
                    print '[4] auth_input found'
                else:
                    print '[4] auth_input not found'
                buttons = browser.find_by_tag('button')
                if buttons:
                    print '[4] auth_button found'
                    auth_button = buttons[1]
                    print '[4] auth_button.click'
                    auth_button.click()
                    print '[4] browser.title: ' + browser.title
                    print '[4] browser.url: ' + browser.url
                    # print browser.html
                else: 
                    print '[4] no buttons found'
            else:
                print '[4] auth_form not found'
        else:
            print 'login_button not found'
    print '[5] quit browser'
    browser.quit()
    
    return render_template('access.html', \
                            user_agent=session['discogs_user_agent'], \
                            consumer_key=session['discogs_consumer_key'], \
                            consumer_secret=session['discogs_consumer_secret'], \
                            callback_url=session['discogs_callback_url'], \
                            request_token=session['request_token'], \
                            request_secret=session['request_secret'], \
                            access_token=session['access_token'], \
                            access_secret=session['access_secret'], \
                            access_token_url=session['access_token_url'])
    
@main.route('/web_auth')
def web_auth():
    pass

@main.route('/authorise')
def discogs_authorise():
    app = current_app._get_current_object()
    session['oauth_verifier'] = request.args['oauth_verifier']
    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    d.set_token(session['request_token'], session['request_secret'])
    resp = d.get_access_token(request.args['oauth_verifier'])
    session['access_token'] = resp[0]
    session['access_secret'] = resp[1]
    print '[6] response: ' + str(resp)
    
    me = d.identity()
    # session['identity'] = me
    s = "I'm %s (%s) from %s." % (me.name, me.username, me.location)
    u = d.user(me.username)
    wantlist = me.wantlist
    print '[6] wantlist: ' + str(wantlist)
    wantlist_len = str(len(wantlist))
    print '[6] wantlist length: ' + wantlist_len
    wantlist_items = []
    wantlist_ids = []
    wantlist_obj_list = []
    for i in wantlist:
        wantlist_ids.append(i.release.id)
        wantlist_obj = {}
        wantlist_obj['id'] = i.release.id
        wantlist_obj['title'] = i.release.title
        wantlist_obj['year'] = i.release.year
        wantlist_obj['status'] = i.release.status
        wantlist_obj['country'] = i.release.country
        wantlist_obj['data_quality'] = i.release.data_quality
        wantlist_obj['genres'] = i.release.genres
        wantlist_obj['labels'] = i.release.labels
        wantlist_obj['companies'] = "companies"  # i.release.companies
        wantlist_obj['artists'] = "artists"  # i.release.artists
        wantlist_obj['notes'] = "notes"  # i.release.notes
        wantlist_obj['formats'] = i.release.formats
        wantlist_obj['credits'] = "credits"  # i.release.credits
        wantlist_obj['tracklist'] = "tracklist"  # i.release.tracklist
        wantlist_obj_list.append(wantlist_obj)
    
    session['wantlist_ids'] = wantlist_ids
    
    # search for x number of users from 0..x
    
    
    fela.userlist = ['Diognes_The_Fox', 'scientistindubwise', 'lhrecords', 'theory-x']
    
    # for i in session['wantlist']:
    #    wantlist_items.append(i)
    """
    for i in wantlist_items:
        #print i.release.url
        #print i.release.tracklist
    """
    # session['wantlist_items'] = wantlist_items
    # session['wantlist'] = str(wantlist)
    # session['wantlist'] = 'wantlist'
    
    # print str(wantlist_items)
    
    return render_template('access.html', \
                            user_agent=session['discogs_user_agent'], \
                            consumer_key=session['discogs_consumer_key'], \
                            consumer_secret=session['discogs_consumer_secret'], \
                            callback_url=session['discogs_callback_url'], \
                            request_token=session['request_token'], \
                            request_secret=session['request_secret'], \
                            access_token=session['access_token'], \
                            access_secret=session['access_secret'], \
                            access_token_url=session['access_token_url'], \
                            # wantlist = session['wantlist'], \
                            user=u, \
                            wantlist_items=wantlist_items, \
                            wantlist_len=wantlist_len, \
                            wantlist_ids=session['wantlist_ids'], \
                            wantlist_obj_list=wantlist_obj_list, \
                            fela_wantlist=wantlist_len, \
                            fela_userlist=str(fela.userlist), \
                            fela_user_len=str(len(fela.userlist)), \
                            fela_collection=fela.collection, \
                            fela_name=u.username, \
                            fela_wantlist_ids = wantlist_ids, \
                            fela = fela, \
                            num_users=200000)

@main.route('/discogs/user/<username>')
def discogs_user(username):
    
    d = Client(session['discogs_user_agent'])
    d.set_consumer_key(session['discogs_consumer_key'], session['discogs_consumer_secret'])
    d.set_token(session['request_token'], session['request_secret'])
    
    u = d.user(username)
    inventory_len = str(len(u.inventory))
    # inventory = u.inventory
    inventory = []
    
    return render_template('collection.html', \
                            user=u, \
                            username=username, \
                            )
                            #inventory=inventory, \
                            #inventory_len=inventory_len)

# list all sellers with the release <release_id>
@main.route('/discogs/sellers/<release_id>')
def discogs_sellers(release_id):
    u = 'http://www.discogs.com/sell/release/'
    return 'discogs_sellers '+u+str(release_id)


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


