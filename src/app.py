import mongo
import neo4j
import processor
from threading import Timer


def event_callback():
    print("test")
    processor.push_suggestions(processor.node_suggestion_dict,
                               mongo.get_node_suggestions())
    neo4j.process_node_suggestion(processor.get_max_suggestions_array(
        processor.node_suggestion_dict)[0])
    mongo.instant_delete_node_suggestions(
        neo4j.get_node_suggestion_delete_array()
    )
    Timer(interval, event_callback).start()


def event_callback2():
    print("test2")
    processor.push_suggestions(processor.link_suggestion_dict,
                               mongo.get_link_suggestions())

    neo4j.process_link_suggestion(processor.get_max_suggestions_array(
        processor.link_suggestion_dict)[0])
    mongo.instant_delete_link_suggestions(
        neo4j.get_link_suggestion_delete_array()
    )

interval = 10
# Timer(interval, event_callback).start()
print("Data processor up and running")


event_callback()
# event_callback2()

mongo.delete_old_data()