from api_funcs import get_all

def character_episode_rarity(limit) -> list:
    """Sort character's episode amount

    :param limit: limit the number of results
    """
    #get all characters
    characters = get_all("character")

    #create list of {character_name, rarity}
    rarity = [{'name': characters[i]['name'], 'episode_amount': 0, 'origin': characters[i]['origin']['name']} for i in range(len(characters))]

    #foreach character, count the episode amount
    for character_index in range(len(characters)):
        rarity[character_index]['name'] = characters[character_index]['name']
        rarity[character_index]['episode_amount'] = len(characters[character_index]["episode"])

    #Sort the list
    if limit and limit <= len(rarity):
        return sorted(rarity, key=lambda item: item['episode_amount'], reverse=True)[:limit]
    else:
        return sorted(rarity, key=lambda item: item['episode_amount'], reverse=True)

def location_character_rarity(limit):
    """Sort location residents amount

    :param limit: limit the number of results
    """

    #Get all of the locations
    locations = get_all("location")

    #create a list of {location_name, amount}
    rarity = [{'name': locations[i]['name'], 'residents_amount': 0} for i in range(len(locations))]

    #foreach location, count residents amount
    for location_index in range(len(locations)):
        rarity[location_index]['name'] = locations[location_index]['name']
        rarity[location_index]['residents_amount'] = len(locations[location_index]["residents"])

    #Sort the list
    if limit:
        return sorted(rarity, key=lambda item: item['residents_amount'], reverse=True)[:limit]
    else:
        return sorted(rarity, key=lambda item: item['residents_amount'], reverse=True)



MATRICES={"character":character_episode_rarity, "location":location_character_rarity}


def matrix(args):
    return MATRICES[args.type](args.limit)
