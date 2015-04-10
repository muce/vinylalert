from flask import Blueprint

discogs = Blueprint('discogs', __name__)

from . import views