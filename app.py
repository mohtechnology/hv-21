import cv2
import time
import threading
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///traffic.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Vehiclelog(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    lane =db.Column(db.Integer, nullable=False)
    vehicles = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.Datetime, nullable=False)

    __table_args__ = (UniqueConstraint("lane", "timestamp", name="unique_lane_timestamp"),)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)