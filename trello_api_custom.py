def trello_update():
    import requests
    import json
    import webbrowser as wb

    trello_key = '******'
    url = 'https://api.trello.com/1/'
    api_url = {'boards': 'boards/', 'all_boards': 'members/me/boards/', 'lists': 'lists/'}

    def trello_authorize():
        global user_token
        auth_url = 'https://trello.com/1/authorize'
        payload_auth = {
            'scope': 'read,write',
            'expiration': 'never',
            'name': 'Item_Tracker',
            'key': trello_key,
            'response_type': 'token'
        }

        response_trello_auth = requests.get(auth_url, params=payload_auth)
        wb.get().open(response_trello_auth.url, new=1)

        input("Authorize the app in your browser")
        user_token = input("Please input here the PIN you received in the browser: ")

        with open('user_trello_token.txt', 'w+') as user_trello_token:
            user_trello_token.write(user_token)
        return user_token

    try:
        with open('user_trello_token.txt', 'r') as user_trello_token:
            user_token = user_trello_token.read()

    except FileNotFoundError:
        user_token = trello_authorize()

    finally:
        payload_api = {'fields': 'name,url', 'key': trello_key, 'token': user_token}
        boards = requests.get(url+api_url['all_boards'], params=payload_api)

        # IF THE TOKEN IS NOT VALID ANYMORE (CODE 401):
        if boards.status_code == 401:
            print('The token used is invalid, you will be redirected to authorize the app again')
            user_token = trello_authorize()

            payload_api = {'fields': 'name,url', 'key': trello_key, 'token': user_token}
            boards = requests.get(url + api_url['all_boards'], params=payload_api)
            boards_json = boards.json()
        else:
            boards_json = boards.json()

        # ML BOARD #
        verificador_board = False

        print('Getting the ML Boards')

        for board in boards_json:
            if board["name"] == "ML Price Tracker":
                ML_board = board
                verificador_board = True
                break

        if verificador_board is False:
            ML_board = {}
            board_creation = requests.post(url+api_url['boards'], data={
                                                                        'key': trello_key,
                                                                        'token': user_token,
                                                                        'name': "ML Price Tracker",
                                                                        'defaultLists': 'false'})
            ML_board['id'] = board_creation.json()['id']
            ML_board['name'] = board_creation.json()['name']
            ML_board['url'] = board_creation.json()['url']

        # PREVIOUS DATA BOARD #
        verificador_board = False

        print('Getting the Previous Data Board')

        for board in boards_json:
            if board["name"] == "Previous Data":
                Previous_board = board
                verificador_board = True
                break

        if verificador_board is False:
            Previous_board = {}
            board_creation = requests.post(url+api_url['boards'], data={
                                                                        'key': trello_key,
                                                                        'token': user_token,
                                                                        'name': "Previous Data",
                                                                        'defaultLists': 'false'})
            Previous_board['id'] = board_creation.json()['id']
            Previous_board['name'] = board_creation.json()['name']
            Previous_board['url'] = board_creation.json()['url']

        # Getting all lists in the ML board
        lists_on_board = requests.get(url + api_url['boards'] + ML_board['id'] + '/lists',
                                      params={'key': trello_key,
                                              'token': user_token
                                              })
        lists_on_board_json = lists_on_board.json()

        # Getting all lists in the Previous Data Board
        lists_on_previous = requests.get(url + api_url['boards'] + Previous_board['id'] + '/lists',
                                         params={'key': trello_key,
                                                 'token': user_token
                                                 })

        lists_on_previous_json = lists_on_previous.json()

        # Creating a delete board
        delete_board = requests.post(url + api_url['boards'], data={
                                                                    'key': trello_key,
                                                                    'token': user_token,
                                                                    'name': "Delete_Board",
                                                                    'defaultLists': 'false'
                                                                    })
        delete_board_json = delete_board.json()

        # Transferring all lists in Previous Data Board to Delete Board

        print("Transferring the Previous Data Board's lists to the Delete Board")

        for listas in lists_on_previous_json:
            move_lists = requests.put(url + api_url['lists'] + listas['id'] + '/idBoard',
                                      params={
                                                'key': trello_key,
                                                'token': user_token,
                                                'value': delete_board_json['id']
                                              })

        # Transferring all lists in ML Board to Previous Board

        print("Transferring the ML Board's lists to the Previous Board")

        for listas in lists_on_board_json:
            move_lists = requests.put(url + api_url['lists'] + listas['id'] + '/idBoard',
                                      params={'key': trello_key,
                                              'token': user_token,
                                              'value': Previous_board['id']
                                              })

        with open('items.json') as items_json:
            all_items = json.load(items_json)

        # Creating lists for the updated data obtained from the ML
        i = 0

        print(f'Updating Lists')

        for listas in all_items:
            list_create = requests.post(url + api_url['lists'], params={
                                                                        'key': trello_key,
                                                                        'token': user_token,
                                                                        'name': listas[0]['title'],
                                                                        'idBoard': ML_board['id']
                                                                        })

            for dicionarios in listas:
                desc = f'id: {dicionarios["id"]}\nseller: {dicionarios["seller"]}\nprice: {dicionarios["price"]}'
                card_create = requests.post(url + 'cards/', params={
                                                                    'key': trello_key,
                                                                    'token': user_token,
                                                                    'name': f"{dicionarios['title']} - R$ {dicionarios['price']}",
                                                                    'desc': desc,
                                                                    'idList': list_create.json()['id']
                                                                    })
            i = i+1
            print(f'List {i} updated')

        # Deleting the Delete Board
        delete = requests.delete(url + api_url['boards'] + delete_board_json['id'], data={
                                                                                          'key': trello_key,
                                                                                          'token': user_token,
                                                                                          })

