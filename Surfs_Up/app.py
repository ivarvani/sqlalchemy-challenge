"""
surfs up assignment
"""
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# # reflect an existing database into a new model
Base = automap_base()
# # reflect the tables
# Base.prepare(engine, reflect=True)
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurment = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to my Homepage<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/2016-08-22<br/>"
        f"/api/v1.0/temp/2013-08-22/2016-08-22"
    )


##################################################################


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # """Return precipitation data"""
    prcp_data = (
        session.query(Measurment.date, Measurment.prcp)
        .filter(Measurment.date > "2016-08-22")
        .order_by(Measurment.date)
        .all()
    )
    session.close()
    # adding  the list of tuples into normal list
    prcp_results = []
    for data in prcp_data:
        prcp_results.append(data)
    # forming  a dictionary with the list of tuples
    prcp = dict(prcp_results)
    return jsonify(prcp)


##########################################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # """Return station data from station table"""
    total_stations = session.query(Station.name).all()
    session.close()
    # Convert list of tuples into normal list
    stations_data = list(np.ravel(total_stations))
    return jsonify(stations_data)


###############################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # """Return temperature data for most active station"""
    tobs_data = (
        session.query(Measurment.date, Measurment.tobs)
        .filter(Measurment.station == "USC00519281")
        .filter(Measurment.date > "2016-08-22")
    )
    tobs_results = []
    for tob in tobs_data:
        tobs_results.append(tob)
    session.close()
    #converting our result to dictionary format date as key and temp as value
    temperature_data = dict(tobs_results)
    return jsonify(temperature_data)


#######################################################################
### Dynamic routes
@app.route("/api/v1.0/temp/<start>")
def stats(start):
# Create our session (link) from Python to the DB
    session = Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    sel = [
        func.min(Measurment.tobs),
        func.avg(Measurment.tobs),
        func.max(Measurment.tobs),
    ]
    results = session.query(*sel).filter(Measurment.date >= start).all()
    session.close()
    #storing our results in dictionary format
    temps_list = []
    for data in results:
        temps_dict = {}
        (min_temp, avg_temp, max_temp) = data
        temps_dict["min_temp"] = min_temp
        temps_dict["max_temp"] = max_temp
        temps_dict["avg_temp"] = avg_temp
        temps_list.append(temps_dict)
    return jsonify(temps_list)


#############################################################################
@app.route("/api/v1.0/temp/<start>/<end>")
def stat(start, end):
# Create our session (link) from Python to the DB
    session = Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(end, "%Y-%m-%d").date()
    sel = [
        func.min(Measurment.tobs),
        func.avg(Measurment.tobs),
        func.max(Measurment.tobs),
    ]
    results = (
        session.query(*sel)
        .filter(Measurment.date >= start)
        .filter(Measurment.date <= end)
        .all()
    )
    session.close()
    temp_list = []
    #storing our results in dictionary format
    for result in results:
        temp_dict = {}
        (temp_min, temp_avg, temp_max) = result
        temp_dict["min_temp"] = temp_min
        temp_dict["max_temp"] = temp_max
        temp_dict["avg_temp"] = temp_avg
        temp_list.append(temp_dict)
    return jsonify(temp_list)


if __name__ == "__main__":
    app.run(debug=True)
