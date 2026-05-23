// Configuration de l'application
const CONFIG = {
    API_URL: 'http://localhost:8000/api/v1',

    // 8 jours en millisecondes
    TOKEN_EXPIRY: 8 * 24 * 60 * 60 * 1000,

    STORAGE_KEYS: {
        TOKEN: 'auth_token',
        USER: 'user_data',
        TOKEN_EXPIRY: 'token_expiry'
    }
};
