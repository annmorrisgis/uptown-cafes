"""
This script calls the Yelp Fusion API to identify coffee shops
in Upper Manhattan, the parameters of which are defined by Latitude
and Longitude coordinates, in addition to select zip codes.

Note that Yelp limits the number of API calls an individual user can make per dayself.

The script creates a JSON file of businesses which is then mapped using a Leaflet.js script.
"""

from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib

# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY= "Bpr7aqrhwoYuY-I283HtuO01CzCLd8-Bd8tLmTRw4ddK-vAv0WYeode20fQ_EI90-OFb2KukYqkXjer05oeghtvjJOfMYDxp2PBVTXyRvw5xastlvsgb8Xlfl0UUW3Yx"
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

# Defaults for our simple example.
DEFAULT_TERM = 'cafes'
DEFAULT_LATITUDE = 40.841022
DEFAULT_LONGITUDE = -73.939791
DEFAULT_RADIUS = 6000
SEARCH_LIMIT = 50
DEFAULT_OFFSET = 0

zipcodes = ['10026', '10027', '10030', '10031', '10032', '10033', '10034', '10035', '10037', '10039', '10040']
cafes = {}

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')

    parser.add_argument('-lat', '--latitude', dest='latitude',
                        default=DEFAULT_LATITUDE, type=float,
                        help='Search latitude (default: %(default)s)')

    parser.add_argument('-lon', '--longitude', dest='longitude',
                        default=DEFAULT_LONGITUDE, type=float,
                        help='Search longitude (default: %(default)s)')

    parser.add_argument('-r', '--radius', dest='radius',
                        default=DEFAULT_RADIUS, type=int,
                        help='Search radius (default: %(default)s)')

    parser.add_argument('-o', '--offset', dest='offset',
                        default=DEFAULT_OFFSET, type=int,
                        help='Offset (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.latitude, input_values.longitude, input_values.radius, input_values.offset)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )

def query_api(term, latitude, longitude, radius, offset):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """

    response = search(API_KEY, term, latitude, longitude, radius, offset)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, latitude, longitude, radius))
        return

    business_id = businesses[0]['id']

    print(u'{0} businesses found, querying business info ' \
        'for the top result "{1}" ...'.format(
            len(businesses), business_id))

    tot_businesses = response.get('total')
    count = 0

    while offset < tot_businesses:
        print('Processing offset:', offset)
        businessCount = 0
        while businessCount < len(businesses):
            business_id = businesses[businessCount]['id']
            response = get_business(API_KEY, business_id)
            if businesses[businessCount]['is_closed'] == False:
                if businesses[businessCount]['location']['zip_code'] in zipcodes:
                    cafes.update({count:{
                        'name':businesses[businessCount]['name'],
                        'latitude':businesses[businessCount]['coordinates']['latitude'],
                        'longitude':businesses[businessCount]['coordinates']['longitude'],
                        'address':businesses[businessCount]['location']['display_address'],
                        'phone':businesses[businessCount]['phone'],
                        'URL':businesses[businessCount]['url'],
                        'imageURL':businesses[businessCount]['image_url'],
                        'rating':businesses[businessCount]['rating'],
                        'reviewCount':businesses[businessCount]['review_count']
                    }})
                businessCount+=1
                count+=1
        offset += 50
        response = search(API_KEY, term, latitude, longitude, radius, offset)
        businesses = response.get('businesses')

    with open('cafes.json', 'w') as outfile:
        json.dump(cafes, outfile)

def search(api_key, term, latitude, longitude, radius, offset):
    """Query the Search API by a search term and location.

        Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

        Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'limit': SEARCH_LIMIT,
        'offset': offset
    }

    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

def get_business(api_key, business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

if __name__ == '__main__':
    main()
