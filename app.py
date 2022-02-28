#import dependancies
import datetime as dt
import numpy as np
import pandas as pd
#import more dependencies for SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#finally import Flask and jsonify
from flask import Flask, jsonify

#create the engine to connect to the sqlite database 
engine = create_engine("sqlite:///hawaii.sqlite")
#reflect the database into our classes
Base = automap_base()
#call the prepare method on the base object passing in the engine object 
Base.prepare(engine, reflect=True)
#create a new instance of flask called app

#create a variable for each of the classes so that they may be referenced later
Measurement = Base.classes.measurement
Station = Base.classes.station

#create a session link from python to the database
session = Session(engine)

app = Flask(__name__)

@app.route('/')
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API! </br>
    Available Routes: </br>
    /api/v1.0/precipitation </br>
    /api/v1.0/stations </br>
    /api/v1.0/tobs </br>
    /api/v1.0/temp/start/end </br>
    ''')

#precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #calculate the date one year ago from the most recent date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #query to get the date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    #dic to store data with date as key and precipitation as value
    precip = {date: prcp for date, prcp in precipitation}
    
    #return neat jsonified version of the dictionary
    return jsonify(precip)

#stations route
@app.route("/api/v1.0/stations")
def stations():
    #preform a query on the database stored into results variable
    results = session.query(Station.station).all()
    #unraveling results into a one-dimensional array using np.ravel then convert ounraveld results into a list
    stations = list(np.ravel(results))

    #stations=stations to format list into JSON
    return jsonify(stations=stations)

#temp observations route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #query the primary station for all temp observation from previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    #unravel the results into a one-dimensional array and cover that array into a list 
    temps = list(np.ravel(results))

    #jsonify the list for return
    return jsonify(temps=temps)

#route to report on the min, avg and max temps
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    #list to store min, avg and func
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    #if not statement to query database using the list 
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        #unravel results into array and convert to a list
        temps = list(np.ravel(results))
        #jsonify temps as return
        return jsonify(temps)

    #query into results variable
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    #unravel results into array and convert to list
    temps = list(np.ravel(results))
    
    #jsonify the return value
    return jsonify(temps)