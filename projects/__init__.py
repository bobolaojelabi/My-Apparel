#initialize the app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__,instance_relative_config=True)
#initialize extension which will protect all my post route against csrf and you must pass the csrf_token when submitting to these routes
csrf = CSRFProtect(app)
#load the config
app.config.from_pyfile('config.py', silent=False)

db=SQLAlchemy(app)

#load the route
from projects import adminroutes,userroutes