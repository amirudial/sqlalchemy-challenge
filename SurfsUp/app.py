# Import the dependencies.
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request
import os

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

base_dir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(base_dir, "Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{database_path}")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory) 


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;'>/api/v1.0/&lt;start&gt;</a><br/>"
        f"<a href='/api/v1.0/&lt;start&gt;/&lt;end&gt;'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session()
    a_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= a_year_ago).filter(Measurement.prcp.isnot(None)).\
        order_by(Measurement.date).all()

    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session()
    results = session.query(Station.station).all()
    stations = [station[0] for station in results]
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session()
    a_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= a_year_ago).\
        order_by(Measurement.date).all()

    tobs_data = [{"date": result.date, "tobs": result.tobs} for result in results]
    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session()
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    if results:
        tmin, tavg, tmax = results[0]
        temperature_data = {"TMIN": tmin, "TAVG": tavg, "TMAX": tmax}
        session.close()
        return jsonify(temperature_data)
    else:
        session.close()
        return jsonify({"error": "No data found for the given start date."})


@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    session = Session()
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    if results:
        tmin, tavg, tmax = results[0]
        temperature_data = {"TMIN": tmin, "TAVG": tavg, "TMAX": tmax}
        session.close()
        return jsonify(temperature_data)
    else:
        session.close()
        return jsonify({"error": "No data found for the given date range."})

if __name__ == "__main__":
    app.run(debug=True)