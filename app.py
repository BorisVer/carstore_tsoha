from flask import Flask
from os import getenv

# Make sure the app get created corretly and runs
app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

# Initiate static folder with the .css files to run
app.config['STATIC_FOLDER'] = 'static'

import routes
    
