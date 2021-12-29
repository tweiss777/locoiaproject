import os
import json
import tempfile

import pytest

import gistapi


@pytest.fixture
def client(request):
    #db_fd, gistapi.app.config['DATABASE'] = tempfile.mkstemp()
    gistapi.app.config['TESTING'] = True
    client = gistapi.app.test_client()

    #with gistapi.app.app_context():
    #    gistapi.init_db()
    
    #def teardown():
    #    os.close(db_fd)
    #    os.unlink(flaskr.app.config['DATABASE'])
    #request.addfinalizer(teardown)

    return client


def test_ping(client):
    """Start with a sanity check."""
    rv = client.get('/ping')
    assert b'pong' in rv.data


def test_search(client):
    """Start with a passing test."""
    post_data = {'username': 'justdionysus', 'pattern': 'TerbiumLabsChallenge_[0-9]+'}
    rv = client.post('/api/v1/search', 
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'success', 
                     'username': 'justdionysus',
                     'pattern': 'TerbiumLabsChallenge_[0-9]+',
                     'matches': ['https://gist.github.com/justdionysus/6b2972aa971dd605f524']}

    assert result_dict == expected_dict


'''Test case to handle if the user is not found via the gist api'''
def test_search_fail(client):
    dataTopass = {
        'username': 'badusername',
        'pattern':  '(.docx|.pdf)'
    }

    actual_result = client.post('/api/v1/search',
                     data=json.dumps(dataTopass),
                     headers={'content-type': 'application/json'})
    actual_result = json.loads(actual_result.data.decode('utf-8'))
    
    expected_result = {
        'status': 'failure',
        'username': 'badusername',
        'pattern': '(.docx|.pdf)',
        'matches': ['Error: User not found']
    }

    assert expected_result == actual_result


# test case for valid user input
def test_validate_input(client):
    dataToPass = {"something":"hello world"}
    actual_result = client.post('/api/v1/search',data=json.dumps(dataToPass),headers={'content-type': 'application/json'})
    actual_result = json.loads(actual_result.data.decode('utf-8'))

    expected_result = "Invalid arguments"
    assert expected_result == actual_result