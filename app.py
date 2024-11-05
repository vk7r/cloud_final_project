#!/usr/bin/python
from flask import Flask
import random


# Flask Application
app = Flask(__name__)

@app.route('/directhit')
def normal_endpoint():
    # Forward the request directly to the master
    pass

@app.route('/random')
def random_endpoint():
    # Randomly chose slave node
    pass


@app.route('/custom')
def custom_endpoint():
    # Forward the requests to the node with the least response time