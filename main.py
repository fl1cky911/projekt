from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from tinydb import TinyDB
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'steam.png', mimetype='image/vnd.microsoft.icon')



# discounts
@app.route("/", methods=['GET', 'POST'])
def indexpage():
    pop = []
    url = "https://store.steampowered.com/api/featuredcategories?cc=EUR"
    res = requests.get(url)
    spisek = res.json()
    for i in range(len(spisek["specials"]['items'])):
        slika = spisek["specials"]['items'][i]['header_image']
        ime = spisek["specials"]['items'][i]['name']
        cena = spisek["specials"]['items'][i]['final_price']
        originalcena = spisek["specials"]['items'][i]['original_price']
        pop.append({
            'header_image': slika,
            'name': ime,
            'new price': cena / 100,
            'original price': originalcena / 100
        })

# week specials
    weekspec = []
    for x in range(7):
        if f"{x}" in spisek and 'items' in spisek[f"{x}"] and len(spisek[f"{x}"]['items']) > 0:
            slikaweek = spisek[f"{x}"]['items'][0].get('header_image')
            urlplswork = spisek[f"{x}"]['items'][0].get('url')
            weekspec.append({'header_image': slikaweek, 'url': urlplswork})
        else:
            slikaweek = None
            urlplswork = None
            weekspec.append({'header_image': slikaweek, 'url': urlplswork})
    # coming soon
    csp = []
    for cs in range(len(spisek["coming_soon"]['items'])):
        slikacs = spisek["coming_soon"]['items'][cs]['header_image']
        imecs = spisek["coming_soon"]['items'][cs]['name']
        originalcenacs = spisek["coming_soon"]['items'][cs]['original_price']
        finalcenacs = spisek["coming_soon"]['items'][cs]['final_price']
        csp.append({
            'header_image': slikacs,
            'name': imecs,
            'final price': finalcenacs / 100,
            'original price': originalcenacs / 100 if originalcenacs is not None else None
        })
        
    # TOP SELLERS
    tsp = []
    for ts in range(len(spisek["top_sellers"]['items'])):
        slikatsp = spisek["top_sellers"]['items'][ts]['header_image']
        imetsp = spisek["top_sellers"]['items'][ts]['name']
        originalcenatsp = spisek["top_sellers"]['items'][ts]['original_price']
        finalcenatsp = spisek["top_sellers"]['items'][ts]['final_price']
        tsp.append({
            'header_image': slikatsp,
            'name': imetsp,
            'final price': finalcenatsp / 100,
            'original price': originalcenatsp / 100 if originalcenatsp is not None else None
        })

    # new releases
    nrp_list = []
    for nrp in range(len(spisek["new_releases"]['items'])):
        slikanrp = spisek["new_releases"]['items'][nrp]['header_image']
        imetnrp = spisek["new_releases"]['items'][nrp]['name']
        originalcenanrp = spisek["new_releases"]['items'][nrp]['original_price']
        finalcenanrp = spisek["new_releases"]['items'][nrp]['final_price']
        nrp_list.append({
            'header_image': slikanrp,
            'name': imetnrp,
            'final price': finalcenanrp / 100,
            'original price': originalcenanrp / 100 if originalcenanrp is not None else None
        })
    
    return render_template('index.html', pop=pop, weekspec=weekspec, csp=csp, tsp=tsp, nrp=nrp_list)

# live player count
@app.route('/games', methods=['GET', 'POST'])
def index():
    with open('player_counts.json') as f:
        games = json.load(f)

    game_data = []
    for game in games:
        app_id = game["id"]
        app_name = game["name"]
        url = f"http://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={app_id}&l=en"
        response = requests.get(url)
        data = response.json()

        if data.get('response') and data['response'].get('result') != 42:
            player_count = data['response'].get('player_count', 0)
            game_info = get_game_info(app_id)
            if game_info:
                game_data.append({
                    'name': app_name,
                    'player_count': player_count,
                    'image_url': game_info['image_url'],
                    'game_id': app_id
                })

    sorted_game_data = sorted(game_data, key=lambda x: x['player_count'], reverse=True)
    return render_template('live.html', game_data=sorted_game_data)

@app.route('/game/<game_id>')
def game_details(game_id):
    game_info = get_game_info(game_id)
    if game_info:
        return render_template('game_details.html', **game_info)
    else:
        return "Game details not found."

def get_game_info(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=en"
    response = requests.get(url)
    data = response.json()

    if data.get(app_id) and data[app_id].get('success'):
        game_data = data[app_id]['data']
        if game_data.get('header_image'):
            image_url = game_data['header_image']
            platforms = game_data['platforms']
            supported_platforms = [platform for platform, supported in platforms.items() if supported]
            return {
                'image_url': image_url,
                'name': game_data['name'],
                'release_date': game_data['release_date']['date'],
                'developers': ', '.join(game_data['developers']),
                'publishers': ', '.join(game_data['publishers']),
                'genres': [genre['description'] for genre in game_data['genres']],
                'screenshots': game_data['screenshots'],
                'supported_platforms': supported_platforms
            } 
    return None


@app.route('/dontpress', methods=['GET', 'POST'])
def dontpress():
  return render_template('dontpress.html')

@app.route('/player', methods=['GET', 'POST'])
def index1():
    return render_template('index_player.html')

import requests

import requests

@app.route('/player_info', methods=['GET', 'POST'])
def player_info():
    player_id = request.form['player_id']

    # Retrieve player info from Steam API
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=5673C50B8372BAD2BA70C3C51DF74F59&steamids={player_id}'
    response = requests.get(url)
    data = response.json()

    if data['response']['players']:
        player_info = data['response']['players'][0]

        # Retrieve player's country from Steam API
        player_country_url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=5673C50B8372BAD2BA70C3C51DF74F59&steamids={player_id}'
        player_country_response = requests.get(player_country_url)
        player_country_data = player_country_response.json()
        player_country = player_country_data['response']['players'][0].get('loccountrycode', 'N/A')

        # Retrieve player's games from Steam API
        games_url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=5673C50B8372BAD2BA70C3C51DF74F59&steamid={player_id}&format=json'
        games_response = requests.get(games_url)
        games_data = games_response.json()

        if games_data.get('response'):
            games_info = games_data['response'].get('games', [])

            # Sort games by playtime and get the top 3 played games
            top_games = sorted(games_info, key=lambda x: x.get('playtime_forever', 0), reverse=True)[:3]

            # Fetch game details including the game name
            for game in top_games:
                app_id = game['appid']
                app_details_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}&l=en'
                app_details_response = requests.get(app_details_url)
                app_details_data = app_details_response.json()

                if app_details_data.get(str(app_id)):
                    game_details = app_details_data[str(app_id)]
                    if game_details.get('success') and game_details.get('data'):
                        game['name'] = game_details['data'].get('name')
                        game['logo_url'] = game_details['data'].get('header_image')

            # Estimate account worth based on number of games owned
            account_worth = len(games_info) * 10  # Assuming an average game price of $10

            # Add country, games, and account worth to the player_info dictionary
            player_info['country'] = player_country
            player_info['games_owned'] = len(games_info)
            player_info['account_worth'] = account_worth

            # Save player info to a JSON file
            with open('player_info.json', 'w') as file:
                json.dump(player_info, file)

            return render_template('player_info.html', player=player_info, top_games=top_games)
        else:
            error_message = 'No game data available for the player.'
            return render_template('index_player.html', error=error_message)
    else:
        error_message = 'Player not found.'
        return render_template('index_player.html', error=error_message)




if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
