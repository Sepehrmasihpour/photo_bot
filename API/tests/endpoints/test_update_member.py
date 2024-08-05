from db_control import get_member_info, delete_member_info, insert_member_info

member_data = {"name": "test_name", "user_name": "test_user_name", "chat_id": 1}
chat_id = member_data["chat_id"]
updated_member_data = {
    "name": "test_name",
    "user_name2": "test_user_name2",
    "chat_id": chat_id,
}


def test_new_member(client):
    try:

        response = client.post("/updateGroupMembers", params=member_data)
        result = get_member_info(chat_id)
        assert result, "The new member data was not added to the data base"
        print(response["message"])
        if result:
            delete_member_info(chat_id)
    except Exception as e:
        print(f"error doing adding the tests member error:{e}")


def test_update_member_info(client):
    try:

        insert_member_info(
            chat_id=chat_id,
            name=member_data["name"],
            user_name=member_data["user_name"],
        )
        response = client.post("/updateGroupMembers", params=updated_member_data)
        result = get_member_info(chat_id=chat_id)
        assert result == updated_member_data, "The member info was not updated"
        print(response["message"])
        if result:
            delete_member_info(chat_id=chat_id)
    except Exception as e:
        print(f"error updating the member info. error:{e}")
