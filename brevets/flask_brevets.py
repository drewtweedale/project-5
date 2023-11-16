"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""
import os
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
from mongo_file import insert_brev, get_brev
import logging
from pymongo import MongoClient
import traceback

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    start_time = request.args.get('start_time')
    brevet_dist = request.args.get('brev_dist', type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    open_time = acp_times.open_time(km, brevet_dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet_dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/submit", methods=["POST"])
def insert():
    """
    /submit : inserts a controle distance (and the respective times) into the database.

    Accepts POST requests ONLY!

    JSON interface: gets JSON, responds with JSON
    """
    try:
        # Read the entire request body as a JSON
        # This will fail if the request body is NOT a JSON.
        input_json = request.json
        # if successful, input_json is automatically parsed into a python dictionary!
        
        # Because input_json is a dictionary, we can do this:
        brev_dist = input_json["brev_dist"] # Should be a string
        start_time = input_json["start_time"] # Should be a string
        items = input_json["items"] # Should be a list of dictionaries
        if len(items) == 0:
            return flask.jsonify(
                message ="No controle distances were entered.",
                status = 0
            )
        brev_id = insert_brev(brev_dist, start_time, items)

        return flask.jsonify(result={},
                        message="Inserted!", 
                        status=1, # This is defined by you. You just read this value in your javascript.
                        mongo_id=brev_id)
    except Exception:
        # The reason for the try and except is to ensure Flask responds with a JSON.
        # If Flask catches your error, it means you didn't catch it yourself,
        # And Flask, by default, returns the error in an HTML.
        # We want /insert to respond with a JSON no matter what!
        return flask.jsonify(result={},
                        message="Oh no! Server error!", 
                        status=0, 
                        mongo_id='None')

@app.route("/display")
def fetch():
    """
    /display : fetches the newest to-do list from the database.

    Accepts GET requests ONLY!

    JSON interface: gets JSON, responds with JSON
    """
    try:
        brev_dist, start_time, items = get_brev()
        return flask.jsonify(
                result={"brevet_dist_km": brev_dist, "begin_date": start_time, "items": items}, 
                status=1,
                message="Successfully fetched a brevet")
    except:
        return flask.jsonify(
                result={}, 
                status=0,
                message="Something went wrong, couldn't fetch the brevet!")

#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
