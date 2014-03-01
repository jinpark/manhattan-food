#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#

from flask import * # do not use '*'; actually input the dependencies.
from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *

from flask.ext.googlemaps import GoogleMaps
import requests
import urllib
import json

import apikey

from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)
GoogleMaps(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''

MANHATTAN_ZIP_CODES = [10026, 10027, 10030, 10037, 10039,10001, 10011, 10018, 10019, 10020, 10036,10029, 10035, 10010, 10016, 10017, 10022, 10012, 10013, 10014, 10004, 10005, 10006, 10007, 10038, 10280, 10002, 10003, 10009, 10021, 10028, 10044, 10128, 10023, 10024, 10025, 10031, 10032, 10033, 10034, 10040]
#MANHATTAN_ZIP_CODES = [10026, 10027, 10030, 10037, 10039, 11361]
LOCU_API = apikey.locu

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form = form)

@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form = form)

@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)

# Helper Functions
@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        print request.form
        menu_item = request.form['menu_item']
        zip_code = request.form['zip_code']
        return json.dumps(search_restaraunts(zip_code, menu_item))

def search_restaraunts(zip_code, menu_item):
    encoded_menu_item = urllib.quote(menu_item)
    restaraunts = cache.get(menu_item)
    if not restaraunts:
        print 'cache miss'
        restaraunts = []
        payload = {'api_key': LOCU_API, 'region': 'NY', 'postal_code' : str(zip_code), 'name' : encoded_menu_item}
        r = requests.get("https://api.locu.com/v1_0/menu_item/search/", params=payload)
        for restaraunt in r.json()['objects']:
            restaraunts.append(restaraunt)
        cache.set(menu_item, restaraunts, timeout=60 * 60 * 24 * 7)

    # if restaraunts is None:
    #     restaraunts = {}
    #     for zip_code in MANHATTAN_ZIP_CODES:
    #         payload = {'api_key': LOCU_API, 'region': 'NY', 'postal_code' : str(zip_code), 'name' : encoded_menu_item}
    #         r = requests.get("https://api.locu.com/v1_0/menu_item/search/", params=payload)
    #         for restaraunt in r.json()['objects']:
    #             restaraunts.setdefault(zip_code, []).append(restaraunt)
    #     cache.set(menu_item, restaraunts)

    return restaraunts

# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
