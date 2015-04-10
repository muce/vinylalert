from flask import current_app, render_template, flash, url_for, session, redirect
from flask_oauth import OAuth

@discogs.route('/')
def index():
    #app = current_app._get_current_object()
    return render_template(url_for('main.index'))