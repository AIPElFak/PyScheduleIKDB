from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.client import NotFoundError

from CONST import MAX_VOTES_SUM

db = GraphDatabase("http://localhost:7474", username="neo4j", password="test")

# izbegava try-except blokove
node_array = db.nodes.all()
link_array = db.relationships.all()

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


def refresh_link_array():
    global link_array
    link_array = db.relationships.all()


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


def get_link(link_id):
    for link in link_array:
        if str(link.id) == link_id:
            return link
    return None


def get_link_by_nodes_and_type(node_from, node_to, type):
    for link in link_array:
        if link.start.id == node_from and link.end.id == node_to and link.type == type:
            return link
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
            n1 = get_node_by_name(suggestion['start_name'])
            n2 = get_node_by_name(suggestion['end_name'])
            if n1 is not None and n2 is not None:
                pom = get_link_by_nodes_and_type(n1.id, n2.id, suggestion['type'])
                if pom is None:
                    rel = n1.relationships.create(suggestion['type'], n2,
                                                  votes_for=['placeholder1'],
                                                  votes_against=['placeholder2'])
                    rel['votes_for'] = suggestion['votes_for']
                    rel['votes_against'] = suggestion['votes_against']
                    rel['start_name'] = n1['name']
                    rel['end_name'] = n2['name']
                    if suggestion['description'] is not None:
                        rel['description'] = suggestion['description']
                    refresh_link_array()
                    link_suggestion_delete_array.append(suggestion['_id'])
                else:
                    link_suggestion_delete_array.append(suggestion['_id'])
            else:
                link_suggestion_delete_array.append(suggestion['_id'])
        elif suggestion_type == "EDIT":
            pom = get_link(suggestion['link_id'])
            if pom is not None:
                pom_votes = len(pom['votes_for']) - len(pom['votes_against'])
                if votes_sum > pom_votes:
                    if suggestion['description'] is not None:
                        pom['description'] = suggestion['description']
                    pom['start_name'] = suggestion['start_name']
                    pom['end_name'] = suggestion['end_name']
                    pom['votes_for'] = suggestion['votes_for']
                    pom['votes_against'] = suggestion['votes_against']
                    refresh_link_array()
                    link_suggestion_delete_array.append(suggestion['_id'])
            else:
                link_suggestion_delete_array.append(suggestion['_id'])
        elif suggestion_type == "DELETE":
            pom = get_link(suggestion['link_id'])
            if pom is not None:
                pom_votes = len(pom['votes_for']) - len(pom['votes_against'])
                if votes_sum > pom_votes:
                    pom.delete()
                    refresh_link_array()
                    link_suggestion_delete_array.append(suggestion['_id'])
            else:
                link_suggestion_delete_array.append(suggestion['_id'])
        else:
            link_suggestion_delete_array.append(suggestion['_id'])


def process_link_suggestions(suggestion_array):
    for suggestion in suggestion_array:
        process_link_suggestion(suggestion)
