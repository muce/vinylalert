from flask import current_app, render_template, flash
from flask.ext.login import login_required, current_user
from forms import EditProfileForm
from . import main
from ..models import User
from ..discogs_client.client import Client
from ..discogs_client.models import Artist, Release, Master, Label, User, \
                                    Listing, Track, Price, Video


@main.route('/')
def index():
    app = current_app._get_current_object()
    
    cbu = app.config['DISCOGS_CALLBACK_URL'] or 'DISCOGS_CALLBACK_URL'
    dck = app.config['DISCOGS_CONSUMER_KEY'] or 'DISCOGS_CONSUMER_KEY'
    dcs = app.config['DISCOGS_CONSUMER_SECRET'] or 'DISCOGS_CONSUMER_SECRET'
    drt = app.config['DISCOGS_REQUEST_TOKEN'] or 'DISCOGS_REQUEST_TOKEN'
    drs = app.config['DISCOGS_REQUEST_SECRET'] or 'DISCOGS_REQUEST_SECRET'
    dat = app.config['DISCOGS_ACCESS_TOKEN'] or 'DISCOGS_ACCESS_TOKEN'
    das = app.config['DISCOGS_ACCESS_SECRET'] or 'DISCOGS_ACCESS_SECRET'
    drtu = app.config['DISCOGS_REQUEST_TOKEN_URL'] or 'DISCOGS_REQUEST_TOKEN_URL'
    dau = app.config['DISCOGS_AUTHORIZE_URL'] or 'DISCOGS_AUTHORIZE_URL'
    datu = app.config['DISCOGS_ACCESS_TOKEN_URL'] or 'DISCOGS_ACCESS_TOKEN_URL'
    diu = app.config['DISCOGS_IDENTITY_URL'] or 'DISCOGS_IDENTITY_URL'
    dvc = app.config['DISCOGS_VALIDATION_CODE'] or 'DISCOGS_VALIDATION_CODE'
    dti = app.config['DISCOGS_TEST_ITEM'] or 'DISCOGS_TEST_ITEM'
    ua = app.config['USER_AGENT'] or 'USER_AGENT'
    
    print 'start cbu: '+cbu
    
    d = Client(ua)
    d.set_consumer_key(dck, dcs)
    resp = d.get_authorize_url(callback_url=cbu)
    #resp = d.get_authorize_url()
    drt = resp[0]
    drs = resp[1]
    dau = resp[2] # same as dau?oauth_token=drt
    
    print 'cbu: '+cbu
    
    #The client will hang on to the access token and secret, but in a web app, you'd want to persist those and pass them into a new `Client` instance on the next request.
    #Next, visit the authorize URL, authenticate as a Discogs user, and get the verifier:
    
    return render_template('index.html', \
                           ua = ua, d = d, \
                           dck = dck, dcs = dcs, drtu = drtu, dau = dau, datu = datu, diu = diu, \
                           dvc = dvc, drt = drt, drs = drs, dti = dti, dat = dat, das = das)

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


