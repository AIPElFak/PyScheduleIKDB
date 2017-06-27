import mongo
import neo4j
import processor
import requests
from threading import Timer

from CONST import PROCESS_INTERVAL


def event_callback():
    print("Tick")
    processor.push_node_suggestions(mongo.get_node_suggestions())
    neo4j.process_node_suggestions(processor.get_max_suggestions_array(
        processor.node_suggestion_dict))
    mongo.instant_delete_node_suggestions(
        neo4j.get_node_suggestion_delete_array()
    )
    processor.push_link_suggestions(mongo.get_link_suggestions())
    neo4j.process_link_suggestions(processor.get_max_suggestions_array(
        processor.link_suggestion_dict))
    mongo.instant_delete_link_suggestions(
        neo4j.get_link_suggestion_delete_array()
    )
    mongo.delete_old_data()
    processor.clear_data()
    neo4j.clear_data()
    requests.get('http://127.0.0.1:3000/serverupdate')
    Timer(PROCESS_INTERVAL, event_callback).start()


# Timer(interval, event_callback).start()
event_callback()
print("Data processor up and running")
