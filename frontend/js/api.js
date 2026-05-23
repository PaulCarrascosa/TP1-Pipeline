// Gestion des appels API
const Api = {
    getHeaders: function() {
        const headers = { 'Content-Type': 'application/json' };
        if (Auth.isAuthenticated()) {
            headers['Authorization'] = `Bearer ${Auth.getToken()}`;
        }
        return headers;
    },

    call: async function(endpoint, method = 'GET', data = null) {
        UI.showLoading();
        const url = `${CONFIG.API_URL}${endpoint}`;
        const options = { method, headers: this.getHeaders() };

        if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(responseData.detail || 'Une erreur est survenue');
            }

            UI.hideLoading();
            return responseData;
        } catch (error) {
            UI.hideLoading();
            UI.showMessage(error.message, 'error');
            throw error;
        }
    },

    // Authentification
    login: async function(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        UI.showLoading();
        try {
            const response = await fetch(`${CONFIG.API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Échec de la connexion');

            Auth.setToken(data.access_token);
            await this.getCurrentUser();
            UI.hideLoading();
            return data;
        } catch (error) {
            UI.hideLoading();
            UI.showMessage(error.message, 'error');
            throw error;
        }
    },

    register: async function(userData) {
        return this.call('/auth/register', 'POST', userData);
    },

    getCurrentUser: async function() {
        try {
            const userData = await this.call('/users/me');
            Auth.setUser(userData);
            return userData;
        } catch (error) {
            Auth.logout();
            throw error;
        }
    },

    updateCurrentUser: async function(userData) {
        const updated = await this.call('/users/me', 'PUT', userData);
        Auth.setUser(updated);
        return updated;
    },

    changePassword: async function(newPassword) {
        return this.call('/users/me', 'PUT', { password: newPassword });
    },

    // Livres — retourne la structure Page {items, total, page, size, pages}
    getBooks: async function(skip = 0, limit = 12, query = null) {
        let endpoint = `/books/?skip=${skip}&limit=${limit}`;
        if (query) {
            endpoint = `/books/search/?query=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`;
        }
        return this.call(endpoint);
    },

    getBook: async function(id) {
        return this.call(`/books/${id}`);
    },

    searchBooks: async function(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this.call(`/books/search/?${qs}`);
    },

    // Emprunts
    getUserLoans: async function(userId) {
        return this.call(`/loans/user/${userId}`);
    },

    returnLoan: async function(loanId) {
        return this.call(`/loans/${loanId}/return`, 'POST');
    }
};
