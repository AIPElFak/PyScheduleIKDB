import datetime
from pymongo import MongoClient

from CONST import time_delta

client = MongoClient('localhost', 27017)
db = client['test']
# test je ime db
node_suggestions = db['nodesuggestions']
link_suggestions = db['linksuggestions']
users = db['users']


def get_node_suggestions():
    suggestions = node_suggestions.find()
    return suggestions


def get_link_suggestions():
    suggestions = link_suggestions.find()
    return suggestions


def delete_old_node_suggestions():
    date_limit = datetime.datetime.utcnow() - time_delta
    node_suggestions.delete_many({'date_created': {'$lt': date_limit}})


def delete_old_link_suggestions():
    date_limit = datetime.datetime.utcnow() - time_delta
    link_suggestions.delete_many({'date_created': {'$lt': date_limit}})


def delete_old_unverified_users():
    date_limit = datetime.datetime.utcnow() - time_delta
    users.delete_many({'verified': False, 'date_created': {'$lt': date_limit}})


def instant_delete_node_suggestions(delete_array):
    node_suggestions.delete_many({'_id': {'$in': delete_array}})


def instant_delete_link_suggestions(delete_array):
    link_suggestions.delete_many({'_id': {'$in': delete_array}})


def delete_old_data():
    delete_old_node_suggestions()
    delete_old_link_suggestions()
    # ne brise se iz redis-a, za sad ne mora ni ovde
    # delete_old_unverified_users()

