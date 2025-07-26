class Game {
    constructor() {
        this.playerData = null;
        this.dailyTasks = null;
        this.inventory = null;
        this.quests = null;
        this.achievements = null;
        this.shop = null;
        this.personalQuests = null;
        this.timerInterval = null;

        this.init();
    }

    async init() {
        try {
            await this.loadAllData();
            this.setupEventListeners();
            this.startTimer();
            this.showNotification('Welcome back, Hunter!');
        } catch (error) {
            console.error('Failed to initialize game:', error);
            this.showNotification('Failed to load game data', 'error');
        }
    }

    async loadAllData() {
        const promises = [
            this.loadPlayer(),
            this.loadDailyTasks(),
            this.loadInventory(),
            this.loadQuests(),
            this.loadAchievements(),
            this.loadShop(),
            this.loadPersonalQuests()
        ];

        await Promise.all(promises);
    }

    async loadPlayer() {
        try {
            const response = await fetch('/api/player');
            this.playerData = await response.json();
            this.updatePlayerDisplay();
        } catch (error) {
            console.error('Failed to load player data:', error);
        }
    }

    async loadDailyTasks() {
        try {
            const response = await fetch('/api/daily-tasks');
            this.dailyTasks = await response.json();
            this.updateDailyTasksDisplay();
        } catch (error) {
            console.error('Failed to load daily tasks:', error);
        }
    }

    async loadInventory() {
        try {
            const response = await fetch('/api/inventory');
            this.inventory = await response.json();
            this.updateInventoryDisplay();
        } catch (error) {
            console.error('Failed to load inventory:', error);
        }
    }

    async loadQuests() {
        try {
            const response = await fetch('/api/quests');
            this.quests = await response.json();
            this.updateQuestsDisplay();
        } catch (error) {
            console.error('Failed to load quests:', error);
        }
    }

    async loadAchievements() {
        try {
            const response = await fetch('/api/achievements');
            this.achievements = await response.json();
            this.updateAchievementsDisplay();
        } catch (error) {
            console.error('Failed to load achievements:', error);
        }
    }

    async loadShop() {
        try {
            const response = await fetch('/api/shop');
            this.shop = await response.json();
            this.updateShopDisplay();
        } catch (error) {
            console.error('Failed to load shop:', error);
        }
    }

    async loadPersonalQuests() {
        try {
            const response = await fetch('/api/personal-quests');
            this.personalQuests = await response.json();
            this.updatePersonalQuestsDisplay();
        } catch (error) {
            console.error('Failed to load personal quests:', error);
        }
    }

    updatePlayerDisplay() {
        if (!this.playerData) return;

        // Update header
        document.getElementById('playerLevel').textContent = this.playerData.level;
        document.getElementById('playerName').textContent = this.playerData.name;
        document.getElementById('playerCoins').textContent = this.playerData.coins;
        document.getElementById('playerEnergy').textContent = `${this.playerData.energy}/${this.playerData.max_energy}`;

        // Update XP bar
        const xpProgress = document.getElementById('xpProgress');
        const xpText = document.getElementById('xpText');
        const xpPercentage = (this.playerData.current_xp / this.playerData.xp_to_next_level) * 100;

        if (xpProgress) xpProgress.style.width = `${xpPercentage}%`;
        if (xpText) xpText.textContent = `${this.playerData.current_xp}/${this.playerData.xp_to_next_level}`;

        // Update status screen
        document.getElementById('statusPlayerName').textContent = this.playerData.name;
        document.getElementById('playerClass').textContent = this.playerData.class;
        document.getElementById('playerTitle').textContent = this.playerData.title;
        document.getElementById('playerRank').textContent = this.playerData.rank;

        this.updateStatsDisplay();
        this.updateRankDisplay();
    }

    updateStatsDisplay() {
        if (!this.playerData) return;

        const stats = this.playerData.stats;
        const statElements = document.querySelectorAll('.stat .stat-name');
        const pointsNumber = document.querySelector('.points-number');

        statElements.forEach(element => {
            const text = element.textContent;
            if (text.includes('STR')) element.textContent = `STR : ${stats.strength}`;
            else if (text.includes('VIT')) element.textContent = `VIT : ${stats.vitality}`;
            else if (text.includes('AGI')) element.textContent = `AGI : ${stats.agility}`;
            else if (text.includes('INT')) element.textContent = `INT : ${stats.intelligence}`;
            else if (text.includes('PER')) element.textContent = `PER : ${stats.perception}`;
        });

        if (pointsNumber) pointsNumber.textContent = stats.available_points;
    }

    updateRankDisplay() {
        if (!this.playerData) return;

        const rankBadge = document.querySelector('.rank-badge');
        const rankName = document.getElementById('rankName');
        const rankScore = document.getElementById('rankScore');

        if (rankBadge) {
            rankBadge.textContent = this.playerData.rank || 'E';
            rankBadge.className = `rank-badge rank-${(this.playerData.rank || 'E').toLowerCase()}`;
        }

        // Update stats grid with rank effects
        const statsGrid = document.querySelector('.stats-grid');
        if (statsGrid) {
            statsGrid.className = `stats-grid rank-${(this.playerData.rank || 'E').toLowerCase()}`;
        }

        if (rankName) rankName.textContent = this.playerData.rank_name || 'AWAKENED';
        if (rankScore) rankScore.textContent = this.playerData.rank_score || 0;

        // Update additional stats
        document.getElementById('physicalReduction').textContent = `${this.playerData.physical_damage_reduction || 0}%`;
        document.getElementById('magicalReduction').textContent = `${this.playerData.magical_damage_reduction || 0}%`;
        document.getElementById('totalExperience').textContent = this.playerData.total_experience || 0;
    }

    updateDailyTasksDisplay() {
        if (!this.dailyTasks) return;

        const taskList = document.getElementById('taskList');
        const streakNumber = document.getElementById('streakNumber');

        if (streakNumber) streakNumber.textContent = this.dailyTasks.streak;

        if (taskList) {
            taskList.innerHTML = '';
            this.dailyTasks.tasks.forEach((task, index) => {
                const taskElement = document.createElement('div');
                taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;

                taskElement.innerHTML = `
                    <div class="task-checkbox ${task.completed ? 'checked' : ''}" onclick="game.completeTask(${index})">
                        ${task.completed ? '✓' : ''}
                    </div>
                    <div class="task-name">${task.name}</div>
                    <div class="task-progress">${task.progress}/${task.max}</div>
                    <div class="task-reward">+${task.xp_reward} XP +${task.coin_reward} 💰</div>
                `;

                taskList.appendChild(taskElement);
            });
        }
    }

    updateInventoryDisplay() {
        if (!this.inventory) return;

        const inventoryGrid = document.getElementById('inventoryGrid');
        if (!inventoryGrid) return;

        inventoryGrid.innerHTML = '';

        if (this.inventory.length === 0) {
            inventoryGrid.innerHTML = '<div class="empty-message">Your inventory is empty</div>';
            return;
        }

        this.inventory.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'inventory-item';

            const icon = item.type === 'consumable' ? '🧪' : '📦';

            itemElement.innerHTML = `
                <div class="item-icon">${icon}</div>
                <div class="item-name">${item.name}</div>
                <div class="item-quantity">Quantity: ${item.quantity}</div>
                <div class="item-effect">${item.effect}</div>
                <button class="use-btn" onclick="game.useItem('${item.name}')">USE</button>
            `;

            inventoryGrid.appendChild(itemElement);
        });
    }

    updateQuestsDisplay() {
        if (!this.quests) return;

        const questCards = {
            'strength_training': 'strengthQuest',
            'intelligence': 'intelligenceQuest',
            'discipline': 'disciplineQuest',
            'spiritual_training': 'spiritualQuest',
            'secret_quests': 'secretQuest'
        };

        Object.keys(questCards).forEach(questName => {
            const quest = this.quests[questName];
            const card = document.getElementById(questCards[questName]);

            if (card && quest && typeof quest === 'object') {
                const progressBar = card.querySelector('.progress');
                const questCount = card.querySelector('.quest-count');
                const completeBtn = card.querySelector('.complete-quest-btn');

                const progress = (quest.progress / quest.max) * 100;

                if (questCount) questCount.textContent = `${quest.progress}/${quest.max}`;
                if (progressBar) progressBar.style.width = `${progress}%`;

                // Show complete button if quest is ready and not completed
                if (completeBtn) {
                    if (quest.progress >= quest.max && !quest.completed) {
                        completeBtn.style.display = 'block';
                        card.classList.add('quest-ready');
                    } else {
                        completeBtn.style.display = 'none';
                        card.classList.remove('quest-ready');
                    }

                    if (quest.completed) {
                        card.classList.add('quest-completed');
                        completeBtn.style.display = 'none';
                    }
                }
            }
        });
    }

    updatePersonalQuestsDisplay() {
        if (!this.personalQuests) return;

        const personalQuestsList = document.getElementById('personalQuestsList');
        if (!personalQuestsList) return;

        personalQuestsList.innerHTML = '';

        if (this.personalQuests.length === 0) {
            personalQuestsList.innerHTML = '<div class="empty-message">No personal quests yet</div>';
            return;
        }

        this.personalQuests.forEach(quest => {
            const questElement = document.createElement('div');
            questElement.className = `personal-quest-item ${quest.completed ? 'completed' : ''}`;

            questElement.innerHTML = `
                <div class="quest-info">
                    <div class="quest-title">${quest.name}</div>
                    <div class="quest-desc">${quest.description || 'No description'}</div>
                    <div class="quest-reward">Reward: +${quest.reward_xp} XP, +${quest.reward_coins} 💰</div>
                    <div class="quest-date">Created: ${quest.created_date}</div>
                </div>
                <div class="quest-actions">
                    ${quest.completed ? 
                        '<div class="quest-status completed">COMPLETED</div>' :
                        `<button class="complete-quest-btn" onclick="game.completePersonalQuest(${quest.id})">COMPLETE</button>`
                    }
                    <button class="delete-quest-btn" onclick="game.deletePersonalQuest(${quest.id})">DELETE</button>
                </div>
            `;

            personalQuestsList.appendChild(questElement);
        });
    }

    updateShopDisplay() {
        if (!this.shop) return;

        const shopGrid = document.getElementById('shopGrid');
        if (!shopGrid) return;

        shopGrid.innerHTML = '';

        this.shop.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'shop-item';

            const icon = item.type === 'consumable' ? '🧪' : item.type === 'booster' ? '⚡' : '📦';
            const canAfford = this.playerData && this.playerData.coins >= item.price;

            itemElement.innerHTML = `
                <div class="item-icon">${icon}</div>
                <div class="item-name">${item.name}</div>
                <div class="item-price">${item.price} 💰</div>
                <div class="item-effect">${item.effect}</div>
                <button class="buy-btn" ${!canAfford ? 'disabled' : ''} onclick="game.buyItem('${item.name}')">
                    ${canAfford ? 'BUY' : 'TOO EXPENSIVE'}
                </button>
            `;

            shopGrid.appendChild(itemElement);
        });
    }

    updateAchievementsDisplay() {
        if (!this.achievements) return;

        const achievementsList = document.getElementById('achievementsList');
        if (!achievementsList) return;

        achievementsList.innerHTML = '';

        this.achievements.forEach((achievement, index) => {
            const achievementElement = document.createElement('div');
            const status = achievement.claimed ? 'claimed' : achievement.unlocked ? 'claimable' : 'locked';
            achievementElement.className = `achievement-item ${status}`;

            const icon = achievement.unlocked ? '🏆' : '🔒';

            achievementElement.innerHTML = `
                <div class="achievement-icon">${icon}</div>
                <div class="achievement-info">
                    <div class="achievement-name">${achievement.name}</div>
                    <div class="achievement-desc">${achievement.description}</div>
                    <div class="achievement-reward">Reward: ${achievement.reward_coins} 💰</div>
                </div>
                <div class="achievement-status ${status}">
                    ${achievement.claimed ? 'CLAIMED' : 
                      achievement.unlocked ? 
                        `<button class="claim-btn" onclick="game.claimAchievement(${index})">CLAIM</button>` :
                        'LOCKED'
                    }
                </div>
            `;

            achievementsList.appendChild(achievementElement);
        });
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
            });
        });
    }

    startTimer() {
        if (this.timerInterval) clearInterval(this.timerInterval);

        if (this.dailyTasks && this.dailyTasks.timer_seconds) {
            let seconds = this.dailyTasks.timer_seconds;

            this.timerInterval = setInterval(() => {
                seconds--;

                if (seconds <= 0) {
                    clearInterval(this.timerInterval);
                    this.loadDailyTasks(); // Reload tasks when timer expires
                    return;
                }

                const hours = Math.floor(seconds / 3600);
                const minutes = Math.floor((seconds % 3600) / 60);
                const secs = seconds % 60;

                const timerElement = document.getElementById('timer');
                if (timerElement) {
                    timerElement.textContent = `TIME REMAINING: ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

                    if (seconds < 3600) { // Less than 1 hour
                        timerElement.classList.add('warning');
                    }
                }
            }, 1000);
        }
    }

    showScreen(screenName) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        const targetScreen = document.getElementById(screenName);
        if (targetScreen) {
            targetScreen.classList.add('active');
        }

        // Load specific data when switching screens
        if (screenName === 'leaderboard') {
            this.loadLeaderboard();
        }
    }

    async completeTask(taskIndex) {
        try {
            const response = await fetch('/api/complete-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ task_index: taskIndex })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadAllData();
                this.showNotification('Task completed! +XP +Coins');
                this.createParticleEffect('✨');
            }
        } catch (error) {
            console.error('Failed to complete task:', error);
            this.showNotification('Failed to complete task', 'error');
        }
    }

    async allocateStat(statName) {
        if (!this.playerData || this.playerData.stats.available_points <= 0) {
            this.showNotification('No available stat points', 'error');
            return;
        }

        try {
            const response = await fetch('/api/allocate-stat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ stat_name: statName })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadPlayer();
                this.showNotification(`${statName.toUpperCase()} increased!`);
            }
        } catch (error) {
            console.error('Failed to allocate stat:', error);
            this.showNotification('Failed to allocate stat', 'error');
        }
    }

    async buyItem(itemName) {
        try {
            const response = await fetch('/api/buy-item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ item_name: itemName })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadPlayer();
                await this.loadInventory();
                await this.loadShop();
                this.showNotification(`${itemName} purchased!`);
            } else {
                this.showNotification(result.error || 'Purchase failed', 'error');
            }
        } catch (error) {
            console.error('Failed to buy item:', error);
            this.showNotification('Purchase failed', 'error');
        }
    }

    async useItem(itemName) {
        try {
            const response = await fetch('/api/use-item', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ item_name: itemName })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadPlayer();
                await this.loadInventory();
                this.showNotification(`${itemName} used!`);
            } else {
                this.showNotification(result.error || 'Failed to use item', 'error');
            }
        } catch (error) {
            console.error('Failed to use item:', error);
            this.showNotification('Failed to use item', 'error');
        }
    }

    async completeQuest(questName) {
        try {
            const response = await fetch('/api/complete-quest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quest_name: questName })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadAllData();
                this.showNotification(`Quest completed! +${result.rewards.xp} XP +${result.rewards.coins} 💰`);
                this.createQuestCompleteEffect();
            } else {
                this.showNotification(result.error || 'Quest not ready', 'error');
            }
        } catch (error) {
            console.error('Failed to complete quest:', error);
            this.showNotification('Failed to complete quest', 'error');
        }
    }

    async addPersonalQuest() {
        const questName = document.getElementById('questName').value.trim();
        const questDescription = document.getElementById('questDescription').value.trim();

        if (!questName) {
            this.showNotification('Quest name is required', 'error');
            return;
        }

        try {
            const response = await fetch('/api/add-personal-quest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    name: questName,
                    description: questDescription
                })
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('questName').value = '';
                document.getElementById('questDescription').value = '';
                await this.loadPersonalQuests();
                await this.loadQuests();
                this.showNotification('Personal quest added!');
            } else {
                this.showNotification(result.error || 'Failed to add quest', 'error');
            }
        } catch (error) {
            console.error('Failed to add personal quest:', error);
            this.showNotification('Failed to add quest', 'error');
        }
    }

    async completePersonalQuest(questId) {
        try {
            const response = await fetch('/api/complete-personal-quest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quest_id: questId })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadAllData();
                this.showNotification(`Personal quest completed! +${result.rewards.xp} XP +${result.rewards.coins} 💰`);
            } else {
                this.showNotification(result.error || 'Failed to complete quest', 'error');
            }
        } catch (error) {
            console.error('Failed to complete personal quest:', error);
            this.showNotification('Failed to complete quest', 'error');
        }
    }

    async deletePersonalQuest(questId) {
        if (!confirm('Are you sure you want to delete this quest?')) return;

        try {
            const response = await fetch('/api/delete-personal-quest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quest_id: questId })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadPersonalQuests();
                await this.loadQuests();
                this.showNotification('Personal quest deleted');
            } else {
                this.showNotification(result.error || 'Failed to delete quest', 'error');
            }
        } catch (error) {
            console.error('Failed to delete personal quest:', error);
            this.showNotification('Failed to delete quest', 'error');
        }
    }

    async claimAchievement(achievementIndex) {
        try {
            const response = await fetch('/api/claim-achievement', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ achievement_index: achievementIndex })
            });

            const result = await response.json();

            if (result.success) {
                await this.loadPlayer();
                await this.loadAchievements();
                this.showNotification(`Achievement claimed! +${result.coins_awarded} 💰`);
            } else {
                this.showNotification(result.error || 'Failed to claim achievement', 'error');
            }
        } catch (error) {
            console.error('Failed to claim achievement:', error);
            this.showNotification('Failed to claim achievement', 'error');
        }
    }

    async loadLeaderboard() {
        try {
            const response = await fetch('/api/leaderboard');
            const leaderboard = await response.json();
            this.updateLeaderboardDisplay(leaderboard);
        } catch (error) {
            console.error('Failed to load leaderboard:', error);
            this.showNotification('Failed to load leaderboard', 'error');
        }
    }

    updateLeaderboardDisplay(leaderboard) {
        const currentRank = document.getElementById('currentRank');
        const totalPlayers = document.getElementById('totalPlayers');
        const leaderboardList = document.getElementById('leaderboardList');

        if (currentRank) currentRank.textContent = leaderboard.current_player_position;
        if (totalPlayers) totalPlayers.textContent = leaderboard.total_players;

        if (leaderboardList) {
            leaderboardList.innerHTML = '';

            leaderboard.players.forEach(player => {
                const playerElement = document.createElement('div');
                playerElement.className = `leaderboard-entry ${player.position <= 3 ? 'top-three' : ''}`;

                playerElement.innerHTML = `
                    <div class="position">#${player.position}</div>
                    <div class="player-info">
                        <div class="player-name">${player.name}</div>
                        <div class="player-details">
                            <span class="level">Level ${player.level}</span>
                            <span class="class">${player.class}</span>
                            <span class="rank rank-${player.rank.toLowerCase()}">${player.rank}</span>
                        </div>
                    </div>
                    <div class="player-stats">
                        <div class="experience">${player.total_experience} XP</div>
                        <div class="streak">${player.max_streak} streak</div>
                    </div>
                `;

                leaderboardList.appendChild(playerElement);
            });
        }
    }

    showLeaderboard() {
        this.showScreen('leaderboard');
    }

    showNotification(message, type = 'success') {
        const container = document.getElementById('notificationContainer');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Hide and remove notification
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                container.removeChild(notification);
            }, 300);
        }, 3000);
    }

    createParticleEffect(emoji) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.textContent = emoji;
        particle.style.position = 'fixed';
        particle.style.left = Math.random() * window.innerWidth + 'px';
        particle.style.top = window.innerHeight + 'px';
        particle.style.fontSize = '24px';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '1000';

        document.body.appendChild(particle);

        setTimeout(() => {
            document.body.removeChild(particle);
        }, 2000);
    }

    createQuestCompleteEffect() {
        const effect = document.createElement('div');
        effect.className = 'quest-complete-effect';
        effect.style.left = '50%';
        effect.style.top = '50%';

        document.body.appendChild(effect);

        setTimeout(() => {
            document.body.removeChild(effect);
        }, 1000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.game = new Game();
});