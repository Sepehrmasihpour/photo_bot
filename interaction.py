import time
import httpx

seshat_is_active = True


if __name__ == "__main__":
    while seshat_is_active:
        getUpdates_url = "http://127.0.0.1:8000/getUpdates"  #! This is the url for the local machine server, after deployment of the api change this to the actual url
        getUpdates_params = {
            "allowed_updates": ["audio", "photo", "video"],
            "timeout": 10,
        }

        update = httpx.get(getUpdates_url, params=getUpdates_params)
        update_json = update.json()
        print(update_json["result"])
        time.sleep(10)
