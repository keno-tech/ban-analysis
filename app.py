from flask import Flask, render_template, request, redirect, url_for, session
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pprint
import os
from datetime import timedelta, datetime
import secrets  # for generating secure session keys

app = Flask(__name__, static_url_path='/static')
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key
app.permanent_session_lifetime = timedelta(hours=1)  # Reduce session lifetime to 1 hour

# Create a ThreadPoolExecutor for running async code
thread_pool = ThreadPoolExecutor()

HERO_IMAGES = {
    "Black Panther": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1026.png%3Fv%3D1734906793/image.png",
    "Winter Soldier": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1041.png%3Fv%3D1734906798/image.png",
    "Spider-Man": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1036.png%3Fv%3D1734906795/image.png",
    "Storm": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1015.png%3Fv%3D1734906791/image.png",
    "Adam Warlock": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1046.png%3Fv%3D1734906798/image.png",
    "Star Lord": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1043.png%3Fv%3D1734906798/image.png",
    "Moon Knight": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1030.png%3Fv%3D1734906793/image.png",
    "Iron Man": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1034.png%3Fv%3D1734906794/image.png",
    "Hela": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1024.png%3Fv%3D1734906792/image.png",
    "Mantis": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1020.png%3Fv%3D1734906791/image.png",
    "Namor": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1045.png%3Fv%3D1734906798/image.png",
    "Captain America": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1022.png%3Fv%3D1734906792/image.png",
    "Luna Snow": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1031.png%3Fv%3D1734906794/image.png",
    "The Punisher": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1014.png%3Fv%3D1734906790/image.png",
    "Rocket Raccoon": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1023.png%3Fv%3D1734906792/image.png",
    "Wolverine": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1049.png%3Fv%3D1734906799/image.png",
    "Hawkeye": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1021.png%3Fv%3D1734906791/image.png",
    "Psylocke": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1048.png%3Fv%3D1734906799/image.png",
    "Squirrel Girl": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1032.png%3Fv%3D1734906794/image.png",
    "Magik": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1029.png%3Fv%3D1734906793/image.png",
    "Scarlet Witch": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1038.png%3Fv%3D1734906797/image.png",
    "Magneto": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1037.png%3Fv%3D1734906796/image.png",
    "Doctor Strange": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1018.png%3Fv%3D1734906791/image.png",
    "Venom": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1035.png%3Fv%3D1734906794/image.png",
    "Black Widow": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1033.png%3Fv%3D1734906794/image.png",
    "Cloak & Dagger": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1025.png%3Fv%3D1734906792/image.png",
    "Bruce Banner": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1011.png%3Fv%3D1734906790/image.png",
    "Hulk": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1011.png%3Fv%3D1734906790/image.png",
    "Groot": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1027.png%3Fv%3D1734906793/image.png",
    "Mister Fantastic": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1040.png%3Fv%3D1736499638/image.png",
    "Loki": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1016.png%3Fv%3D1734906791/image.png",
    "Invisible Woman": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1050.png%3Fv%3D1736499639/image.png",
    "Thor": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1039.png%3Fv%3D1734906797/image.png",
    "Iron Fist": "https://imgsvc.trackercdn.com/url/max-width(180),quality(70)/https%3A%2F%2Ftrackercdn.com%2Fcdn%2Ftracker.gg%2Fmarvel-rivals%2Fimages%2Fheroes%2Fsquare%2F1052.png%3Fv%3D1734906799/image.png"

    }   

def get_player_id(name):
    response = requests.get(f"https://mrapi.org/api/player-id/{name}")
    if response.status_code == 200:
        return response.json().get("id")
    return None

def get_player_stats(player_id):
    response = requests.get(f"https://mrapi.org/api/player/{player_id}")
    if response.status_code == 200:
        return response.json()["hero_stats"]
    return None

def get_ranked_stats(stats_list):
    ranked_stats_list = []
    for hero_id in stats_list:
        for id in hero_id:
            ranked_stats = hero_id.get(id).get("ranked")
            if ranked_stats is not None:
                ranked_stats_list.append((hero_id.get(id).get("hero_name"), ranked_stats))
    return ranked_stats_list

def analyze_ranked_stats(ranked_stats_list):
    target_bans = []
    for hero_name, stats in ranked_stats_list:
        wr = calculate_win_rate(stats)
        matches = stats['matches']
        if matches >= 15 and wr >= 50:
            target_bans.append((hero_name, str(wr) + "%"))
    return target_bans

def calculate_win_rate(stats):
    matches = stats['matches']
    wins = stats["wins"]

    if matches == 0:
        return 0
    else:
        win_rate = (wins / matches) * 100
        return round(win_rate, 2)


def multi_analysis(target_bans):
    name_wr_dict = {}
    for hero_stats in target_bans:
        hero_name = hero_stats[0]
        winrate = hero_stats[1]
        if hero_name in name_wr_dict:
            name_wr_dict[hero_name].append(winrate)
        else:
            name_wr_dict[hero_name] = [winrate]
    
    # Sort the dictionary by average winrate in descending order
    sorted_dict = dict(sorted(name_wr_dict.items(), 
                            key=lambda x: sum(float(wr.strip('%')) for wr in x[1])/len(x[1]), 
                            reverse=True))
    
    return sorted_dict
    
def average_winrate(name_wr_dict):
    def percentage_to_float(percentage):
        return float(percentage.strip('%')) / 100

    max_key = max(name_wr_dict, key=lambda k: (len(name_wr_dict[k]), sum([percentage_to_float(val) for val in name_wr_dict[k]]) / len(name_wr_dict[k]) if len(name_wr_dict[k]) > 0 else 0))

    sublist = name_wr_dict[max_key]

    values_as_floats = [percentage_to_float(val) for val in sublist]
    average = (sum(values_as_floats) / len(values_as_floats)) * 100  

    num_values = len(sublist)
    if num_values == 0:
        return None
    if num_values > 1:
        return f"There are {num_values } {max_key} players with an average winrate {average:.2f}%"
    else:
        return f"There is {num_values } {max_key} player with an average winrate {average:.2f}%"
        
def clear_data():
    pass

def main(player_names):
    target_bans = []
    player_stats = []
    
    for name in player_names:
        player_id = get_player_id(name)
        if player_id:
            stats = get_player_stats(player_id)
            if stats:
                player_stats.append(stats)
            else:
                print(f"Could not fetch stats for {name}")
                index = player_names.index(name)
                player_names[index] = (name + " has a private profile, not included")
        else:
            print(f"Could not fetch ID for {name}")
    
    ranked_stats = get_ranked_stats(player_stats)
    target_bans = analyze_ranked_stats(ranked_stats)
    name_wr_dict = multi_analysis(target_bans)
        
    return name_wr_dict

async def get_player_id_async(name, session):
    async with session.get(f"https://mrapi.org/api/player-id/{name}") as response:
        if response.status == 200:
            data = await response.json()
            return data.get("id")
    return None

async def get_player_stats_async(player_id, session):
    async with session.get(f"https://mrapi.org/api/player/{player_id}") as response:
        if response.status == 200:
            data = await response.json()
            return data["hero_stats"]
    return None

async def process_player_async(name):
    async with aiohttp.ClientSession() as session:
        player_id = await get_player_id_async(name, session)
        if player_id:
            stats = await get_player_stats_async(player_id, session)
            return name, stats
        return name, None

async def main_async(player_names):
    player_stats = []
    
    # Process all players concurrently
    async with aiohttp.ClientSession() as session:
        tasks = [process_player_async(name) for name in player_names]
        results = await asyncio.gather(*tasks)
        
        for name, stats in results:
            if stats:
                player_stats.append(stats)
            else:
                print(f"Could not fetch stats for {name}")
    
    ranked_stats = get_ranked_stats(player_stats)
    target_bans = analyze_ranked_stats(ranked_stats)
    name_wr_dict = multi_analysis(target_bans)
        
    return name_wr_dict

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        print("GET request received")
        session.clear()
        return render_template('index.html', 
                             player_names=[],
                             result=None,
                             highlight=None,
                             error_messages=[],
                             hero_images=HERO_IMAGES)
    
    if request.method == 'POST':
        print("POST request received")
        result = None
        highlight = None
        error_messages = []
        
        submitted_names = [request.form.get(f'player{i}', '').strip() for i in range(1, 6)]
        submitted_names = [name for name in submitted_names if name]
        
        if len(submitted_names) != len(set(submitted_names)):
            seen = set()
            duplicates = set(name for name in submitted_names if name in seen or seen.add(name))
            error_messages.append(f"Duplicate player names found: {', '.join(duplicates)}. Each player name must be unique.")
            return render_template('index.html', 
                                player_names=submitted_names,
                                result=None,
                                highlight=None,
                                error_messages=error_messages,
                                hero_images=HERO_IMAGES)
        
        if submitted_names:
            try:
                # Run the async analysis in a separate thread
                future = thread_pool.submit(run_async, main_async(submitted_names))
                result = future.result()
                
                if result:
                    highlight = average_winrate(result)
            except Exception as e:
                print(f"Error in analysis: {str(e)}")
                error_messages.append(f"Error in analysis: {str(e)}")
        else:
            error_messages.append("No player names submitted")
            
        return render_template('index.html', 
                             player_names=submitted_names,
                             result=result,
                             highlight=highlight,
                             error_messages=error_messages,
                             hero_images=HERO_IMAGES)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
