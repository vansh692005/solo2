from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    player_data = db.relationship('PlayerData', backref='user', uselist=False, cascade='all, delete-orphan', lazy='select')
    daily_tasks = db.relationship('DailyTask', backref='user', cascade='all, delete-orphan')
    quests = db.relationship('Quest', backref='user', cascade='all, delete-orphan')
    inventory_items = db.relationship('InventoryItem', backref='user', cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='user', cascade='all, delete-orphan')
    personal_quests = db.relationship('PersonalQuest', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PlayerData(db.Model):
    __tablename__ = 'player_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic player info
    name = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Integer, default=1)
    current_xp = db.Column(db.Integer, default=0)
    xp_to_next_level = db.Column(db.Integer, default=100)
    total_experience = db.Column(db.Integer, default=0)
    
    # Character attributes
    player_class = db.Column(db.String(50), default='BEGINNER')
    title = db.Column(db.String(50), default='NEWBIE')
    rank = db.Column(db.String(10), default='E')
    rank_name = db.Column(db.String(50), default='AWAKENED')
    rank_score = db.Column(db.Integer, default=0)
    
    # Resources
    coins = db.Column(db.Integer, default=100)
    energy = db.Column(db.Integer, default=100)
    max_energy = db.Column(db.Integer, default=100)
    
    # Stats
    strength = db.Column(db.Integer, default=10)
    vitality = db.Column(db.Integer, default=10)
    agility = db.Column(db.Integer, default=10)
    intelligence = db.Column(db.Integer, default=10)
    perception = db.Column(db.Integer, default=10)
    available_points = db.Column(db.Integer, default=0)
    
    # Damage reductions
    physical_damage_reduction = db.Column(db.Integer, default=5)
    magical_damage_reduction = db.Column(db.Integer, default=3)
    
    # Streaks and progress
    daily_streak = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)
    last_daily_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_stats_dict(self):
        return {
            'strength': self.strength,
            'vitality': self.vitality,
            'agility': self.agility,
            'intelligence': self.intelligence,
            'perception': self.perception,
            'available_points': self.available_points
        }

class DailyTask(db.Model):
    __tablename__ = 'daily_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    progress = db.Column(db.Integer, default=0)
    max_progress = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)
    xp_reward = db.Column(db.Integer, default=20)
    coin_reward = db.Column(db.Integer, default=10)
    task_date = db.Column(db.Date, default=datetime.utcnow().date)

class Quest(db.Model):
    __tablename__ = 'quests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    quest_type = db.Column(db.String(50), nullable=False)  # strength_training, intelligence, etc.
    progress = db.Column(db.Integer, default=0)
    max_progress = db.Column(db.Integer, default=100)
    completed = db.Column(db.Boolean, default=False)
    xp_reward = db.Column(db.Integer, default=200)
    coin_reward = db.Column(db.Integer, default=100)

class PersonalQuest(db.Model):
    __tablename__ = 'personal_quests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    reward_xp = db.Column(db.Integer, default=50)
    reward_coins = db.Column(db.Integer, default=25)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # consumable, equipment, etc.
    quantity = db.Column(db.Integer, default=1)
    effect = db.Column(db.String(200))
    value = db.Column(db.Integer, default=0)

class ShopItem(db.Model):
    __tablename__ = 'shop_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    effect = db.Column(db.String(200))
    description = db.Column(db.Text)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unlocked = db.Column(db.Boolean, default=False)
    claimed = db.Column(db.Boolean, default=False)
    unlock_date = db.Column(db.DateTime)
    reward_xp = db.Column(db.Integer, default=0)
    reward_coins = db.Column(db.Integer, default=0)
