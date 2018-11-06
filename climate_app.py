import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import logging

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)
session = scoped_session(sessionmaker(bind=engine))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.teardown_request
def remove_session(ex=None):
    session.remove()

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation"""
    # Query all precipitation
    precipitation_results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of precipitation
    all_precipitation = []
    for precipitation in precipitation_results:
        precipitation_dict = {}
        precipitation_dict["date"] = precipitation.date
        precipitation_dict["prcp"] = precipitation.prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    stations_results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations_results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of tobs"""
    # Query all tobs
    tobs_results = session.query(Measurement.date, Measurement.tobs).all()

    # Create a dictionary from the row data and append to a list of tobs
    all_tobs = []
    for tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = tobs.date
        tobs_dict["tobs"] = tobs.tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

def calc_temps(start_date, end_date):

    """
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    split_date = start_date.split('-')
    dt_start_date = dt.date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

    split_date = end_date.split('-')
    dt_end_date = dt.date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

    logging.warning("End: " + split_date[0] + "/" + split_date[1] + "/" + split_date[2])
    # Query all tobs start with start date
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= dt_start_date).filter(Measurement.date <= dt_end_date).all()
		
    return start_results[0]

@app.route("/api/v1.0/<start>")
def with_start(start):
    """Return a list of calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""

	# Create a dictionary from the row data and append to a list of tobs
    end = dt.datetime.now()
    tmin, tavg, tmax = calc_temps(start, str(end.year) + "-" + str(end.month) + "-" + str(end.day))

    all_starts = []
    start_dict = {}
    start_dict["tmin"] = tmin
    start_dict["tavg"] = tavg
    start_dict["tmax"] = tmax
    all_starts.append(start_dict)
	
    return jsonify(all_starts)
	
	
@app.route("/api/v1.0/<start>/<end>")
def with_start_end(start, end):
    """Return a list of calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""

	# Create a dictionary from the row data and append to a list of tobs
    tmin, tavg, tmax = calc_temps(start, end)

    all_starts = []
    start_dict = {}
    start_dict["tmin"] = tmin
    start_dict["tavg"] = tavg
    start_dict["tmax"] = tmax
    all_starts.append(start_dict)
	
    return jsonify(all_starts)
	


if __name__ == '__main__':
    app.run(debug=True)
