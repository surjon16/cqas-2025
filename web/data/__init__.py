from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_httpauth import HTTPBasicAuth
from application import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/db_hifi' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# app.config['SQLALCHEMY_POOL_SIZE'] = 20
# app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
# app.config['SQLALCHEMY_POOL_TIMEOUT'] = 5
# app.config['SQLALCHEMY_POOL_RECYCLE'] = 10

# db = SQLAlchemy(app, session_options={'autocommit': True})
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# WEB VIEWS WITH LOGIN REQUIRED
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

# API BASIC AUTH
auth = HTTPBasicAuth()

csrf = CSRFProtect()
csrf.init_app(app)