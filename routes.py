from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, PlayerData, DailyTask, Quest, InventoryItem, ShopItem, Achievement, PersonalQuest
from game_logic import GameLogic
from datetime import datetime, timedelta
import logging

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('game'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('game'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User()
        user.email = email
        user.name = name
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default player data
        GameLogic.create_default_player_data(user)
        GameLogic.create_daily_tasks(user)
        GameLogic.initialize_shop()
        
        session['user_id'] = user.id
        session['user_name'] = user.name
        flash('Registration successful! Welcome to Solo Leveler!', 'success')
        return redirect(url_for('game'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/game')
def game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    # Check for daily reset
    GameLogic.check_daily_reset(user)
    
    return render_template('game.html', user=user)

# API Routes

@app.route('/api/player')
def api_player():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    player = PlayerData.query.filter_by(user_id=user.id).first()
    if not user or not player:
        return jsonify({'error': 'Player data not found'}), 404
    return jsonify({
        'name': player.name,
        'level': player.level,
        'current_xp': player.current_xp,
        'xp_to_next_level': player.xp_to_next_level,
        'total_experience': player.total_experience,
        'class': player.player_class,
        'title': player.title,
        'rank': player.rank,
        'rank_name': player.rank_name,
        'rank_score': player.rank_score,
        'coins': player.coins,
        'energy': player.energy,
        'max_energy': player.max_energy,
        'stats': player.get_stats_dict(),
        'physical_damage_reduction': player.physical_damage_reduction,
        'magical_damage_reduction': player.magical_damage_reduction
    })

@app.route('/api/daily-tasks')
def api_daily_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    today = datetime.utcnow().date()
    tasks = DailyTask.query.filter_by(user_id=user.id, task_date=today).all()
    
    task_data = []
    for task in tasks:
        task_data.append({
            'id': task.id,
            'name': task.name,
            'progress': task.progress,
            'max': task.max_progress,
            'completed': task.completed,
            'xp_reward': task.xp_reward,
            'coin_reward': task.coin_reward
        })
    
    player_data = PlayerData.query.filter_by(user_id=user.id).first()
    return jsonify({
        'tasks': task_data,
        'streak': player_data.daily_streak if player_data else 0
    })

@app.route('/api/complete-task/<int:task_id>', methods=['POST'])
def api_complete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    task = DailyTask.query.filter_by(id=task_id, user_id=user.id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if task.completed:
        return jsonify({'error': 'Task already completed'}), 400
    
    task.completed = True
    task.progress = task.max_progress
    
    # Add rewards and check for level up
    player_data = PlayerData.query.filter_by(user_id=user.id).first()
    if not player_data:
        return jsonify({'error': 'Player data not found'}), 404
    
    old_level = player_data.level
    player_data.coins += task.coin_reward
    GameLogic.add_xp(player_data, task.xp_reward)
    new_level = player_data.level
    
    db.session.commit()
    
    # Check if player leveled up
    level_up = new_level > old_level
    
    response_data = {
        'success': True, 
        'message': f'Task completed! +{task.xp_reward} XP, +{task.coin_reward} coins',
        'level_up': level_up
    }
    
    if level_up:
        response_data['new_level'] = new_level
    
    return jsonify(response_data)

@app.route('/api/quests')
def api_quests():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    quests = Quest.query.filter_by(user_id=user.id).all()
    
    quest_data = {}
    for quest in quests:
        quest_data[quest.quest_type] = {
            'progress': quest.progress,
            'max': quest.max_progress,
            'completed': quest.completed,
            'xp_reward': quest.xp_reward,
            'coin_reward': quest.coin_reward
        }
    
    return jsonify(quest_data)

@app.route('/api/complete-quest/<quest_type>', methods=['POST'])
def api_complete_quest(quest_type):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    quest = Quest.query.filter_by(user_id=user.id, quest_type=quest_type).first()
    
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    
    if quest.progress < quest.max_progress:
        return jsonify({'error': 'Quest not ready to complete'}), 400
    
    if quest.completed:
        return jsonify({'error': 'Quest already completed'}), 400
    
    quest.completed = True
    
    # Add rewards
    player_data = user.player_data
    player_data.coins += quest.coin_reward
    GameLogic.add_xp(player_data, quest.xp_reward)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Quest completed! +{quest.xp_reward} XP, +{quest.coin_reward} coins'})

@app.route('/api/increment-quest/<quest_type>', methods=['POST'])
def api_increment_quest(quest_type):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    quest = Quest.query.filter_by(user_id=user.id, quest_type=quest_type).first()
    
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    
    if quest.completed:
        return jsonify({'error': 'Quest already completed'}), 400
    
    amount = request.json.get('amount', 1) if request.is_json else 1
    quest.progress = min(quest.progress + amount, quest.max_progress)
    
    db.session.commit()
    
    return jsonify({'success': True, 'progress': quest.progress})

@app.route('/api/allocate-stat/<stat_name>', methods=['POST'])
def api_allocate_stat(stat_name):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    player_data = user.player_data
    
    if player_data.available_points <= 0:
        return jsonify({'error': 'No available stat points'}), 400
    
    valid_stats = ['strength', 'vitality', 'agility', 'intelligence', 'perception']
    if stat_name not in valid_stats:
        return jsonify({'error': 'Invalid stat name'}), 400
    
    # Allocate stat point
    current_value = getattr(player_data, stat_name)
    setattr(player_data, stat_name, current_value + 1)
    player_data.available_points -= 1
    
    # Update rank
    GameLogic.update_rank(player_data)
    
    db.session.commit()
    
    return jsonify({'success': True, 'new_value': current_value + 1})

@app.route('/api/inventory')
def api_inventory():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    items = InventoryItem.query.filter_by(user_id=user.id).all()
    
    inventory_data = []
    for item in items:
        inventory_data.append({
            'id': item.id,
            'name': item.name,
            'type': item.item_type,
            'quantity': item.quantity,
            'effect': item.effect,
            'value': item.value
        })
    
    return jsonify(inventory_data)

@app.route('/api/use-item/<item_name>', methods=['POST'])
def api_use_item(item_name):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    item = InventoryItem.query.filter_by(user_id=user.id, name=item_name).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    if item.quantity <= 0:
        return jsonify({'error': 'No items left to use'}), 400
    
    player_data = user.player_data
    
    # Apply item effects based on item name
    if 'Health Potion' in item.name:
        player_data.energy = min(player_data.energy + 25, player_data.max_energy)
        message = 'Health restored!'
    elif 'Energy Drink' in item.name:
        player_data.energy = min(player_data.energy + 15, player_data.max_energy)
        message = 'Energy restored!'
    elif 'Strength Elixir' in item.name:
        player_data.strength += 1
        message = 'Strength permanently increased!'
    else:
        message = 'Item used!'
    
    # Decrease quantity
    item.quantity -= 1
    if item.quantity <= 0:
        db.session.delete(item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': message})

@app.route('/api/shop')
def api_shop():
    items = ShopItem.query.all()
    shop_data = []
    for item in items:
        shop_data.append({
            'id': item.id,
            'name': item.name,
            'type': item.item_type,
            'price': item.price,
            'effect': item.effect,
            'description': item.description
        })
    
    return jsonify(shop_data)

@app.route('/api/buy-item/<int:item_id>', methods=['POST'])
def api_buy_item(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    shop_item = ShopItem.query.get(item_id)
    
    if not shop_item:
        return jsonify({'error': 'Item not found'}), 404
    
    player_data = user.player_data
    if player_data.coins < shop_item.price:
        return jsonify({'error': 'Insufficient coins'}), 400
    
    # Deduct coins
    player_data.coins -= shop_item.price
    
    # Add to inventory
    existing_item = InventoryItem.query.filter_by(
        user_id=user.id, 
        name=shop_item.name
    ).first()
    
    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = InventoryItem()
        new_item.user_id = user.id
        new_item.name = shop_item.name
        new_item.item_type = shop_item.item_type
        new_item.quantity = 1
        new_item.effect = shop_item.effect
        new_item.value = shop_item.price
        db.session.add(new_item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'{shop_item.name} purchased!'})

@app.route('/api/achievements')
def api_achievements():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    achievements = Achievement.query.filter_by(user_id=user.id).all()
    
    achievement_data = []
    for achievement in achievements:
        achievement_data.append({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'unlocked': achievement.unlocked,
            'claimed': achievement.claimed,
            'unlock_date': achievement.unlock_date.isoformat() if achievement.unlock_date else None,
            'reward_xp': achievement.reward_xp,
            'reward_coins': achievement.reward_coins
        })
    
    return jsonify(achievement_data)

@app.route('/api/claim-achievement/<int:achievement_id>', methods=['POST'])
def api_claim_achievement(achievement_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    achievement = Achievement.query.filter_by(id=achievement_id, user_id=user.id).first()
    
    if not achievement:
        return jsonify({'error': 'Achievement not found'}), 404
    
    if not achievement.unlocked:
        return jsonify({'error': 'Achievement not unlocked yet'}), 400
    
    if achievement.claimed:
        return jsonify({'error': 'Achievement already claimed'}), 400
    
    # Claim the achievement
    achievement.claimed = True
    
    # Add rewards to player
    player_data = PlayerData.query.filter_by(user_id=user.id).first()
    if not player_data:
        return jsonify({'error': 'Player data not found'}), 404
    
    player_data.coins += achievement.reward_coins
    GameLogic.add_xp(player_data, achievement.reward_xp)
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'Achievement claimed! +{achievement.reward_xp} XP, +{achievement.reward_coins} coins'
    })

@app.route('/api/personal-quests')
def api_personal_quests():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    quests = PersonalQuest.query.filter_by(user_id=user.id).order_by(PersonalQuest.created_date.desc()).all()
    
    quest_data = []
    for quest in quests:
        quest_data.append({
            'id': quest.id,
            'name': quest.name,
            'description': quest.description,
            'completed': quest.completed,
            'reward_xp': quest.reward_xp,
            'reward_coins': quest.reward_coins,
            'created_date': quest.created_date.strftime('%Y-%m-%d')
        })
    
    return jsonify(quest_data)

@app.route('/api/add-personal-quest', methods=['POST'])
def api_add_personal_quest():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    data = request.get_json()
    
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    if not name:
        return jsonify({'error': 'Quest name is required'}), 400
    
    # Check if user already has too many personal quests
    quest_count = PersonalQuest.query.filter_by(user_id=user.id, completed=False).count()
    if quest_count >= 10:
        return jsonify({'error': 'You can only have 10 active personal quests'}), 400
    
    quest = PersonalQuest()
    quest.user_id = user.id
    quest.name = name
    quest.description = description
    quest.completed = False
    quest.reward_xp = 50
    quest.reward_coins = 25
    
    db.session.add(quest)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Personal quest added!'})

@app.route('/api/complete-personal-quest/<int:quest_id>', methods=['POST'])
def api_complete_personal_quest(quest_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    quest = PersonalQuest.query.filter_by(id=quest_id, user_id=user.id).first()
    
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    
    if quest.completed:
        return jsonify({'error': 'Quest already completed'}), 400
    
    quest.completed = True
    
    # Add rewards and check for level up
    player_data = PlayerData.query.filter_by(user_id=user.id).first()
    if not player_data:
        return jsonify({'error': 'Player data not found'}), 404
    
    old_level = player_data.level
    player_data.coins += quest.reward_coins
    GameLogic.add_xp(player_data, quest.reward_xp)
    new_level = player_data.level
    
    db.session.commit()
    
    # Check if player leveled up
    level_up = new_level > old_level
    
    response_data = {
        'success': True, 
        'message': f'Quest completed! +{quest.reward_xp} XP, +{quest.reward_coins} coins',
        'level_up': level_up
    }
    
    if level_up:
        response_data['new_level'] = new_level
    
    return jsonify(response_data)

@app.route('/api/delete-personal-quest/<int:quest_id>', methods=['DELETE'])
def api_delete_personal_quest(quest_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    quest = PersonalQuest.query.filter_by(id=quest_id, user_id=user.id).first()
    
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    
    db.session.delete(quest)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Quest deleted!'})

@app.route('/api/leaderboard')
def api_leaderboard():
    # Get top players by rank score
    top_players = db.session.query(PlayerData).order_by(
        PlayerData.rank_score.desc(), 
        PlayerData.level.desc()
    ).limit(50).all()
    
    leaderboard_data = []
    for i, player in enumerate(top_players):
        leaderboard_data.append({
            'position': i + 1,
            'name': player.name,
            'level': player.level,
            'rank': player.rank,
            'rank_name': player.rank_name,
            'rank_score': player.rank_score,
            'daily_streak': player.daily_streak,
            'is_top_three': i < 3
        })
    
    # Get current user's rank
    current_rank = 1
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.player_data:
            better_players = db.session.query(PlayerData).filter(
                PlayerData.rank_score > user.player_data.rank_score
            ).count()
            current_rank = better_players + 1
    
    total_players = PlayerData.query.count()
    
    return jsonify({
        'leaderboard': leaderboard_data,
        'current_rank': current_rank,
        'total_players': total_players
    })

@app.route('/api/time-remaining')
def api_time_remaining():
    now = datetime.utcnow()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    remaining = tomorrow - now
    
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    seconds = remaining.seconds % 60
    
    return jsonify({
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'total_seconds': remaining.total_seconds()
    })
