import threading
import time
url_get = ''


# function used to filter the search of items
def prep_func(x):
    prepositions = ['a', 'ante', 'após', 'até', 'com', 'contra', 'de', 'desde', 'em', 'entre',
                    'para', 'per', 'perante', 'por', 'sem', 'sob', 'sobre', 'trás', 'pelo',
                    'pela', 'pelos', 'pelas', 'dos', 'das']
    if x.lower() not in prepositions and len(x) > 2:
        return x


def server():
    from flask import Flask, render_template, request
    app = Flask(__name__)

    @app.route('/')
    def confirmation():
        global url_get
        url_get = request.query_string.decode('utf-8')
        return render_template("Confirmation Page.html")

    app.run()


def aplicativo():
    global url_get
    import requests
    import webbrowser as wb
    import json
    import time
    from trello_api_custom import trello_update

    app_id = "*****"
    app_secret = "******"
    redirect = "http://localhost:5000/"

    url = 'https://api.mercadolibre.com/'
    url_search = 'https://api.mercadolibre.com/sites/MLB/search'
    auth_url = "https://auth.mercadolivre.com.br/authorization/"
    token_url = "https://api.mercadolibre.com/oauth/token/"

    payload_auth = {"response_type": "code", "client_id": app_id, "redirect_uri": redirect}
    response_auth = requests.get(auth_url, params=payload_auth)
    wb.get().open(response_auth.url, new=1)

    input("Authorize the app in your browser")

    authorization_code = (url_get.split('=')[1])
    auth_payload = {
                     "grant_type": "authorization_code",
                     "client_id": app_id,
                     "client_secret": app_secret,
                     "redirect_uri": redirect,
                     "code": authorization_code
                    }

    auth_token = requests.post(token_url, data=auth_payload)
    token_json = auth_token.json()
    access_token = token_json["access_token"]

    while True:
        # --- items --- #
        user_info = requests.get(url + 'users/me', params={'access_token': access_token})

        user_items_info = requests.get(
                                url + "users/" +
                                str(user_info.json()["id"]) +
                                "/items/search",
                                params={'access_token': access_token}
                                )

        item = requests.get(
                            url +
                            "items/",
                            params={'ids': ','.join(user_items_info.json()["results"]), 'access_token': access_token}
                            )
        user_items = []

        for items in item.json():
            user_items.append({'id': items['body']['id'], 'title': items["body"]["title"], 'seller': items["body"]["seller_id"],'category_id': items["body"]["category_id"], 'price': items["body"]["price"]})
            print(f'{items["body"]["title"]}, {items["body"]["category_id"]}, {items["body"]["price"]}')
            print('')

        user_items.sort(key=lambda e: e["title"], reverse=True)

        specific_item = []
        all_items = []
        i = 0
        for dict_items in user_items:

            title = dict_items['title']
            title_list = title.split(' ')
            title_list = list(filter(prep_func, title_list))

            # IN THIS SECTION WE GET ONLY THE FIRST 4 WORDS OF OUR ADVERTISEMENT
            # SO WE DO NOT END UP WITH A OVERLY SPECIFIC SEARCH TERM

            if len(title_list) > 4:
                title_list = title_list[0:4]
                title = ' '.join(title_list)
            else:
                title = ' '.join(title_list)

            category = dict_items['category_id']
            payload_search = {'q': title, 'category': category, 'power_seller': 'yes', 'sort': 'price_asc'}
            response = requests.get(url_search, params=payload_search)

            for results in response.json()['results']:
                specific_item.append({
                                      'id': results['id'],
                                      'title': results['title'],
                                      'seller': results['seller']['id'],
                                      'price': results['price']
                                      })
            specific_item.sort(key=lambda e: float(e["price"]))
            specific_item.insert(0, dict_items)
            all_items.append(specific_item)
            specific_item = []
            i = i+1
            print(f'item {i} done')

        with open('items.json', 'w') as items_json:
            items_json.seek(0)
            json.dump(all_items, items_json, indent=3)
            items_json.truncate()

        trello_update()

        print('Done')

        time.sleep(18000)
        refresh_payload = {
                           "grant_type": "refresh_token",
                           "client_id": app_id,
                           "client_secret": app_secret,
                           "refresh_token": token_json["refresh_token"]
                           }

        refresh_token = requests.post(token_url, data=refresh_payload).json()
        access_token = refresh_token["access_token"]


if __name__ == "__main__":
    t1 = threading.Thread(target=server)
    t2 = threading.Thread(target=aplicativo)

    t1.start()
    time.sleep(3)
    t2.start()
