import pytest
import requests

GRAPHQL_URL = "https://graphqlzero.almansi.me/api"

def run_graphql_query(query, variables=None):
    payload = {
        "query": query,
        "variables": variables or {}
    }
    response = requests.post(GRAPHQL_URL, json=payload)
    return response

@pytest.fixture(scope="module")
def create_albums():
    mutation_create = """
    mutation createAlbum($input: CreateAlbumInput!) {
        createAlbum(input: $input) {
            id
            title
        }
    }
    """
    variables1 = {"input": {"title": "album1"}}
    response1 = run_graphql_query(mutation_create, variables1)
    album1 = response1.json()["data"]["createAlbum"]

    variables2 = {"input": {"title": "album1-1"}}
    response2 = run_graphql_query(mutation_create, variables2)
    album1_1 = response2.json()["data"]["createAlbum"]

    return album1, album1_1

@pytest.mark.update_album
def test_update_album(create_albums):
    album1, album1_1 = create_albums

    mutation_update = """
    mutation updateAlbum($id: ID!, $input: UpdateAlbumInput!) {
        updateAlbum(id: $id, input: $input) {
            id
            title
        }
    }
    """
    variables_update = {
        "id": album1_1["id"],
        "input": {"title": "album2"}
    }
    response_update = run_graphql_query(mutation_update, variables_update)
    updated_album = response_update.json()["data"]["updateAlbum"]
    assert updated_album["title"] == "album2"

@pytest.mark.delete_album
def test_delete_album(create_albums):
    album1, album1_1 = create_albums

    mutation_delete = """
    mutation deleteAlbum($id: ID!) {
        deleteAlbum(id: $id)
    }
    """
    variables_delete = {"id": album1["id"]}
    response_delete = run_graphql_query(mutation_delete, variables_delete)
    deleted = response_delete.json()["data"]["deleteAlbum"]
    assert deleted is True
