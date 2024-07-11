def test_change_group_photo_sucsess(client):
    params = {
        "file_id": "AgACAgQAAx0CfLzENAADn2aOjypywC8emWA1LNsMsjPgpGsGAALZszEbze-tU2pTtamGq1BCAQADAgADbQADNQQ"
    }
    response = client.post("/changGroupPhoto", params=params)
    response_json = response.json()
    assert (
        response_json["ok"] == True
    ), "The method does not change the photo here even though it should"
    assert (
        response_json["result"] == True
    ), "The method does not change the photo here even though it should"
