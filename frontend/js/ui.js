// Gestion de l'interface utilisateur
const UI = {
    elements: {},

    init: function() {
        this.elements = {
            pageContent: document.getElementById('page-content'),
            loading: document.getElementById('loading'),
            messageContainer: document.getElementById('message-container'),
            message: document.getElementById('message'),
            navLinks: document.querySelectorAll('.nav-link'),
            authRequired: document.querySelectorAll('.auth-required'),
            guestOnly: document.querySelectorAll('.guest-only'),
            logoutLink: document.getElementById('logout-link')
        };

        this.updateNavigation();
        this.setupEventListeners();
    },

    setupEventListeners: function() {
        // Navigation principale
        document.getElementById('main-nav').addEventListener('click', (e) => {
            const link = e.target.closest('[data-page]');
            if (link) {
                e.preventDefault();
                App.loadPage(link.getAttribute('data-page'));
            }
        });

        // Déconnexion
        this.elements.logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
            this.updateNavigation();
            App.loadPage('login');
            this.showMessage('Vous avez été déconnecté avec succès', 'success');
        });
    },

    // Délégation d'événements pour les liens dans le contenu dynamique
    bindPageLinks: function() {
        document.getElementById('page-content').addEventListener('click', (e) => {
            const link = e.target.closest('[data-page]');
            if (link) {
                e.preventDefault();
                App.loadPage(link.getAttribute('data-page'));
            }
        });
    },

    updateNavigation: function() {
        const auth = Auth.isAuthenticated();
        document.querySelectorAll('.auth-required').forEach(el => el.classList.toggle('hidden', !auth));
        document.querySelectorAll('.guest-only').forEach(el => el.classList.toggle('hidden', auth));
    },

    showMessage: function(text, type = 'success') {
        this.elements.message.textContent = text;
        this.elements.message.className = type;
        this.elements.messageContainer.classList.remove('hidden');
        clearTimeout(this._msgTimer);
        this._msgTimer = setTimeout(() => this.hideMessage(), 5000);
    },

    hideMessage: function() {
        this.elements.messageContainer.classList.add('hidden');
    },

    showLoading: function() {
        this.elements.loading.classList.remove('hidden');
    },

    hideLoading: function() {
        this.elements.loading.classList.add('hidden');
    },

    setContent: function(html) {
        this.hideLoading();
        this.elements.pageContent.innerHTML = html;
        this.bindPageLinks();
    }
};
