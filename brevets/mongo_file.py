import os
import logging

from pymongo import MongoClient

# Set up MongoDB connection

# Set up MongoDB connection
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)

# Use database "todo"
db = client.brevetsdb

# Use collection "lists" in the databse
collection = db.lists

##################################################
################ MongoDB Functions ############### 
##################################################


def get_brev(collection):
    """
    Obtains the newest document in the "lists" collection in database "brevetsdb".

    Returns  (string) and items (list of dictionaries) as a tuple.
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This will translate into finding the newest inserted document.

    lists = collection.find().sort("_id", -1).limit(1)

    # lists is a PyMongo cursor, which acts like a pointer.
    # We need to iterate through it, even if we know it has only one entry:
    for brev in lists:
        # We store all of our lists as documents with two fields:
        ## title: string # title of our to-do list
        ## items: list   # list of items:

        ### every item has two fields:
        #### desc: string   # description
        #### priority: int  # priority
        return brev["brev_dist"], brev["start_time"], brev["items"]


def insert_brev(collection, brev_dist, start_time, items):
    """
    Inserts a new brev into the database "brevetsdb", under the collection "lists".
    
    Inputs a brev_dist, start time and the required controle distances, 
    and open and close times (list of dictionaries)

    Returns the unique ID assigned to the document by mongo (primary key.)
    """
    output = collection.insert_one({
        "brev_dist": brev_dist,
        "start_time": start_time,
        "items": items})
    _id = output.inserted_id # this is how you obtain the primary key (_id) mongo assigns to your inserted document.
    return str(_id)


