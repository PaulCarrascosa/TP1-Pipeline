// Gestion de l'authentification
const Auth = {
    setToken: function(token, expiresIn = CONFIG.TOKEN_EXPIRY) {
        const expiryTime = Date.now() + expiresIn;
        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY, expiryTime);
    },

    getToken: function() {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    },

    isAuthenticated: function() {
        const token = this.getToken();
        if (!token) return false;
        const expiryTime = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY);
        if (!expiryTime) return false;
        return Date.now() < parseInt(expiryTime);
    },

    setUser: function(userData) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(userData));
    },

    getUser: function() {
        const raw = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);
        return raw ? JSON.parse(raw) : null;
    },

    logout: function() {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
    }
};
