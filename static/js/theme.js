// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use preferred color scheme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeToggle(savedTheme);
    } else if (prefersDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeToggle('dark');
    }
    
    // Theme toggle click handler
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Update theme
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update toggle button
            updateThemeToggle(newTheme);
        });
    }
    
    // Update toggle button icon and text
    function updateThemeToggle(theme) {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) return;
        
        const icon = themeToggle.querySelector('i');
        const text = themeToggle.querySelector('span');
        
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            text.textContent = 'Light Mode';
        } else {
            icon.className = 'fas fa-moon';
            text.textContent = 'Dark Mode';
        }
    }
});

// Add animation classes to elements when they come into view
document.addEventListener('DOMContentLoaded', function() {
    // Add the fade-in class to tweets
    const tweets = document.querySelectorAll('.card');
    tweets.forEach((tweet, index) => {
        tweet.classList.add('fade-in');
        tweet.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add tweet-card class to tweet cards for hover effect
    const tweetCards = document.querySelectorAll('.tweets .card');
    tweetCards.forEach(card => {
        card.classList.add('tweet-card');
    });
    
    // Add classes to user suggestions and trending items
    const suggestionItems = document.querySelectorAll('.user-suggestions .list-group-item');
    suggestionItems.forEach(item => {
        item.classList.add('user-suggestion-item');
    });
    
    const trendingItems = document.querySelectorAll('.trending .list-group-item');
    trendingItems.forEach(item => {
        item.classList.add('trending-item');
    });
});
