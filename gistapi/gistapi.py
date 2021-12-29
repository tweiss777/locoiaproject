# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
import re as regex
import urllib3
import json

# *The* app object
app = Flask(__name__)

# our http object for urllib3
http = urllib3.PoolManager()



'''helper function for retrieving pattern in url
    params : pattern str, url str
    returns url if regex pattern detected in content
    

'''
def retrieve_pattern(pattern: str, gist_id: str,user: str):
    # retrieve the gist page
    final_url = "https://gist.github.com/{user}/{gist_id}".format(user=user,gist_id=gist_id)
    gist_page = http.request('GET', final_url)

    # store gist page in Beautiful soup object to retrieve text
    html_content = BeautifulSoup(gist_page.data,'html.parser')

    text_content = html_content.getText()

    if bool(regex.search(pattern, text_content)):
        return final_url
    return ""





@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


# this is where we implement retrieving gists
def gists_for_user(username):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = 'https://api.github.com/users/{username}/gists'.format(
            username=username)
    response = http.request('GET',gists_url)
    jsonResponse = json.loads(response.data)
    if response.status == 200 and len(jsonResponse) >= 1:
        return jsonResponse

    # BONUS: What failures could happen?
        # we can end up getting a status 400 or 404 in that case we can return a message saying something is wrong with github
    elif response.status == 404 or response.status == 400:
        return "Something is wrong with github"
    else:

        # BONUS: Handle invalid users?
            # the way we handle invalid users is by checking what is returned from the gist api.
            # if the list of gists returned from the user is empty based on testing the gist api
            # it means that the user is not found
        return "Error: username not found"

    # BONUS: Paging? How does this work for users with tons of gists?
        # we can assign a certain amount of results to a page which would reduce the number of data sent by the api
        # we can even program the api to return a range of results from page number to page number limiting the data returned by the api


@app.route("/api/v1/search", methods=['POST'])
def search():
    print("Recieving connection")
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    try:
        post_data = request.get_json()
        # BONUS: Validate the arguments?
        username = post_data['username']
        pattern = post_data['pattern']
    except KeyError: # we can validate the arguments in the post request by checking the keys in the request
        return jsonify("Invalid arguments")
    # limit = post_data['limit']
    # initialize result to empty dict and matches to empty array to store urls that contain matching regex
    result = {}
    result['matches'] = []

    gists = gists_for_user(username)

    # Handle invalid users with this if statement below
    if gists == "Error: username not found":
        result['status'] = 'failure'
        result['username'] = username
        result['pattern'] = pattern
        result['matches'] = ['Error: User not found']
        return jsonify(result)


    for gist in gists:
        # REQUIRED: Fetch each gist and check for the pattern
        match = retrieve_pattern(pattern,gist['id'],username)
        if len(match) >= 1:
            result['matches'].append(match)
        # BONUS: What about huge gists?
            # we can create a new endpoint that limits up to a certain number of gists
            # by passing in the length as an int and we can compare the length of the json result downloaded from github
            # to the length we specified and if the length of the json results exceed that of the limit we can just return what is below the limit threshold
        # BONUS: Can we cache results in a datastore/db?

    if len(result['matches']) >= 1:
        result['status'] = 'success'
    else:
        result['status'] = 'failure'
        result['matches'] = ['Error: No matches found']
    result['username'] = username
    result['pattern'] = pattern

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9876)
