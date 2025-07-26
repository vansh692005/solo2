from datetime import datetime, timedelta
from app import db
from models import User, PlayerData, DailyTask, Quest, InventoryItem, ShopItem, Achievement, PersonalQuest
import random

class GameLogic:
    
    @staticmethod
    def create_default_player_data(user):
        """Create default player data for a new user"""
        player_data = PlayerData()
        player_data.user_id = user.id
        player_data.name = user.name.upper()
        player_data.level = 1
        player_data.current_xp = 0
        player_data.xp_to_next_level = 100
        player_data.total_experience = 0
        player_data.player_class = 'BEGINNER'
        player_data.title = 'NEWBIE'
        player_data.rank = 'E'
        player_data.rank_name = 'AWAKENED'
        player_data.rank_score = 0
        player_data.coins = 100
        player_data.energy = 100
        player_data.max_energy = 100
        player_data.strength = 10
        player_data.vitality = 10
        player_data.agility = 10
        player_data.intelligence = 10
        player_data.perception = 10
        player_data.available_points = 0
        player_data.physical_damage_reduction = 5
        player_data.magical_damage_reduction = 3
        player_data.daily_streak = 0
        player_data.max_streak = 0
        player_data.last_daily_reset = datetime.utcnow()
        db.session.add(player_data)
        
        # Create default quests
        quest_types = [
            ('strength_training', 100, 200, 100),
            ('intelligence', 100, 200, 100),
            ('discipline', 100, 250, 150),
            ('spiritual_training', 100, 220, 120),
            ('secret_quests', 100, 1000, 500)
        ]
        
        for quest_type, max_prog, xp_reward, coin_reward in quest_types:
            quest = Quest()
            quest.user_id = user.id
            quest.quest_type = quest_type
            quest.progress = 0
            quest.max_progress = max_prog
            quest.completed = False
            quest.xp_reward = xp_reward
            quest.coin_reward = coin_reward
            db.session.add(quest)
        
        # Create default achievements
        achievements = [
            ('First Steps', 'Complete your first daily task', False, 50, 25),
            ('Dedication', 'Maintain a 7-day streak', False, 200, 100),
            ('Warrior', 'Reach level 10', False, 500, 250),
            ('Master', 'Reach level 25', False, 1000, 500),
            ('Legend', 'Reach level 50', False, 2500, 1000)
        ]
        
        for name, desc, unlocked, xp, coins in achievements:
            achievement = Achievement()
            achievement.user_id = user.id
            achievement.name = name
            achievement.description = desc
            achievement.unlocked = unlocked
            achievement.reward_xp = xp
            achievement.reward_coins = coins
            db.session.add(achievement)
        
        db.session.commit()
        return player_data
    
    @staticmethod
    def create_daily_tasks(user):
        """Create daily tasks for a user with progressive difficulty"""
        # Clear existing tasks for today
        today = datetime.utcnow().date()
        DailyTask.query.filter_by(user_id=user.id, task_date=today).delete()
        
        # Get player streak for progressive difficulty
        player_data = user.player_data
        streak = player_data.daily_streak if player_data else 0
        
        # Calculate progressive numbers (add 2 more each day for pushups/situps)
        pushup_count = 12 + (streak * 2)
        situp_count = 12 + (streak * 2)
        
        # Fixed daily tasks with progressive difficulty
        task_templates = [
            (f'{pushup_count} PUSHUPS', pushup_count, 25, 10),
            (f'{situp_count} SITUPS', situp_count, 25, 10),
            ('2KM OUTDOOR RUN', 2, 50, 20),
            ('MEDITATE 15 MIN', 15, 30, 15)
        ]
        
        for name, max_prog, xp, coins in task_templates:
            task = DailyTask()
            task.user_id = user.id
            task.name = name
            task.progress = 0
            task.max_progress = max_prog
            task.completed = False
            task.xp_reward = xp
            task.coin_reward = coins
            task.task_date = today
            db.session.add(task)
        
        db.session.commit()
    
    @staticmethod
    def check_daily_reset(user):
        """Check if daily tasks need to be reset"""
        player_data = user.player_data
        if not player_data:
            return
        
        now = datetime.utcnow()
        last_reset = player_data.last_daily_reset
        
        # Check if it's a new day
        if last_reset.date() < now.date():
            # Check if all tasks were completed yesterday
            yesterday = (now - timedelta(days=1)).date()
            yesterday_tasks = DailyTask.query.filter_by(
                user_id=user.id, 
                task_date=yesterday
            ).all()
            
            all_completed = all(task.completed for task in yesterday_tasks) if yesterday_tasks else False
            
            if all_completed:
                player_data.daily_streak += 1
                if player_data.daily_streak > player_data.max_streak:
                    player_data.max_streak = player_data.daily_streak
            else:
                player_data.daily_streak = 0
            
            player_data.last_daily_reset = now
            GameLogic.create_daily_tasks(user)
            db.session.commit()
    
    @staticmethod
    def add_xp(player_data, xp_amount):
        """Add XP and handle level ups"""
        player_data.current_xp += xp_amount
        player_data.total_experience += xp_amount
        
        # Check for level up
        while player_data.current_xp >= player_data.xp_to_next_level:
            player_data.current_xp -= player_data.xp_to_next_level
            player_data.level += 1
            player_data.available_points += 2  # 2 stat points per level
            
            # Increase XP requirement for next level
            player_data.xp_to_next_level = int(player_data.xp_to_next_level * 1.1)
            
            # Update rank based on level
            GameLogic.update_rank(player_data)
        
        db.session.commit()
    
    @staticmethod
    def update_rank(player_data):
        """Update player rank based on level and stats"""
        level = player_data.level
        total_stats = (player_data.strength + player_data.vitality + 
                      player_data.agility + player_data.intelligence + 
                      player_data.perception)
        
        rank_score = level * 10 + total_stats + player_data.daily_streak
        player_data.rank_score = rank_score
        
        if rank_score < 100:
            player_data.rank = 'E'
            player_data.rank_name = 'AWAKENED'
        elif rank_score < 250:
            player_data.rank = 'D'
            player_data.rank_name = 'HUNTER'
        elif rank_score < 500:
            player_data.rank = 'C'
            player_data.rank_name = 'ELITE'
        elif rank_score < 1000:
            player_data.rank = 'B'
            player_data.rank_name = 'VETERAN'
        elif rank_score < 2000:
            player_data.rank = 'A'
            player_data.rank_name = 'EXPERT'
        else:
            player_data.rank = 'S'
            player_data.rank_name = 'LEGEND'
    
    @staticmethod
    def initialize_shop():
        """Initialize shop items if they don't exist"""
        if ShopItem.query.count() == 0:
            shop_items = [
                ('Health Potion', 'consumable', 50, 'Restores 25 energy', 'A basic healing potion'),
                ('XP Booster', 'booster', 100, 'Doubles XP gain for 1 hour', 'Temporary XP boost'),
                ('Strength Elixir', 'consumable', 200, 'Permanently increases STR by 1', 'Rare strength enhancement'),
                ('Energy Drink', 'consumable', 30, 'Restores 15 energy', 'Quick energy restoration'),
                ('Focus Pills', 'consumable', 80, 'Increases INT by 2 for 1 day', 'Temporary intelligence boost'),
                ('Stamina Supplement', 'consumable', 120, 'Increases max energy by 10', 'Permanent energy increase')
            ]
            
            for name, item_type, price, effect, desc in shop_items:
                item = ShopItem()
                item.name = name
                item.item_type = item_type
                item.price = price
                item.effect = effect
                item.description = desc
                db.session.add(item)
            
            db.session.commit()
