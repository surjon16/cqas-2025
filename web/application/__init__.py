from flask import Flask

app = Flask(__name__)

from application import api
# from application import views

# tentative
# from data import models