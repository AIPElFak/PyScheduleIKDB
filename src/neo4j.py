from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.client import NotFoundError

from CONST import MAX_VOTES_SUM

db = GraphDatabase("http://localhost:7474", username="neo4j", password="test")

# izbegava try-except blokove
node_array = db.nodes.all()

node_suggestion_delete_array = []
link_suggestion_delete_array = []


def get_node_suggestion_delete_array():
    return node_suggestion_delete_array


def get_link_suggestion_delete_array():
    return link_suggestion_delete_array


# ovo je generalno losa ideja pa sam izdvojio u funkciju
def refresh_node_array():
    global node_array
    node_array = db.nodes.all()


def get_node(node_id):
    for node in node_array:
        if node.id == node_id:
            return node
    return None


def get_node_by_name(node_name):
    for node in node_array:
        if node['name'] == node_name:
            return node
    return None


def process_node_suggestion(suggestion):
    suggestion_type = suggestion['suggestion_type']
    votes_sum = len(suggestion['votes_for']) - len(suggestion['votes_against'])
    if votes_sum > MAX_VOTES_SUM:
        if suggestion_type == "CREATE":
            pom = get_node_by_name(suggestion['name'])
            if pom is None:
                new_node = db.nodes.create(name=suggestion['name'],
                                           definition=suggestion['definition'],
                                           description=suggestion['description'],
                                           votes=votes_sum)
                for label in suggestion['types']:
                    new_node.labels.add(label)
                refresh_node_array()
                # nema potrebe za testiranjem da li je uspesno, puci ce ako nije
                node_suggestion_delete_array.append(suggestion['_id'])
            else:
                node_suggestion_delete_array.append(suggestion['_id'])
        elif suggestion_type == "EDIT":
            pom = get_node_by_name(suggestion['name'])
            if pom is not None:
                if votes_sum > pom['votes']:
                    pom['name'] = suggestion['name']
                    pom['definition'] = suggestion['definition']
                    pom['description'] = suggestion['description']
                    if suggestion['types'] is not None:
                        pom.labels = suggestion['types']
                    pom['votes'] = votes_sum

                    refresh_node_array()
                    node_suggestion_delete_array.append(suggestion['_id'])
            else:
                node_suggestion_delete_array.append(suggestion['_id'])
        elif suggestion_type == "DELETE":
            pom = get_node_by_name(suggestion['name'])
            if pom is not None:
                if votes_sum > pom['votes']:
                    pom.delete()
                    refresh_node_array()
                    node_suggestion_delete_array.append(suggestion['_id'])
            else:
                node_suggestion_delete_array.append(suggestion['_id'])
        else:
            node_suggestion_delete_array.append(suggestion['_id'])


def process_node_suggestions(suggestion_array):
    for suggestion in suggestion_array:
        process_node_suggestion(suggestion)


def process_link_suggestion(suggestion):
    suggestion_type = suggestion['suggestion_type']
    votes_sum = len(suggestion['votes_for']) - len(suggestion['votes_against'])
    if votes_sum > MAX_VOTES_SUM:
        if suggestion_type == "CREATE":
            n1 = get_node_by_name(suggestion['node_from_name'])
            n2 = get_node_by_name(suggestion['node_to_name'])
            if n1 is not None and n2 is not None:
                rel = n1.relationships.create(suggestion['type'], n2)
                rel['votes_for'] = suggestion['votes_for']
                rel['votes_against'] = suggestion['votes_against']
                if suggestion['description'] is not None:
                    rel['description'] = suggestion['description']
            else:
                link_suggestion_delete_array.append(suggestion['_id'])
        elif suggestion_type == "EDIT":
            pass
        elif suggestion_type == "DELETE":
            pass
        else:
            link_suggestion_delete_array.append(suggestion['_id'])


def process_link_suggestions(suggestion_array):
    for suggestion in suggestion_array:
        process_link_suggestion(suggestion)
