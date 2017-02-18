from CONST import MIN_VOTES_SUM

node_suggestion_dict = {}
link_suggestion_dict = {}


def push_to_dict(dct, key, value):
    found = False
    for k in dct:
        if k == key:
            found = True
            dct[k].append(value)
            break
    if not found:
        dct[key] = []
        dct[key].append(value)


def push_suggestions(dct, suggestions):
    for s in suggestions:
        push_to_dict(dct, s['name'], s)


def get_max_suggestion(array):
    item_max = None
    value_max = 0
    got_max = False
    for item in array:
        if not got_max:
            value_max = len(item['votes_for']) - len(item['votes_against'])
            item_max = item
            got_max = True
        else:
            pom = len(item['votes_for']) - len(item['votes_against'])
            if pom > value_max:
                value_max = pom
                item_max = item
            # dodati slucaj kad su isti?
    return item_max


def get_max_suggestions_array(dct):
    array = []
    for key in dct:
        array.append(get_max_suggestion(dct[key]))
    return array


def get_instant_delete(array):
    delete_array = []
    for item in array:
        pom = len(item['votes_for']) - len(item['votes_against'])
        if pom < MIN_VOTES_SUM:
            delete_array.append(item)
    return delete_array
