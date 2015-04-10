from flask import current_app, request, render_template, flash, url_for, session, redirect
from flask_oauth import OAuth
from flask.ext.login import login_required, current_user
from forms import EditProfileForm
from . import main
from ..models import User
from ..discogs_client.client import Client
from ..discogs_client.models import Artist, Release, Master, Label, User, \
                                    Listing, Track, Price, Vide

#from selenium.webdriver.chrome.options import Options
from splinter import Browser
#from splinter.driver.zopetestbrowser import ZopeTestBrowser

import logging
import urllib2
import simplejson
import re


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

    discogs_client = Client(app.config['USER_AGENT'])
    discogs_client.set_consumer_key(app.config['DISCOGS_CONSUMER_KEY'], app.config['DISCOGS_CONSUMER_SECRET'])
    
    cbu = app.config['DISCOGS_CALLBACK_URL']
    print 'callback url: '+cbu
    auth_url = discogs_client.get_authorize_url(callback_url=cbu)
    
    auth_path = auth_url[2]
    session['request_token'] = auth_url[0]
    session['request_secret'] = auth_url[1]
    
    discogs_client.set_token(session['request_token'], session['request_secret'])
    
    print 'auth url: '+auth_url[2]
    
    chrome = Browser('chrome')
    #zope = Browser('zope.testbrowser', ignore_robots=True)
    #zope = ZopeTestBrowser()
    
    with chrome as browser:
        # Visit URL
        #url = 'https://www.discogs.com/login?return_to=%2F'
        url = auth_url[2]
        print '[1] browser.visit url: '+url
        browser.visit(url)
        url = browser.url
        print '\n[2] browser.url: '+url
        print '[2] browser.title: '+browser.title
        print '[2] browser.fill username: '+app.config['DISCOGS_USERNAME']
        print '[2] browser.fill password: '+app.config['DISCOGS_PASSWORD']
        browser.fill('username', app.config['DISCOGS_USERNAME'])
        browser.fill('password', app.config['DISCOGS_PASSWORD'])
        login_button_name = 'Action.Login'
        login_button = browser.find_by_name(login_button_name)
        if login_button:
            print '[2] button.click: '+login_button_name
            login_button.click()
            print '\n[3] browser.title: '+browser.title
            print '[3] browser.url: '+browser.url
            auth_url = browser.url
            print '[3] browser.visit '+auth_url
            browser.visit(auth_url)
            print '\n[4] browser.title: '+browser.title
            print '[4] browser.url: '+browser.url
            auth_form_id = 'oauth_form_block'
            auth_form = browser.find_by_id(auth_form_id)
            if auth_form:
                print '[4] auth_form found'
            else:
                print '[4] auth_form not found'
            
            auth_input = browser.find_by_name('oauth_token')
            buttons = browser.find_by_tag('button')
            if auth_input:
                print '[4] auth_input found'
            else:
                print '[4] auth_input not found'
            if buttons:
                print '[4] auth_button found'
                auth_button = buttons[1]
                #print '[4] auth_button.click'
                #auth_button.click()
                #print '[4] browser.title: '+browser.title
                #print '[4] browser.url: '+browser.url
            else: 
                print '[4] no buttons found'
            
        else:
            print 'login_button not found'
            
    """
    req = urllib2.Request(auth_url[2], None, {'user-agent': app.config['USER_AGENT']})
    opener = urllib2.build_opener()
    f = opener.open(req)
    html = str(f.read())
    s = 'vinylalert'
    print 'search for "vinylalert"'
    m = re.findall(s, html)
    if m:
        print 'FOUND RESULT!'
        print m
    s = r'<form'
    m = re.findall(s, html)
    if m:
        print 'FOUND RESULT!'
        print m
    s = r'</form'
    m = re.findall(s, html)
    if m:
        print 'FOUND RESULT!'
        print m
    print html
    """
    
    """
    req = {
        'user_agent': app.config['USER_AGENT'], 
        'consumer_key': app.config['DISCOGS_CONSUMER_KEY'], 
        'consumer_secret': app.config['DISCOGS_CONSUMER_SECRET'], 
        'token': auth_token, 
        'secret': auth_secret
    }
    print 'Request: '+str(req)
    discogs_client2 = Client(app.config['USER_AGENT'], 
                             app.config['DISCOGS_CONSUMER_KEY'], 
                             app.config['DISCOGS_CONSUMER_SECRET'], 
                             auth_token, 
                             auth_secret)
    """
    #discogs_client2.set_consumer_key(app.config['DISCOGS_CONSUMER_KEY'], app.config['DISCOGS_CONSUMER_SECRET'])
    
    return render_template('index.html', \
                            callback_url = app.config['DISCOGS_CALLBACK_URL'] or 'DISCOGS_CALLBACK_URL', \
                            consumer_key = app.config['DISCOGS_CONSUMER_KEY'] or 'DISCOGS_CONSUMER_KEY', \
                            consumer_secret = app.config['DISCOGS_CONSUMER_SECRET'] or 'DISCOGS_CONSUMER_SECRET', \
                            request_token = session['request_token'] or 'DISCOGS_REQUEST_TOKEN', \
                            request_secret = session['request_secret'] or 'DISCOGS_REQUEST_SECRET', \
                            access_token = app.config['DISCOGS_ACCESS_TOKEN'] or 'DISCOGS_ACCESS_TOKEN', \
                            access_secret = app.config['DISCOGS_ACCESS_SECRET'] or 'DISCOGS_ACCESS_SECRET', \
                            validation_code = app.config['DISCOGS_VALIDATION_CODE'] or 'DISCOGS_VALIDATION_CODE', \
                            request_token_url = app.config['DISCOGS_REQUEST_TOKEN_URL'] or 'DISCOGS_REQUEST_TOKEN_URL', \
                            authorize_url = app.config['DISCOGS_AUTHORIZE_URL'] or 'DISCOGS_AUTHORIZE_URL', \
                            access_token_url = auth_url[2] or 'DISCOGS_ACCESS_TOKEN_URL', \
                            identity_url = app.config['DISCOGS_IDENTITY_URL'] or 'DISCOGS_IDENTITY_URL', \
                            test_item_url = app.config['DISCOGS_TEST_ITEM'] or 'DISCOGS_TEST_ITEM', \
                            user_agent = app.config['USER_AGENT'] or 'USER_AGENT')

@main.route('/authorize')
def discogs_authorize():
    app = current_app._get_current_object()
    session['oauth_verifier'] = request.args['oauth_verifier']
    discogs_client = Client(app.config['USER_AGENT'])
    discogs_client.set_consumer_key(app.config['DISCOGS_CONSUMER_KEY'], app.config['DISCOGS_CONSUMER_SECRET'])
    discogs_client.set_token(session['request_token'], session['request_secret'])
    resp = discogs_client.get_access_token(request.args['oauth_verifier'])
    session['access_token'] = resp[0]
    session['access_secret'] = resp[1]
    print 'resp: '+str(resp)
    
    me = discogs_client.identity()
    #session['identity'] = me
    s = "I'm %s (%s) from %s." % (me.name, me.username, me.location)
    wantlist = me.wantlist
    print wantlist
    print 'WANTLIST: '+str(len(wantlist))

    return render_template('authorized.html', \
                            callback_url = app.config['DISCOGS_CALLBACK_URL'] or 'DISCOGS_CALLBACK_URL', \
                            consumer_key = app.config['DISCOGS_CONSUMER_KEY'] or 'DISCOGS_CONSUMER_KEY', \
                            consumer_secret = app.config['DISCOGS_CONSUMER_SECRET'] or 'DISCOGS_CONSUMER_SECRET', \
                            request_token = session['request_token'] or 'DISCOGS_REQUEST_TOKEN', \
                            request_secret = session['request_secret'] or 'DISCOGS_REQUEST_SECRET', \
                            access_token = session['access_token'] or 'DISCOGS_ACCESS_TOKEN', \
                            access_secret = session['access_secret'] or 'DISCOGS_ACCESS_SECRET', \
                            validation_code = session['oauth_verifier'] or 'DISCOGS_VALIDATION_CODE', \
                            request_token_url = app.config['DISCOGS_REQUEST_TOKEN_URL'] or 'DISCOGS_REQUEST_TOKEN_URL', \
                            authorize_url = app.config['DISCOGS_AUTHORIZE_URL'] or 'DISCOGS_AUTHORIZE_URL', \
                            access_token_url = app.config['DISCOGS_ACCESS_TOKEN_URL'] or 'DISCOGS_ACCESS_TOKEN_URL', \
                            identity_url = app.config['DISCOGS_IDENTITY_URL'] or 'DISCOGS_IDENTITY_URL', \
                            test_item_url = app.config['DISCOGS_TEST_ITEM'] or 'DISCOGS_TEST_ITEM', \
                            user_agent = app.config['USER_AGENT'] or 'USER_AGENT', \
                            oauth_verifier = session['oauth_verifier'] or 'OAUTH_VERIFIER', \
                            identity = s or 'IDENTITY', 
                            wantlist = str(len(wantlist)) or 'WANTLIST')

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


