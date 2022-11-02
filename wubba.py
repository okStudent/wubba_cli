#!/usr/bin/python3
import argparse
import json
import pandas as pd
import requests
from datetime import datetime
from api_funcs import wubba_get, wubba_filter, ls
from matrix import matrix
from PIL import Image
#Rick and Morty CLI

#list of sub commands
SUB_COMMANDS = {'get': wubba_get, 'filter': wubba_filter}

def print_jsons_as_table(results):
    """
    Prints list of jsons as table.

    :param results: list of the jsons to print
    """
    cleaned_results = []

    #list of the titles
    title = [item[0] for item in results[0].items()]

    #convert results to list
    for result in results:
        attributes = []

        #convert list item to count, dict item to name
        for item in result.items():
            if type(item[1]) == dict:
                attributes.append(item[1]["name"])
            elif type(item[1]) == list:
                attributes.append(len(item[1]))
            else:
                attributes.append(item[1])

        #add the item's values to the list of all items
        cleaned_results.append(attributes)

    #convert to table
    df = pd.DataFrame(cleaned_results, columns = title)

    #Display the table
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

def display_image(image_url):
    """
    Downloads and displays image from url

    :param image_url: the url of the image to download
    """
    #download the image data
    image_data = requests.get(image_url, stream=True).raw
    #open the image
    with Image.open(image_data) as im:
        im.show()

####################################################### Define Argument Parser ############################################################
#init the argument parser
wubba_parser = argparse.ArgumentParser(description="The *official* Rick and Morty cli! Search everything about Rick and Morty!", prog="wubba")
wubba_parser.add_argument("-t", "--table", action='store_true', help="Print results as table")

#add a subparser for each global command
wubba_subparser = wubba_parser.add_subparsers(dest='command')
wubba_subparser.required = True
#define subparser for each command
ls_p = wubba_subparser.add_parser('ls', description="Lists all of the characters/locations/episodes")
ls_p.set_defaults(func=ls)

get_p = wubba_subparser.add_parser('get', description="Get objects by id")
get_p.set_defaults(func=wubba_get)

filter_p = wubba_subparser.add_parser('filter', description="Filter objects")
filter_p.set_defaults(func=wubba_filter)

matrix_p = wubba_subparser.add_parser('matrix', description="Matrices query commands")
matrix_p.set_defaults(func=matrix)

#define ls arguments
ls_p.add_argument('-c', '--character', action='store_true', help='list all of the characters')
ls_p.add_argument('-l', '--location', action='store_true', help='list all of the locations')
ls_p.add_argument('-e', '--episode', action='store_true', help='list all of the episodes')

#define matrix arguments
matrix_p.add_argument('-l', '--limit', type=int, help='limit the number of the results')
type_arg = matrix_p.add_argument('type', choices=['character', 'location'], help="Get character appearance rarity, or get location residents amount")
type_arg.required = True

#define subparsers for get and filter commands
get_sub = get_p.add_subparsers(dest="object", description='Get Objects by id')
get_sub.required = True
filter_sub = filter_p.add_subparsers(dest="object", description="Filter objects")
filter_sub.required = True
## character get
character_get = get_sub.add_parser('character', description='Get character by id')
character_get.add_argument('-i', '--image', action='store_true', dest='image', help="Download the character's image")
id_arg = character_get.add_argument("id", type=int)
id_arg.required=False
## character filter
character_filter = filter_sub.add_parser('character', description="Filter a character")
character_filter.add_argument('--name', type=str, help="filter by name")
character_filter.add_argument('--status', type=str, choices=['Alive', 'Dead', 'unknown'], help="filter by status")
character_filter.add_argument('--species', type=str, help="filter by species")
character_filter.add_argument('--type', type=str, help="filter by type")
character_filter.add_argument('--gender', type=str, choices=['Female', 'Male', 'Genderless', 'unknown'], help="filter by gender")
character_filter.add_argument('--origin', type=str, help="filter by charater origin")
character_filter.add_argument('--location', type=str, help="filter by current location")
character_filter.add_argument('-i', '--image', action='store_true', dest='image', help="If there is one result, download the character's image")
## location get
location_get = get_sub.add_parser('location', description='Get location by id')
location_get.add_argument("id", type=int).required=False

## location filter
location_filter = filter_sub.add_parser('location', description="Filter a location by name, dimension or type")
location_filter.add_argument('--name', type=str, help="filter by name")
location_filter.add_argument('--dimension', type=str, help="filter by dimension")
location_filter.add_argument('--type', type=str, help="filter by type")

## episode get
episode_get = get_sub.add_parser('episode',description='Get episode by id')
episode_get.add_argument("id", type=int).required=False

## episode filter
episode_filter = filter_sub.add_parser('episode', description='Filter an episode by name or code')
episode_filter.add_argument('-n', '--name', type=str, help="filter by name")
episode_filter.add_argument('-c', '--code', dest='episode', type=str, help="filter by episode code")
episode_filter.add_argument('-b', '--before', type=str, help="filter episodes that aired before a specific date")
episode_filter.add_argument('-a', '--after', type=str, help="filter episodes that aired after a specific date")
episode_filter.add_argument('-s', '--season', type=int, help="filter by season")
episode_filter.add_argument('-e', '--episode', dest='episode_f', type=int, help="filter by episode number")
########################################################################################################################

args = wubba_parser.parse_args()
save_image = (args.command == "get" or args.command == "filter") and args.object == "character" and args.image
command = args.command
table = args.table

#execute argparse
results = args.func(args)

if command != "ls" and table:
    #Display as json
    print_jsons_as_table(results)
else:
    for result in results:
        print(json.dumps(result, indent=4))

#save image flag
if save_image:
    if len(results) > 1:
        print("Got multiple results, image download fail")
    else:
        print("Downloading image")
        display_image(results[0]["image"])
