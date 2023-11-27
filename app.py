#Import the dependencies
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
#Database Setup
#################################################
#Create engine to hawaii.sqlite
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

#Reflect an existing database into a new model
Base = automap_base()
#Reflect the tables
Base.prepare(autoload_with=engine)


#Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
#Flask Setup
#################################################
app = Flask(__name__)

#################################################
#Flask Routes
#################################################

@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(func.max(measurement.date)).first()[0]
    preYear = dt.datetime.strptime(recent_date,'%Y-%m-%d').date() - dt.timedelta(365)
    precip_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= preYear).all()    

    for results in precip_query:
        dict = results._asdict()

    return jsonify(dict)

@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(station.station).all()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_query = session.query(measurement.tobs).filter((measurement.date >= preYear) & 
                                       (measurement.station == 'USC00519281')).all()

    return jsonify(tobs_query)

@app.route("/api/v1.0/<start>")
def pass_start(start):
    date_query = session.query(measurement.date).all()

    canonicalized = dt.strptime(start, '%Y-%m-%d').date()
    
    for date_object in date_query:
        strdate = str(date_object)
        search_term = dt.strptime(strdate, '%Y-%m-%d').date()

        if search_term == canonicalized:
            
            tmin = session.query(func.min(measurement.tobs)).filter(measurement.date >= date_object).all()
            tavg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= date_object).all()
            tmax = session.query(func.max(measurement.tobs)).filter(measurement.date >= date_object).all()
                                 
            return jsonify(tmin, tavg, tmax)
    
    return jsonify({"error": f"Date {start} not found"}), 404

@app.route("/api/v1.0/<start>/<end>")
def pass_range(start, end):
    date_query = session.query(measurement.date).all()

    start_canonicalized = dt.strptime(start, '%Y-%m-%d').date()
    end_canonicalized = dt.strptime(end, '%Y-%m-%d').date()

    start_store = ()
    end_store = ()
    
    for startdate_object in date_query:
        start_strdate = str(startdate_object)
        start_searchterm = dt.strptime(start_strdate, '%Y-%m-%d').date()
    
        if start_searchterm == start_canonicalized:
            start_store.append(startdate_object)
             
    for enddate_object in date_query:
        end_strdate = str(enddate_object)
        end_searchterm = dt.strptime(end_strdate, '%Y-%m-%d').date()

        if end_searchterm == end_canonicalized:
            end_store.append(enddate_object)

            tminr = session.query(func.min(measurement.tobs)).filter(measurement.date >= start_store & measurement.date <= end_store).all()
            tavgr = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start_store & measurement.date <= end_store).all()
            tmaxr = session.query(func.max(measurement.tobs)).filter(measurement.date >= start_store & measurement.date <= end_store).all()

            return jsonify(tminr, tavgr, tmaxr)
    
    return jsonify({"error": f"Date {start, end} not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)