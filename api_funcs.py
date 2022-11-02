import requests
import json
from datetime import datetime
#api functions

BASE_URL = 'https://rickandmortyapi.com/api'

URLS = {'character': BASE_URL + '/character', 'location': BASE_URL + '/location', 'episode': BASE_URL + '/episode'}


def get_all(object_type) -> list:
    """
    Get all of the results of a specific type.

    :param object_type: the type of object to get (location/character/episode)
    """
    #api request
    response = requests.get(URLS[object_type]).json()
    data = response['results']

    #combine all of the results from different pages
    while response['info']['next']:
        response = requests.get(response['info']['next']).json()
        data += response['results']

    return data


def ls(args):
    """
    Get all of the results for possibly multiple types.

    :param args: A dictionary of the cli flags.
    """
    responses = []

    #convert args to dictionary
    args = vars(args)

    #remove command and func arguments
    args.pop("command")
    args.pop("func")
    args.pop("table")

    #create list of the specified types
    selected_flags = [key for key in args.keys() if args[key]]

    #get all of the types if there are no flags
    if len(selected_flags) == 0:
        for sub_command in URLS.keys():
            responses += get_all(sub_command)

    #get the result for each specified types
    for flag in selected_flags:
        responses += get_all(flag)

    return responses

def wubba_get(args):
    """
    Get an object of a specific type by id

    :param args: A dictionary of the cli flags.
    """
    response = None

    #if id is not specified, get all objects
    if not args.id:
        response = get_all(args.object)
    else:
        response = [requests.get(URLS[args.object] + f"/{args.id}").json()]

    return response

def wubba_filter(args):
    """
    Get objects with specific attributes

    :param args: A dictionary of the cli flags.
    """
    #base url of the chosen type
    url = URLS[args.object] + '?'

    object_type = args.object

    #convert arguments to dictionary
    args = vars(args)

    #remove command and sub-command items
    args.pop("object")
    args.pop("command")
    args.pop("func")

    #loop through arguments and add it to the url
    for item in args.items():
        if item[1]:
            url += str(item[0]) + "=" + str(item[1]) + "&"

    #remove last '&'
    url = url[:-1]

    #send get request
    response = requests.get(url).json()

    #if there are multiple pages, combine the pages
    if 'results' in response.keys():
        data = response['results']
        while response['info']['next']:
            response = requests.get(response['info']['next']).json()
            data += response['results']
    elif 'error' in response.keys():
        raise Exception(response["error"])


    #apply extra filtering to the results
    if object_type == 'episode':
        data = extended_episode_filter(args, data)

    if object_type == 'character':
        data = extended_character_filter(args, data)

    return data

def filter_by_date(before_str, after_str, result):
    """
    Checks if json result air_date is after/before/between a specific date.

    :param before_str: filter all episodes that aired before this date
    :param after_str: filter all episodes that aired after this date
    :param result: the json result to filter
    """
    #if not requested to filter by air_date, keep the result
    if not before_str and not after_str:
        return True

    before_date = None
    after_date = None

    #convert dates to date objects
    if before_str:
        before_date = datetime.strptime(before_str, "%d/%m/%Y")

    if after_str:
        after_date = datetime.strptime(after_str, "%d/%m/%Y")

    #if before_date is after_date, throw exception
    if before_date and after_date:
        if before_date < after_date:
            raise Exception("Before date is after the After date")

    #convert current episode's air date to date object
    result_date = datetime.strptime(result["air_date"], "%B %d, %Y")

    #compare dates
    if before_date and after_date:
        return result_date > after_date and result_date < before_date
    elif after_date:
        return result_date > after_date
    else:
        return result_date < before_date

def filter_by_location(location, result):
    """
    Checks if json result is from specific location.

    :param location: the location to filter by
    :param result: the json result to filter
    """
    if location:
        return result["location"]["name"] == location
    return True

def filter_by_origin(origin, result):
    """
    Checks if json result is from specific origin.

    :param origin: the origin to filter by
    :param result: the json result to filter
    """
    if origin:
        return result["origin"]["name"] == origin
    return True

def filter_by_season(season, result):
    """
    Checks if json result is from specific season.

    :param season: the season to filter by
    :param result: the json result to filter
    """
    if season:
        result_season = result["episode"].split("E")[0][1:]
        return int(result_season) == season
    return True

def filter_by_episode(episode, result):
    """
    Checks if json result is from specific episode.

    :param episode: the episode to filter by
    :param result: the json result to filter
    """
    if episode:
        result_episode = result["episode"].split("E")[1]
        return int(result_episode) == episode
    return True

def extended_episode_filter(args, results):
    """
    Apply extended episode filters.

    :param args: A dictionary of the cli flags.
    :param results: A list of the json results.
    """
    filtered_results = []

    #loop through all results
    for result in results:
        append_result = False

        #apply each filter with &
        append_result = filter_by_date(args["before"], args["after"], result)
        append_result &= filter_by_season(args["season"], result)
        append_result &= filter_by_episode(args["episode_f"], result)

        #if the result has passed all filters, add it to the filtered_results
        if append_result:
            filtered_results.append(result)

    return filtered_results

def extended_character_filter(args, results):
    """
    Apply extended character filters.

    :param args: A dictionary of the cli flags.
    :param results: A list of the json results.
    """
    filtered_results = []

    #loop through all results
    for result in results:
        append_result = False
        append_result = filter_by_origin(args["origin"], result)
        append_result &= filter_by_location(args["location"], result)

        if append_result:
            filtered_results.append(result)

    return filtered_results
