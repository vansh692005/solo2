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
        this.currentScreen = 'daily-tasks';

        this.init();
    }

    async init() {
        try {
            await this.loadAllData();
            this.setupEventListeners();
            this.startTimer();
            this.showNotification('Welcome back, Hunter!', 'success');
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
            if (!response.ok) throw new Error('Failed to load player data');
            this.playerData = await response.json();
            this.updatePlayerDisplay();
        } catch (error) {
            console.error('Failed to load player data:', error);
            this.showNotification('Failed to load player data', 'error');
        }
    }

    async loadDailyTasks() {
        try {
            const response = await fetch('/api/daily-tasks');
            if (!response.ok) throw new Error('Failed to load daily tasks');
            this.dailyTasks = await response.json();
            this.updateDailyTasksDisplay();
        } catch (error) {
            console.error('Failed to load daily tasks:', error);
            this.showNotification('Failed to load daily tasks', 'error');
        }
    }

    async loadInventory() {
        try {
            const response = await fetch('/api/inventory');
            if (!response.ok) throw new Error('Failed to load inventory');
            this.inventory = await response.json();
            this.updateInventoryDisplay();
        } catch (error) {
            console.error('Failed to load inventory:', error);
            this.showNotification('Failed to load inventory', 'error');
        }
    }

    async loadQuests() {
        try {
            const response = await fetch('/api/quests');
            if (!response.ok) throw new Error('Failed to load quests');
            this.quests = await response.json();
            this.updateQuestsDisplay();
        } catch (error) {
            console.error('Failed to load quests:', error);
            this.showNotification('Failed to load quests', 'error');
        }
    }

    async loadAchievements() {
        try {
            const response = await fetch('/api/achievements');
            if (!response.ok) throw new Error('Failed to load achievements');
            this.achievements = await response.json();
            this.updateAchievementsDisplay();
        } catch (error) {
            console.error('Failed to load achievements:', error);
            this.showNotification('Failed to load achievements', 'error');
        }
    }

    async loadShop() {
        try {
            const response = await fetch('/api/shop');
            if (!response.ok) throw new Error('Failed to load shop');
            this.shop = await response.json();
            this.updateShopDisplay();
        } catch (error) {
            console.error('Failed to load shop:', error);
            this.showNotification('Failed to load shop', 'error');
        }
    }

    async loadPersonalQuests() {
        try {
            const response = await fetch('/api/personal-quests');
            if (!response.ok) throw new Error('Failed to load personal quests');
            this.personalQuests = await response.json();
            this.updatePersonalQuestsDisplay();
        } catch (error) {
            console.error('Failed to load personal quests:', error);
            this.showNotification('Failed to load personal quests', 'error');
        }
    }

    updatePlayerDisplay() {
        if (!this.playerData) return;

        // Update header
        const playerLevel = document.getElementById('playerLevel');
        const playerName = document.getElementById('playerName');
        const playerCoins = document.getElementById('playerCoins');
        const playerEnergy = document.getElementById('playerEnergy');

        if (playerLevel) playerLevel.textContent = this.playerData.level;
        if (playerName) playerName.textContent = this.playerData.name;
        if (playerCoins) playerCoins.textContent = this.playerData.coins;
        if (playerEnergy) playerEnergy.textContent = `${this.playerData.energy}/${this.playerData.max_energy}`;

        // Update XP bar
        const xpProgress = document.getElementById('xpProgress');
        const xpText = document.getElementById('xpText');
        const xpPercentage = (this.playerData.current_xp / this.playerData.xp_to_next_level) * 100;

        if (xpProgress) xpProgress.style.width = `${xpPercentage}%`;
        if (xpText) xpText.textContent = `${this.playerData.current_xp}/${this.playerData.xp_to_next_level}`;

        // Update status screen
        const statusPlayerName = document.getElementById('statusPlayerName');
        const playerClass = document.getElementById('playerClass');
        const playerTitle = document.getElementById('playerTitle');
        const playerRank = document.getElementById('playerRank');
        const rankName = document.getElementById('rankName');

        if (statusPlayerName) statusPlayerName.textContent = this.playerData.name;
        if (playerClass) playerClass.textContent = this.playerData.class;
        if (playerTitle) playerTitle.textContent = this.playerData.title;
        if (playerRank) playerRank.textContent = this.playerData.rank;
        if (rankName) rankName.textContent = this.playerData.rank_name;

        this.updateStatsDisplay();
        this.updateRankDisplay();
    }

    updateStatsDisplay() {
        if (!this.playerData || !this.playerData.stats) return;

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

        const rankBadge = document.getElementById('rankBadge');
        const physicalReduction = document.getElementById('physicalReduction');
        const magicalReduction = document.getElementById('magicalReduction');
        const totalExperience = document.getElementById('totalExperience');
        const rankScore = document.getElementById('rankScore');

        if (rankBadge) {
            rankBadge.textContent = this.playerData.rank || 'E';
            rankBadge.className = `rank-badge rank-${(this.playerData.rank || 'E').toLowerCase()}`;
        }

        if (physicalReduction) physicalReduction.textContent = `${this.playerData.physical_damage_reduction || 0}%`;
        if (magicalReduction) magicalReduction.textContent = `${this.playerData.magical_damage_reduction || 0}%`;
        if (totalExperience) totalExperience.textContent = this.playerData.total_experience || 0;
        if (rankScore) rankScore.textContent = this.playerData.rank_score || 0;
    }

    updateDailyTasksDisplay() {
        if (!this.dailyTasks) return;

        const taskList = document.getElementById('taskList');
        const streakNumber = document.getElementById('streakNumber');

        if (streakNumber) streakNumber.textContent = this.dailyTasks.streak;

        if (taskList) {
            taskList.innerHTML = '';
            
            if (this.dailyTasks.tasks.length === 0) {
                taskList.innerHTML = '<div class="empty-message">No daily tasks available</div>';
                return;
            }

            this.dailyTasks.tasks.forEach((task, index) => {
                const taskElement = document.createElement('div');
                taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;

                taskElement.innerHTML = `
                    <div class="task-checkbox ${task.completed ? 'checked' : ''}" onclick="game.completeTask(${task.id})">
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
        const inventoryGrid = document.getElementById('inventoryGrid');
        if (!inventoryGrid) return;

        inventoryGrid.innerHTML = '';

        if (!this.inventory || this.inventory.length === 0) {
            inventoryGrid.innerHTML = '<div class="empty-message">Your inventory is empty</div>';
            return;
        }

        this.inventory.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'inventory-item';

            const icon = item.type === 'consumable' ? '🧪' : item.type === 'booster' ? '⚡' : '📦';

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
        const personalQuestsList = document.getElementById('personalQuestsList');
        if (!personalQuestsList) return;

        personalQuestsList.innerHTML = '';

        if (!this.personalQuests || this.personalQuests.length === 0) {
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
        const shopGrid = document.getElementById('shopGrid');
        if (!shopGrid) return;

        shopGrid.innerHTML = '';

        if (!this.shop || this.shop.length === 0) {
            shopGrid.innerHTML = '<div class="empty-message">No items available in shop</div>';
            return;
        }

        this.shop.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'shop-item';

            const icon = item.type === 'consumable' ? '🧪' : item.type === 'booster' ? '⚡' : '📦';

            itemElement.innerHTML = `
                <div class="shop-item-icon">${icon}</div>
                <div class="shop-item-name">${item.name}</div>
                <div class="shop-item-price">💰 ${item.price}</div>
                <div class="shop-item-effect">${item.effect}</div>
                <div class="shop-item-description">${item.description}</div>
                <button class="buy-btn" onclick="game.buyItem(${item.id})">BUY</button>
            `;

            shopGrid.appendChild(itemElement);
        });
    }

    updateAchievementsDisplay() {
        const achievementsList = document.getElementById('achievementsList');
        if (!achievementsList) return;

        achievementsList.innerHTML = '';

        if (!this.achievements || this.achievements.length === 0) {
            achievementsList.innerHTML = '<div class="empty-message">No achievements available</div>';
            return;
        }

        this.achievements.forEach(achievement => {
            const achievementElement = document.createElement('div');
            achievementElement.className = `achievement-item ${achievement.unlocked ? 'unlocked' : ''} ${achievement.claimed ? 'claimed' : ''}`;

            const claimButton = achievement.unlocked && !achievement.claimed ? 
                `<button class="claim-btn" onclick="game.claimAchievement(${achievement.id})">CLAIM REWARD</button>` : '';

            achievementElement.innerHTML = `
                <div class="achievement-icon">🏆</div>
                <div class="achievement-info">
                    <div class="achievement-name">${achievement.name}</div>
                    <div class="achievement-description">${achievement.description}</div>
                    <div class="achievement-reward">Reward: +${achievement.reward_xp} XP, +${achievement.reward_coins} 💰</div>
                    ${achievement.unlocked && achievement.unlock_date ? 
                        `<div class="achievement-date">Unlocked: ${new Date(achievement.unlock_date).toLocaleDateString()}</div>` : 
                        ''
                    }
                    ${achievement.claimed ? '<div class="claimed-status">✓ CLAIMED</div>' : ''}
                </div>
                <div class="achievement-actions">
                    ${claimButton}
                </div>
            `;

            achievementsList.appendChild(achievementElement);
        });
    }

    // Task completion
    async completeTask(taskId) {
        try {
            const response = await fetch(`/api/complete-task/${taskId}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                // Check for level up and show animation
                if (result.level_up && result.new_level) {
                    this.showLevelUpAnimation(result.new_level);
                    this.showNotification(`Level up! You are now Level ${result.new_level}!`, 'success');
                } else {
                    this.showNotification(result.message, 'success');
                }
                await this.loadDailyTasks();
                await this.loadPlayer();
            } else {
                this.showNotification(result.error || 'Failed to complete task', 'error');
            }
        } catch (error) {
            console.error('Error completing task:', error);
            this.showNotification('Failed to complete task', 'error');
        }
    }

    // Quest completion
    async completeQuest(questType) {
        try {
            const response = await fetch(`/api/complete-quest/${questType}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification(result.message, 'success');
                await this.loadQuests();
                await this.loadPlayer();
            } else {
                this.showNotification(result.error || 'Failed to complete quest', 'error');
            }
        } catch (error) {
            console.error('Error completing quest:', error);
            this.showNotification('Failed to complete quest', 'error');
        }
    }

    // Increment quest progress
    async incrementQuest(questType, amount = 1) {
        try {
            const response = await fetch(`/api/increment-quest/${questType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ amount })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                await this.loadQuests();
            } else {
                console.error('Failed to increment quest:', result.error);
            }
        } catch (error) {
            console.error('Error incrementing quest:', error);
        }
    }

    // Stat allocation
    async allocateStat(statName) {
        try {
            const response = await fetch(`/api/allocate-stat/${statName}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification(`${statName.toUpperCase()} increased!`, 'success');
                await this.loadPlayer();
            } else {
                this.showNotification(result.error || 'Failed to allocate stat', 'error');
            }
        } catch (error) {
            console.error('Error allocating stat:', error);
            this.showNotification('Failed to allocate stat', 'error');
        }
    }

    // Item usage
    async useItem(itemName) {
        try {
            const response = await fetch(`/api/use-item/${encodeURIComponent(itemName)}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification(result.message, 'success');
                await this.loadInventory();
                await this.loadPlayer();
            } else {
                this.showNotification(result.error || 'Failed to use item', 'error');
            }
        } catch (error) {
            console.error('Error using item:', error);
            this.showNotification('Failed to use item', 'error');
        }
    }

    // Achievement claiming
    async claimAchievement(achievementId) {
        try {
            const response = await fetch(`/api/claim-achievement/${achievementId}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification(result.message, 'success');
                await this.loadAchievements();
                await this.loadPlayer();
            } else {
                this.showNotification(result.error || 'Failed to claim achievement', 'error');
            }
        } catch (error) {
            console.error('Error claiming achievement:', error);
            this.showNotification('Failed to claim achievement', 'error');
        }
    }

    // Item purchase
    async buyItem(itemId) {
        try {
            const response = await fetch(`/api/buy-item/${itemId}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification(result.message, 'success');
                await this.loadInventory();
                await this.loadPlayer();
            } else {
                this.showNotification(result.error || 'Failed to buy item', 'error');
            }
        } catch (error) {
            console.error('Error buying item:', error);
            this.showNotification('Failed to buy item', 'error');
        }
    }

    // Personal quest management
    async addPersonalQuest() {
        const questName = document.getElementById('questName');
        const questDescription = document.getElementById('questDescription');

        if (!questName || !questName.value.trim()) {
            this.showNotification('Please enter a quest name', 'error');
            return;
        }

        try {
            const response = await fetch('/api/add-personal-quest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: questName.value.trim(),
                    description: questDescription ? questDescription.value.trim() : ''
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification(result.message, 'success');
                questName.value = '';
                if (questDescription) questDescription.value = '';
                await this.loadPersonalQuests();
            } else {
                this.showNotification(result.error || 'Failed to add quest', 'error');
            }
        } catch (error) {
            console.error('Error adding personal quest:', error);
            this.showNotification('Failed to add quest', 'error');
        }
    }

    async completePersonalQuest(questId) {
        try {
            const response = await fetch(`/api/complete-personal-quest/${questId}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                // Check for level up and show animation
                if (result.level_up && result.new_level) {
                    this.showLevelUpAnimation(result.new_level);
                    this.showNotification(`Level up! You are now Level ${result.new_level}!`, 'success');
                } else {
                    this.showNotification(result.message, 'success');
                }
                await this.loadPersonalQuests();
                await this.loadPlayer();
            } else {
                this.showNotification(result.error || 'Failed to complete quest', 'error');
            }
        } catch (error) {
            console.error('Error completing personal quest:', error);
            this.showNotification('Failed to complete quest', 'error');
        }
    }

    async deletePersonalQuest(questId) {
        if (!confirm('Are you sure you want to delete this quest?')) {
            return;
        }

        try {
            const response = await fetch(`/api/delete-personal-quest/${questId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification(result.message, 'success');
                await this.loadPersonalQuests();
            } else {
                this.showNotification(result.error || 'Failed to delete quest', 'error');
            }
        } catch (error) {
            console.error('Error deleting personal quest:', error);
            this.showNotification('Failed to delete quest', 'error');
        }
    }

    // Leaderboard
    async showLeaderboard() {
        try {
            const response = await fetch('/api/leaderboard');
            const result = await response.json();

            if (response.ok) {
                this.updateLeaderboardDisplay(result);
                this.showScreen('leaderboard');
            } else {
                this.showNotification('Failed to load leaderboard', 'error');
            }
        } catch (error) {
            console.error('Error loading leaderboard:', error);
            this.showNotification('Failed to load leaderboard', 'error');
        }
    }

    updateLeaderboardDisplay(data) {
        const currentRank = document.getElementById('currentRank');
        const totalPlayers = document.getElementById('totalPlayers');
        const leaderboardList = document.getElementById('leaderboardList');

        if (currentRank) currentRank.textContent = `#${data.current_rank}`;
        if (totalPlayers) totalPlayers.textContent = data.total_players;

        if (leaderboardList) {
            leaderboardList.innerHTML = '';

            if (data.leaderboard.length === 0) {
                leaderboardList.innerHTML = '<div class="empty-message">No players on leaderboard yet</div>';
                return;
            }

            data.leaderboard.forEach(player => {
                const entryElement = document.createElement('div');
                entryElement.className = `leaderboard-entry ${player.position <= 3 ? 'top3' : ''}`;

                // Add medal icons for top 3
                let rankDisplay = `#${player.position}`;
                if (player.position === 1) rankDisplay = '🥇 #1';
                else if (player.position === 2) rankDisplay = '🥈 #2';
                else if (player.position === 3) rankDisplay = '🥉 #3';

                entryElement.innerHTML = `
                    <div class="entry-rank ${player.position <= 3 ? 'top3' : ''}">${rankDisplay}</div>
                    <div class="entry-name">${player.name}</div>
                    <div class="entry-level">LVL ${player.level}</div>
                    <div class="entry-rank-number">#${player.position}</div>
                    <div class="entry-score">${player.rank_score}</div>
                    <div class="entry-streak">${player.daily_streak}</div>
                `;

                leaderboardList.appendChild(entryElement);
            });
        }
    }

    hideLeaderboard() {
        this.showScreen('quests');
    }

    // Screen navigation
    showScreen(screenId) {
        // Hide all screens
        const screens = document.querySelectorAll('.screen');
        screens.forEach(screen => screen.classList.remove('active'));

        // Show selected screen
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
        }

        // Update navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => item.classList.remove('active'));

        // Find and activate corresponding nav item
        const navMap = {
            'daily-tasks': 0,
            'inventory': 1,
            'quests': 2,
            'status': 3,
            'shop': 4,
            'achievements': 5
        };

        const navIndex = navMap[screenId];
        if (navIndex !== undefined && navItems[navIndex]) {
            navItems[navIndex].classList.add('active');
        }

        this.currentScreen = screenId;
    }

    // Timer functionality
    startTimer() {
        this.updateTimer();
        this.timerInterval = setInterval(() => this.updateTimer(), 1000);
    }

    async updateTimer() {
        try {
            const response = await fetch('/api/time-remaining');
            const data = await response.json();

            const timerElement = document.getElementById('timer');
            if (timerElement) {
                const hours = String(data.hours).padStart(2, '0');
                const minutes = String(data.minutes).padStart(2, '0');
                const seconds = String(data.seconds).padStart(2, '0');
                
                timerElement.textContent = `TIME REMAINING: ${hours}:${minutes}:${seconds}`;

                // Add warning class if less than 1 hour remaining
                if (data.total_seconds < 3600) {
                    timerElement.classList.add('warning');
                } else {
                    timerElement.classList.remove('warning');
                }

                // Reload data when timer resets (when it's a new day)
                if (data.hours === 23 && data.minutes === 59 && data.seconds === 59) {
                    setTimeout(() => {
                        this.loadAllData();
                    }, 2000);
                }
            }
        } catch (error) {
            console.error('Error updating timer:', error);
        }
    }

    // Event listeners
    setupEventListeners() {
        // Navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                const screens = ['daily-tasks', 'inventory', 'quests', 'status', 'shop', 'achievements'];
                if (screens[index]) {
                    this.showScreen(screens[index]);
                }
            });
        });

        // Add quest form
        const questName = document.getElementById('questName');
        const questDescription = document.getElementById('questDescription');

        if (questName) {
            questName.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addPersonalQuest();
                }
            });
        }

        if (questDescription) {
            questDescription.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.addPersonalQuest();
                }
            });
        }

        // Auto-increment quest progress based on interactions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('task-checkbox') && !e.target.classList.contains('checked')) {
                this.incrementQuest('discipline', 1);
            }
            
            if (e.target.classList.contains('use-btn')) {
                this.incrementQuest('spiritual_training', 1);
            }
            
            if (e.target.classList.contains('buy-btn')) {
                this.incrementQuest('intelligence', 1);
            }
            
            if (e.target.classList.contains('stat')) {
                this.incrementQuest('strength_training', 1);
            }
        });
    }

    // Notification system
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (!notification) return;

        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');

        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    // Level up animation
    showLevelUpAnimation(newLevel) {
        const levelUpDiv = document.createElement('div');
        levelUpDiv.className = 'level-up-animation';
        levelUpDiv.innerHTML = `
            <div class="level-up-content">
                <div class="level-up-burst">💥</div>
                <div class="level-up-text">LEVEL UP!</div>
                <div class="level-up-number">LEVEL ${newLevel}</div>
                <div class="level-up-effects">✨ STATS INCREASED! ✨</div>
                <div class="level-up-glow"></div>
            </div>
        `;
        
        document.body.appendChild(levelUpDiv);
        
        // Remove animation after 4 seconds
        setTimeout(() => {
            if (levelUpDiv.parentNode) {
                levelUpDiv.parentNode.removeChild(levelUpDiv);
            }
        }, 4000);
    }

    // Cleanup
    destroy() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.game = new Game();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.game) {
        window.game.destroy();
    }
});
