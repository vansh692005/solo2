# Solo Leveler Game - Replit Guide

## Overview

This is a Flask-based web game inspired by the "Solo Leveling" universe. It's a gamified personal development application where users create accounts, complete daily tasks, level up their characters, and progress through various quests and challenges. The app uses a PostgreSQL database with SQLAlchemy ORM and features a modern, game-themed UI.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Database**: PostgreSQL (configured but can be adapted to other databases)
- **Authentication**: Session-based authentication with password hashing using Werkzeug
- **Application Structure**: Modular design with separate files for models, routes, and game logic

### Frontend Architecture
- **Templates**: Jinja2 templating engine with HTML templates
- **Styling**: Custom CSS with gaming theme and animations
- **JavaScript**: Vanilla JavaScript for interactive game features
- **UI Theme**: Dark, futuristic gaming interface with progress bars, notifications, and responsive design

### Database Schema
The application uses several interconnected models:
- **User**: Core user authentication and profile data
- **PlayerData**: Game character stats, levels, experience, and resources
- **DailyTask**: Daily challenges and tasks for users
- **Quest**: Game progression quests with different types
- **InventoryItem**: User's game items and equipment
- **Achievement**: User accomplishments and milestones
- **PersonalQuest**: Custom user-created quests
- **ShopItem**: In-game store items

## Key Components

### Authentication System
- User registration and login with email/password
- Password hashing using Werkzeug security functions
- Session management for maintaining user state
- Protected routes requiring authentication

### Game Logic Engine
- Character progression system with experience points and levels
- Daily task management with streak tracking
- Quest system with multiple quest types
- Resource management (coins, energy, stats)
- Achievement tracking and rewards

### API Endpoints
- RESTful API structure for game data operations
- JSON responses for frontend interactions
- Player data management endpoints
- Task completion and progress tracking

### User Interface
- Multi-screen game interface (daily tasks, quests, inventory, etc.)
- Real-time updates using JavaScript
- Progress bars and visual feedback
- Notification system for user actions

## Data Flow

1. **User Registration/Login**: User creates account → Password hashed and stored → Session created
2. **Game Initialization**: User logs in → Player data loaded → Default game data created if new user
3. **Daily Tasks**: User completes tasks → Progress updated in database → Experience and rewards awarded
4. **Character Progression**: Experience gained → Level calculations → Stats and abilities updated
5. **Quest Management**: User selects quests → Progress tracked → Completion rewards processed

## External Dependencies

### Python Packages
- **Flask**: Web framework for routing and request handling
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: Security utilities for password hashing and middleware
- **Gunicorn**: WSGI server for production deployment

### Frontend Assets
- **Google Fonts**: Orbitron font family for futuristic styling
- **Custom CSS**: Gaming-themed styling with animations and responsive design
- **Vanilla JavaScript**: Client-side game logic and API interactions

## Deployment Strategy

### Production Configuration
- **WSGI Server**: Gunicorn configured via Procfile
- **Database**: PostgreSQL with connection pooling and health checks
- **Environment Variables**: Secret keys and database URLs configured via environment
- **Static Files**: CSS and JavaScript served through Flask's static file handling

### Database Management
- **Connection Pooling**: Configured for production with pool recycling
- **Health Checks**: Database ping functionality to ensure connection stability
- **Auto-Migration**: Tables created automatically on application startup

### Security Considerations
- Session secret keys from environment variables
- Password hashing with salt
- Proxy middleware configuration for deployment behind load balancers
- SQL injection protection through SQLAlchemy ORM

## Development Notes

The application follows a modular structure where:
- `app.py` handles Flask application setup and database configuration
- `models.py` defines all database models and relationships
- `routes.py` contains all web routes and API endpoints
- `game_logic.py` implements core game mechanics and calculations
- `main.py` serves as the application entry point

The frontend uses a single-page application approach with JavaScript managing screen transitions and real-time updates, while maintaining server-side rendering for initial page loads and SEO benefits.