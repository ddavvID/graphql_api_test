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
    assert response1.status_code == 200
    json_data1 = response1.json()
    assert "errors" not in json_data1
    album1 = json_data1["data"]["createAlbum"]

    variables2 = {"input": {"title": "album1-1"}}
    response2 = run_graphql_query(mutation_create, variables2)
    assert response2.status_code == 200
    json_data2 = response2.json()
    assert "errors" not in json_data2
    album1_1 = json_data2["data"]["createAlbum"]

    yield album1, album1_1

    # Cleanup: delete created albums after tests
    mutation_delete = """
    mutation deleteAlbum($id: ID!) {
        deleteAlbum(id: $id)
    }
    """
    run_graphql_query(mutation_delete, {"id": album1["id"]})
    run_graphql_query(mutation_delete, {"id": album1_1["id"]})

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
    assert response_update.status_code == 200
    json_data = response_update.json()
    assert "errors" not in json_data
    updated_album = json_data["data"]["updateAlbum"]
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
    assert response_delete.status_code == 200
    json_data = response_delete.json()
    assert "errors" not in json_data
    deleted = json_data["data"]["deleteAlbum"]
    assert deleted is True

@pytest.mark.query_album
def test_query_album(create_albums):
    album1, _ = create_albums
    query_album = """
    query getAlbum($id: ID!) {
        album(id: $id) {
            id
            title
        }
    }
    """
    variables_query = {"id": album1["id"]}
    response_query = run_graphql_query(query_album, variables_query)
    assert response_query.status_code == 200
    json_data = response_query.json()
    assert "errors" not in json_data
    album = json_data["data"]["album"]
    assert album["id"] == album1["id"]
    assert album["title"] == album1["title"]

@pytest.mark.update_album_error
def test_update_album_invalid_id():
    mutation_update = """
    mutation updateAlbum($id: ID!, $input: UpdateAlbumInput!) {
        updateAlbum(id: $id, input: $input) {
            id
            title
        }
    }
    """
    variables_update = {
        "id": "invalid_id",
        "input": {"title": "newtitle"}
    }
    response_update = run_graphql_query(mutation_update, variables_update)
    assert response_update.status_code == 200
    json_data = response_update.json()
    # Expect errors due to invalid ID
    assert "errors" in json_data

@pytest.mark.create_album_error
def test_create_album_missing_title():
    mutation_create = """
    mutation createAlbum($input: CreateAlbumInput!) {
        createAlbum(input: $input) {
            id
            title
        }
    }
    """
    variables = {"input": {}}  # Missing title field
    response = run_graphql_query(mutation_create, variables)
    assert response.status_code == 200
    json_data = response.json()
    assert "errors" in json_data
