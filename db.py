from app import app
from flask_sqlalchemy import SQLAlchemy
from os import getenv

# Conncet the database
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# Make it so commands get run auotmatically
app.app_context().push()
db.create_all()