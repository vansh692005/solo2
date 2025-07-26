
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import json
import os
from datetime import datetime, timedelta
import random
import hashlib
import secrets
from tinydb import TinyDB, Query
from functools import wraps

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your-secret-key-change-in-production'

# Initialize TinyDB
db = TinyDB('game_database.json')
users_table = db.table('users')
player_data_table = db.table('player_data')

User = Query()

def hash_password(password):
    """Hash password with salt"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id():
    """Generate unique user ID"""
    return secrets.token_hex(16)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_user_data(user_id):
    """Get user's game data"""
    user_data = player_data_table.search(User.user_id == user_id)
    if user_data:
        data = user_data[0]
        check_daily_reset(data)
        return data
    else:
        # Create default data for new user
        default_data = create_default_game_data(user_id)
        player_data_table.insert(default_data)
        return default_data

def save_user_data(user_id, data):
    """Save user's game data"""
    player_data_table.upsert(data, User.user_id == user_id)

def create_default_game_data(user_id):
    """Create default game data for new user"""
    return {
        "user_id": user_id,
        "player": {
            "name": "NEW HUNTER",
            "level": 0,
            "current_xp": 0,
            "xp_to_next_level": 100,
            "class": "BEGINNER",
            "title": "NEWBIE",
            "rank": "E",
            "rank_name": "AWAKENED",
            "rank_score": 0,
            "points_to_next_rank": 200,
            "total_experience": 0,
            "stats": {
                "strength": 10,
                "agility": 10,
                "perception": 10,
                "vitality": 10,
                "intelligence": 10,
                "available_points": 0
            },
            "leaderboard_points": 0,
            "physical_damage_reduction": 0,
            "magical_damage_reduction": 0,
            "streak": 0,
            "max_streak": 0,
            "coins": 100,
            "energy": 100,
            "max_energy": 100
        },
        "daily_tasks": [{
            "name": "12 PUSHUPS",
            "completed": False,
            "progress": 0,
            "max": 12,
            "xp_reward": 25,
            "coin_reward": 10
        }, {
            "name": "12 SITUPS",
            "completed": False,
            "progress": 0,
            "max": 12,
            "xp_reward": 25,
            "coin_reward": 10
        }, {
            "name": "2KM OUTDOOR RUN",
            "completed": False,
            "progress": 0,
            "max": 2,
            "xp_reward": 50,
            "coin_reward": 20
        }, {
            "name": "MEDITATE 15 MIN",
            "completed": False,
            "progress": 0,
            "max": 15,
            "xp_reward": 30,
            "coin_reward": 15
        }],
        "timer": {
            "hours": 4,
            "minutes": 43,
            "seconds": 0
        },
        "last_reset": datetime.now().strftime("%Y-%m-%d"),
        "inventory": [{
            "name": "Health Potion",
            "quantity": 3,
            "type": "consumable",
            "effect": "Restores 50 HP"
        }, {
            "name": "Energy Drink",
            "quantity": 2,
            "type": "consumable",
            "effect": "Restores 30 Energy"
        }],
        "quests": {
            "strength_training": {
                "progress": 0,
                "max": 100,
                "completed": False,
                "reward_coins": 100,
                "reward_xp": 200
            },
            "intelligence": {
                "progress": 0,
                "max": 100,
                "completed": False,
                "reward_coins": 100,
                "reward_xp": 200
            },
            "discipline": {
                "progress": 0,
                "max": 100,
                "completed": False,
                "reward_coins": 150,
                "reward_xp": 250
            },
            "spiritual_training": {
                "progress": 0,
                "max": 100,
                "completed": False,
                "reward_coins": 120,
                "reward_xp": 220
            },
            "secret_quests": {
                "progress": 0,
                "max": 100,
                "completed": False,
                "reward_coins": 500,
                "reward_xp": 1000
            },
            "personal_quests": 0
        },
        "personal_quest_list": [],
        "achievements": [{
            "name": "First Steps",
            "description": "Complete your first daily task",
            "unlocked": False,
            "reward_coins": 50
        }, {
            "name": "Dedication",
            "description": "Maintain a 7-day streak",
            "unlocked": False,
            "reward_coins": 200
        }, {
            "name": "Level Up",
            "description": "Reach level 5",
            "unlocked": False,
            "reward_coins": 100
        }, {
            "name": "Quest Master",
            "description": "Complete 5 quests",
            "unlocked": False,
            "reward_coins": 300
        }, {
            "name": "Unstoppable",
            "description": "Maintain a 30-day streak",
            "unlocked": False,
            "reward_coins": 1000
        }],
        "shop": [{
            "name": "Health Potion",
            "price": 25,
            "type": "consumable",
            "effect": "Restores 50 HP"
        }, {
            "name": "Energy Drink",
            "price": 20,
            "type": "consumable",
            "effect": "Restores 30 Energy"
        }, {
            "name": "XP Booster",
            "price": 100,
            "type": "booster",
            "effect": "Double XP for next task"
        }, {
            "name": "Stat Point",
            "price": 200,
            "type": "permanent",
            "effect": "Gain 1 available stat point"
        }],
        "settings": {
            "notifications": True,
            "sound_effects": True,
            "dark_mode": True,
            "daily_reset_time": "00:00"
        }
    }

def check_daily_reset(data):
    """Check if daily tasks need to be reset"""
    today = datetime.now().strftime("%Y-%m-%d")
    if data.get("last_reset") != today:
        # Check if all tasks were completed yesterday
        all_completed = all(task["completed"] for task in data["daily_tasks"])

        # Reset streak if not all tasks completed
        if not all_completed:
            data["player"]["streak"] = 0

        # Calculate progressive difficulty based on streak
        streak = data["player"]["streak"]
        pushup_count = 12 + (streak * 2)
        situp_count = 12 + (streak * 2)

        # Reset daily tasks with progressive difficulty
        for task in data["daily_tasks"]:
            task["completed"] = False
            task["progress"] = 0

            if "PUSHUPS" in task["name"]:
                task["name"] = f"{pushup_count} PUSHUPS"
                task["max"] = pushup_count
            elif "SITUPS" in task["name"]:
                task["name"] = f"{situp_count} SITUPS"
                task["max"] = situp_count

        # Reset timer
        data["timer"] = {"hours": 4, "minutes": 43, "seconds": 0}
        data["last_reset"] = today

        # Restore energy
        data["player"]["energy"] = data["player"]["max_energy"]

        save_user_data(data["user_id"], data)

def calculate_level_from_xp(total_xp):
    """Calculate level and current XP from total experience"""
    level = 0
    xp_needed = 100
    current_xp = total_xp

    while current_xp >= xp_needed:
        current_xp -= xp_needed
        level += 1
        xp_needed = int(xp_needed * 1.2)

    return level, current_xp, xp_needed

def award_experience(data, xp_amount):
    """Award XP and handle level ups"""
    data["player"]["total_experience"] += xp_amount
    old_level = data["player"]["level"]

    new_level, current_xp, xp_to_next = calculate_level_from_xp(
        data["player"]["total_experience"])

    data["player"]["level"] = new_level
    data["player"]["current_xp"] = current_xp
    data["player"]["xp_to_next_level"] = xp_to_next

    if new_level > old_level:
        levels_gained = new_level - old_level
        data["player"]["stats"]["available_points"] += levels_gained * 2
        data["player"]["coins"] += levels_gained * 50
        update_class_and_title(data)
        check_achievements(data)

def calculate_rank_score(data):
    """Calculate rank score based on player progress"""
    player = data["player"]
    stats = player["stats"]

    total_stats = sum(value for key, value in stats.items()
                      if key != "available_points")

    score = (player["level"] * 10 + total_stats * 2 +
             player["max_streak"] * 5 + player["total_experience"] // 100)

    return score

def get_rank_from_score(score):
    """Get rank letter and name based on score"""
    if score >= 1000:
        return "S", "SHADOW MONARCH"
    elif score >= 800:
        return "A", "ELITE HUNTER"
    elif score >= 600:
        return "B", "SKILLED HUNTER"
    elif score >= 400:
        return "C", "TRAINED HUNTER"
    elif score >= 200:
        return "D", "NOVICE HUNTER"
    else:
        return "E", "AWAKENED"

def update_rank(data):
    """Update player rank based on current progress"""
    score = calculate_rank_score(data)
    rank_letter, rank_name = get_rank_from_score(score)

    data["player"]["rank"] = rank_letter
    data["player"]["rank_name"] = rank_name
    data["player"]["rank_score"] = score

    next_thresholds = [200, 400, 600, 800, 1000]
    points_to_next = None

    for threshold in next_thresholds:
        if score < threshold:
            points_to_next = threshold - score
            break

    data["player"]["points_to_next_rank"] = points_to_next

def update_class_and_title(data):
    """Update player class and title based on level and stats"""
    level = data["player"]["level"]
    stats = data["player"]["stats"]

    highest_stat = max(stats,
                       key=lambda x: stats[x]
                       if x != "available_points" else 0)

    if level >= 20:
        class_map = {
            "strength": "BERSERKER",
            "intelligence": "ARCHMAGE",
            "agility": "ASSASSIN",
            "vitality": "GUARDIAN",
            "perception": "HUNTER"
        }
        data["player"]["class"] = class_map.get(highest_stat, "WARRIOR")
    elif level >= 10:
        class_map = {
            "strength": "WARRIOR",
            "intelligence": "MAGE",
            "agility": "ROGUE",
            "vitality": "TANK",
            "perception": "SCOUT"
        }
        data["player"]["class"] = class_map.get(highest_stat, "FIGHTER")

    if data["player"]["max_streak"] >= 30:
        data["player"]["title"] = "UNSTOPPABLE"
    elif data["player"]["max_streak"] >= 14:
        data["player"]["title"] = "DEDICATED"
    elif data["player"]["level"] >= 15:
        data["player"]["title"] = "VETERAN"
    elif data["player"]["level"] >= 5:
        data["player"]["title"] = "RISING STAR"

    update_rank(data)

def check_achievements(data):
    """Check and unlock achievements"""
    achievements = data["achievements"]
    player = data["player"]

    if not achievements[0]["unlocked"] and any(
            task["completed"] for task in data["daily_tasks"]):
        achievements[0]["unlocked"] = True

    if not achievements[1]["unlocked"] and player["streak"] >= 7:
        achievements[1]["unlocked"] = True

    if not achievements[2]["unlocked"] and player["level"] >= 5:
        achievements[2]["unlocked"] = True

    completed_quests = sum(
        1 for quest in data["quests"].values()
        if isinstance(quest, dict) and quest.get("completed", False))
    if not achievements[3]["unlocked"] and completed_quests >= 5:
        achievements[3]["unlocked"] = True

    if not achievements[4]["unlocked"] and player["streak"] >= 30:
        achievements[4]["unlocked"] = True

# Authentication Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('game'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required')
            return render_template('login.html')
        
        user = users_table.search(User.email == email)
        
        if user and user[0]['password'] == hash_password(password):
            session['user_id'] = user[0]['user_id']
            session['email'] = user[0]['email']
            return redirect(url_for('game'))
        else:
            flash('Invalid email or password')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name', 'NEW HUNTER')
        
        if not email or not password:
            flash('Email and password are required')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = users_table.search(User.email == email)
        if existing_user:
            flash('Email already registered')
            return render_template('register.html')
        
        # Create new user
        user_id = generate_user_id()
        users_table.insert({
            'user_id': user_id,
            'email': email,
            'password': hash_password(password),
            'name': name,
            'created_at': datetime.now().isoformat()
        })
        
        # Create default game data
        game_data = create_default_game_data(user_id)
        game_data["player"]["name"] = name.upper()
        player_data_table.insert(game_data)
        
        session['user_id'] = user_id
        session['email'] = email
        
        flash('Registration successful!')
        return redirect(url_for('game'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/game')
@login_required
def game():
    return render_template('game.html')

# API Routes
@app.route('/api/player')
@login_required
def get_player():
    data = get_user_data(session['user_id'])
    return jsonify(data["player"])

@app.route('/api/daily-tasks')
@login_required
def get_daily_tasks():
    data = get_user_data(session['user_id'])
    total_seconds = data["timer"]["hours"] * 3600 + data["timer"]["minutes"] * 60 + data["timer"]["seconds"]
    timer_string = f"{data['timer']['hours']:02d}:{data['timer']['minutes']:02d}:{data['timer']['seconds']:02d}"

    return jsonify({
        "tasks": data["daily_tasks"],
        "timer": timer_string,
        "timer_seconds": total_seconds,
        "streak": data["player"]["streak"]
    })

@app.route('/api/inventory')
@login_required
def get_inventory():
    data = get_user_data(session['user_id'])
    return jsonify(data["inventory"])

@app.route('/api/quests')
@login_required
def get_quests():
    data = get_user_data(session['user_id'])
    return jsonify(data["quests"])

@app.route('/api/achievements')
@login_required
def get_achievements():
    data = get_user_data(session['user_id'])
    return jsonify(data["achievements"])

@app.route('/api/shop')
@login_required
def get_shop():
    data = get_user_data(session['user_id'])
    return jsonify(data["shop"])

@app.route('/api/complete-task', methods=['POST'])
@login_required
def complete_task():
    data = get_user_data(session['user_id'])
    task_index = request.json.get('task_index')
    
    if 0 <= task_index < len(data["daily_tasks"]):
        task = data["daily_tasks"][task_index]
        if not task["completed"]:
            task["completed"] = True
            task["progress"] = task["max"]

            award_experience(data, task["xp_reward"])
            data["player"]["coins"] += task["coin_reward"]

            if all(t["completed"] for t in data["daily_tasks"]):
                data["player"]["streak"] += 1
                data["player"]["max_streak"] = max(
                    data["player"]["max_streak"],
                    data["player"]["streak"])

            # Update quest progress
            if "PUSHUPS" in task["name"] or "SITUPS" in task["name"]:
                data["quests"]["strength_training"]["progress"] = min(
                    100,
                    data["quests"]["strength_training"]["progress"] + 10)
            elif "MEDITATE" in task["name"]:
                data["quests"]["spiritual_training"]["progress"] = min(
                    100,
                    data["quests"]["spiritual_training"]["progress"] + 15)
            elif "RUN" in task["name"]:
                data["quests"]["discipline"]["progress"] = min(
                    100, data["quests"]["discipline"]["progress"] + 20)

            check_achievements(data)
            save_user_data(session['user_id'], data)

    return jsonify({"success": True})

@app.route('/api/allocate-stat', methods=['POST'])
@login_required
def allocate_stat():
    data = get_user_data(session['user_id'])
    stat_name = request.json.get('stat_name')
    
    if stat_name in data["player"]["stats"] and data["player"]["stats"]["available_points"] > 0:
        data["player"]["stats"][stat_name] += 1
        data["player"]["stats"]["available_points"] -= 1

        data["player"]["physical_damage_reduction"] = int(
            data["player"]["stats"]["vitality"] * 0.5)
        data["player"]["magical_damage_reduction"] = int(
            data["player"]["stats"]["intelligence"] * 0.3)

        update_class_and_title(data)
        save_user_data(session['user_id'], data)

    return jsonify({"success": True})

@app.route('/api/buy-item', methods=['POST'])
@login_required
def buy_item():
    data = get_user_data(session['user_id'])
    item_name = request.json.get('item_name')
    shop_item = next(
        (item for item in data["shop"] if item["name"] == item_name),
        None)

    if shop_item and data["player"]["coins"] >= shop_item["price"]:
        data["player"]["coins"] -= shop_item["price"]

        if shop_item["type"] == "consumable":
            existing_item = next((item for item in data["inventory"]
                                  if item["name"] == item_name), None)
            if existing_item:
                existing_item["quantity"] += 1
            else:
                data["inventory"].append({
                    "name": item_name,
                    "quantity": 1,
                    "type": shop_item["type"],
                    "effect": shop_item["effect"]
                })
        elif shop_item["type"] == "permanent":
            if item_name == "Stat Point":
                data["player"]["stats"]["available_points"] += 1

        save_user_data(session['user_id'], data)
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Insufficient coins"})

@app.route('/api/use-item', methods=['POST'])
@login_required
def use_item():
    data = get_user_data(session['user_id'])
    item_name = request.json.get('item_name')
    item = next((item for item in data["inventory"]
                 if item["name"] == item_name and item["quantity"] > 0), None)

    if item:
        item["quantity"] -= 1
        if item["quantity"] == 0:
            data["inventory"].remove(item)

        if item_name == "Energy Drink":
            data["player"]["energy"] = min(
                data["player"]["max_energy"],
                data["player"]["energy"] + 30)

        save_user_data(session['user_id'], data)
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Item not available"})

@app.route('/api/claim-achievement', methods=['POST'])
@login_required
def claim_achievement():
    data = get_user_data(session['user_id'])
    achievement_index = request.json.get('achievement_index')
    
    if 0 <= achievement_index < len(data["achievements"]):
        achievement = data["achievements"][achievement_index]
        if achievement["unlocked"] and not achievement.get("claimed", False):
            achievement["claimed"] = True
            data["player"]["coins"] += achievement["reward_coins"]

            save_user_data(session['user_id'], data)
            return jsonify({
                "success": True,
                "coins_awarded": achievement["reward_coins"]
            })

    return jsonify({"success": False, "error": "Achievement not available"})

@app.route('/api/personal-quests')
@login_required
def get_personal_quests():
    data = get_user_data(session['user_id'])
    if "personal_quest_list" not in data:
        data["personal_quest_list"] = []
    return jsonify(data["personal_quest_list"])

@app.route('/api/add-personal-quest', methods=['POST'])
@login_required
def add_personal_quest():
    data = get_user_data(session['user_id'])
    quest_data = request.json
    quest_name = quest_data.get('name', '').strip()
    quest_description = quest_data.get('description', '').strip()

    if not quest_name:
        return jsonify({"success": False, "error": "Quest name is required"})

    if "personal_quest_list" not in data:
        data["personal_quest_list"] = []

    new_quest = {
        "id": len(data["personal_quest_list"]) + 1,
        "name": quest_name,
        "description": quest_description,
        "completed": False,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "reward_xp": 100,
        "reward_coins": 50
    }

    data["personal_quest_list"].append(new_quest)
    data["quests"]["personal_quests"] = len(
        [q for q in data["personal_quest_list"] if not q["completed"]])

    save_user_data(session['user_id'], data)
    return jsonify({"success": True, "quest": new_quest})

@app.route('/api/complete-personal-quest', methods=['POST'])
@login_required
def complete_personal_quest():
    data = get_user_data(session['user_id'])
    quest_id = request.json.get('quest_id')

    if "personal_quest_list" not in data:
        return jsonify({"success": False, "error": "No personal quests found"})

    quest = next(
        (q for q in data["personal_quest_list"] if q["id"] == quest_id),
        None)

    if not quest or quest["completed"]:
        return jsonify({"success": False, "error": "Quest not available"})

    quest["completed"] = True
    quest["completion_date"] = datetime.now().strftime("%Y-%m-%d")

    award_experience(data, quest["reward_xp"])
    data["player"]["coins"] += quest["reward_coins"]

    data["quests"]["personal_quests"] = len(
        [q for q in data["personal_quest_list"] if not q["completed"]])

    check_achievements(data)
    save_user_data(session['user_id'], data)

    return jsonify({
        "success": True,
        "rewards": {
            "xp": quest["reward_xp"],
            "coins": quest["reward_coins"]
        }
    })

@app.route('/api/delete-personal-quest', methods=['POST'])
@login_required
def delete_personal_quest():
    data = get_user_data(session['user_id'])
    quest_id = request.json.get('quest_id')

    if "personal_quest_list" not in data:
        return jsonify({"success": False, "error": "No personal quests found"})

    quest_index = next((i
                        for i, q in enumerate(data["personal_quest_list"])
                        if q["id"] == quest_id), None)

    if quest_index is None:
        return jsonify({"success": False, "error": "Quest not found"})

    data["personal_quest_list"].pop(quest_index)
    data["quests"]["personal_quests"] = len(
        [q for q in data["personal_quest_list"] if not q["completed"]])

    save_user_data(session['user_id'], data)
    return jsonify({"success": True})

@app.route('/api/complete-quest', methods=['POST'])
@login_required
def complete_quest():
    data = get_user_data(session['user_id'])
    quest_name = request.json.get('quest_name')

    if quest_name in data["quests"] and isinstance(data["quests"][quest_name], dict):
        quest = data["quests"][quest_name]
        if quest["progress"] >= quest["max"] and not quest["completed"]:
            quest["completed"] = True

            award_experience(data, quest["reward_xp"])
            data["player"]["coins"] += quest["reward_coins"]

            check_achievements(data)
            save_user_data(session['user_id'], data)

            return jsonify({
                "success": True,
                "rewards": {
                    "xp": quest["reward_xp"],
                    "coins": quest["reward_coins"]
                }
            })

    return jsonify({"success": False, "error": "Quest not ready for completion"})

@app.route('/api/leaderboard')
@login_required
def get_leaderboard():
    # Get all player data
    all_player_data = player_data_table.all()
    
    # Create leaderboard entries
    leaderboard_players = []
    current_user_data = get_user_data(session['user_id'])
    
    for data in all_player_data:
        if "player" in data:
            player = data["player"]
            rank_score = calculate_rank_score(data)
            
            leaderboard_players.append({
                "name": player["name"],
                "level": player["level"],
                "total_experience": player["total_experience"],
                "rank": player.get("rank", "E"),
                "class": player.get("class", "BEGINNER"),
                "max_streak": player["max_streak"],
                "rank_score": rank_score
            })

    # Sort by total experience
    leaderboard_players.sort(key=lambda x: x["total_experience"], reverse=True)

    # Add positions
    for i, player in enumerate(leaderboard_players):
        player["position"] = i + 1

    # Find current player position
    current_player_position = next(
        (p["position"] for p in leaderboard_players 
         if p["name"] == current_user_data["player"]["name"]), 1)

    return jsonify({
        "players": leaderboard_players[:10],
        "current_player_position": current_player_position,
        "total_players": len(leaderboard_players)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
