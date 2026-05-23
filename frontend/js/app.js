// Application principale
const App = {
    currentPage: null,

    init: function() {
        UI.init();
        this.loadInitialPage();
    },

    loadInitialPage: function() {
        App.loadPage(Auth.isAuthenticated() ? 'books' : 'login');
    },

    loadPage: function(page) {
        const authRequired = ['books', 'profile', 'loans'];
        if (authRequired.includes(page) && !Auth.isAuthenticated()) {
            UI.showMessage('Vous devez être connecté pour accéder à cette page', 'error');
            page = 'login';
        }

        this.currentPage = page;

        // Mettre à jour le lien actif
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-page') === page);
        });

        switch (page) {
            case 'login':    this.loadLoginPage();    break;
            case 'register': this.loadRegisterPage(); break;
            case 'books':    this.loadBooksPage();    break;
            case 'profile':  this.loadProfilePage();  break;
            case 'loans':    this.loadLoansPage();    break;
            default:         this.loadLoginPage();
        }
    },

    // ===== Connexion =====
    loadLoginPage: function() {
        UI.setContent(`
            <div class="form-container">
                <h2 class="text-center mb-20">Connexion</h2>
                <form id="login-form">
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" class="form-control" placeholder="votre@email.com" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Mot de passe</label>
                        <input type="password" id="password" class="form-control" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-block">Se connecter</button>
                </form>
                <p class="text-center mt-20">
                    Pas encore de compte ?
                    <a href="#" data-page="register">Inscrivez-vous</a>
                </p>
            </div>
        `);

        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await Api.login(
                    document.getElementById('email').value,
                    document.getElementById('password').value
                );
                UI.updateNavigation();
                UI.showMessage('Connexion réussie', 'success');
                App.loadPage('books');
            } catch (_) {}
        });
    },

    // ===== Inscription =====
    loadRegisterPage: function() {
        UI.setContent(`
            <div class="form-container">
                <h2 class="text-center mb-20">Inscription</h2>
                <form id="register-form">
                    <div class="form-group">
                        <label for="full_name">Nom complet</label>
                        <input type="text" id="full_name" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Mot de passe</label>
                        <input type="password" id="password" class="form-control" minlength="8" required>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirmer le mot de passe</label>
                        <input type="password" id="confirm_password" class="form-control" minlength="8" required>
                    </div>
                    <button type="submit" class="btn btn-block">S'inscrire</button>
                </form>
                <p class="text-center mt-20">
                    Déjà un compte ?
                    <a href="#" data-page="login">Connectez-vous</a>
                </p>
            </div>
        `);

        document.getElementById('register-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('password').value;
            const confirm  = document.getElementById('confirm_password').value;

            if (password !== confirm) {
                UI.showMessage('Les mots de passe ne correspondent pas', 'error');
                return;
            }

            try {
                await Api.register({
                    full_name: document.getElementById('full_name').value,
                    email: document.getElementById('email').value,
                    password
                });
                UI.showMessage('Inscription réussie. Vous pouvez maintenant vous connecter.', 'success');
                App.loadPage('login');
            } catch (_) {}
        });
    },

    // ===== Livres =====
    loadBooksPage: async function(skip = 0, searchQuery = '') {
        UI.setContent(`<div id="books-placeholder"><div class="spinner" style="margin-top:40px"></div></div>`);

        try {
            const page = await Api.getBooks(skip, 12, searchQuery || null);
            const books = page.items;
            const total = page.total;
            const limit = page.size;
            const currentPage = page.page;
            const totalPages = page.pages;

            const searchBar = `
                <div class="search-bar">
                    <input type="text" id="book-search" class="form-control"
                           placeholder="Rechercher par titre, auteur, ISBN..."
                           value="${searchQuery}">
                    <button class="btn" id="search-btn"><i class="fas fa-search"></i> Rechercher</button>
                    ${searchQuery ? `<button class="btn btn-secondary" id="clear-search">Effacer</button>` : ''}
                </div>
            `;

            let cardsHtml = '';
            if (books.length === 0) {
                cardsHtml = `<p>Aucun livre trouvé.</p>`;
            } else {
                cardsHtml = `<div class="card-container">`;
                books.forEach(book => {
                    const available = book.quantity > 0;
                    cardsHtml += `
                        <div class="card">
                            <div class="card-header">
                                <h3>${App._escape(book.title)}</h3>
                            </div>
                            <div class="card-body">
                                <p><strong>Auteur :</strong> ${App._escape(book.author)}</p>
                                <p><strong>ISBN :</strong> ${book.isbn}</p>
                                <p><strong>Année :</strong> ${book.publication_year}</p>
                                <p><strong>Disponible :</strong>
                                    <span class="badge ${available ? 'badge-success' : 'badge-error'}">
                                        ${book.quantity} exemplaire(s)
                                    </span>
                                </p>
                            </div>
                            <div class="card-footer">
                                <button class="btn btn-sm" onclick="App.viewBookDetails(${book.id})">
                                    <i class="fas fa-eye"></i> Détails
                                </button>
                            </div>
                        </div>
                    `;
                });
                cardsHtml += `</div>`;
            }

            const paginationHtml = totalPages > 1 ? `
                <div class="pagination">
                    ${currentPage > 1 ? `<button class="btn btn-sm btn-secondary" onclick="App.loadBooksPage(${(currentPage-2)*limit}, '${searchQuery}')">&#8249; Préc.</button>` : ''}
                    <span>Page ${currentPage} / ${totalPages} (${total} livres)</span>
                    ${currentPage < totalPages ? `<button class="btn btn-sm" onclick="App.loadBooksPage(${currentPage*limit}, '${searchQuery}')">Suiv. &#8250;</button>` : ''}
                </div>
            ` : `<p class="text-center mt-10" style="color:#888; font-size:0.85rem">${total} livre(s)</p>`;

            UI.setContent(`
                <div class="page-header">
                    <h2>Catalogue de livres</h2>
                </div>
                ${searchBar}
                ${cardsHtml}
                ${paginationHtml}
            `);

            document.getElementById('search-btn').addEventListener('click', () => {
                App.loadBooksPage(0, document.getElementById('book-search').value.trim());
            });
            document.getElementById('book-search').addEventListener('keydown', (e) => {
                if (e.key === 'Enter') App.loadBooksPage(0, e.target.value.trim());
            });
            const clearBtn = document.getElementById('clear-search');
            if (clearBtn) clearBtn.addEventListener('click', () => App.loadBooksPage(0, ''));

        } catch (_) {
            UI.setContent(`<p>Erreur lors du chargement des livres. <a href="#" data-page="books">Réessayer</a></p>`);
        }
    },

    // ===== Détail d'un livre =====
    viewBookDetails: async function(bookId) {
        UI.showLoading();
        try {
            const book = await Api.getBook(bookId);
            const cats = (book.categories || []).map(c =>
                `<span class="category-tag">${App._escape(c.name)}</span>`
            ).join('');

            UI.setContent(`
                <div class="book-details">
                    <button class="btn btn-secondary btn-sm mb-20" onclick="App.loadPage('books')">
                        &#8592; Retour à la liste
                    </button>
                    <h2>${App._escape(book.title)}</h2>
                    <div class="book-info">
                        <p><strong>Auteur :</strong> ${App._escape(book.author)}</p>
                        <p><strong>ISBN :</strong> ${book.isbn}</p>
                        <p><strong>Année :</strong> ${book.publication_year}</p>
                        <p><strong>Éditeur :</strong> ${book.publisher || 'Non spécifié'}</p>
                        <p><strong>Langue :</strong> ${book.language || 'Non spécifiée'}</p>
                        <p><strong>Pages :</strong> ${book.pages || 'Non spécifié'}</p>
                        <p><strong>Quantité disponible :</strong>
                            <span class="badge ${book.quantity > 0 ? 'badge-success' : 'badge-error'}">
                                ${book.quantity} exemplaire(s)
                            </span>
                        </p>
                        ${cats ? `<p><strong>Catégories :</strong> <span class="category-list">${cats}</span></p>` : ''}
                    </div>
                    <div class="book-description">
                        <h3>Description</h3>
                        <p>${book.description ? App._escape(book.description) : 'Aucune description disponible.'}</p>
                    </div>
                </div>
            `);
        } catch (_) {
            UI.setContent(`<p>Erreur. <a href="#" data-page="books">Retour</a></p>`);
        }
    },

    // ===== Profil =====
    loadProfilePage: async function() {
        UI.showLoading();
        try {
            const user = Auth.getUser() || await Api.getCurrentUser();
            const initials = user.full_name.split(' ')
                .map(n => n.charAt(0)).join('').toUpperCase().slice(0, 2);

            UI.setContent(`
                <div class="profile-container">
                    <div class="profile-header">
                        <div class="profile-avatar">${initials}</div>
                        <h2>${App._escape(user.full_name)}</h2>
                        <p style="color:#888">${user.is_admin ? '👑 Administrateur' : 'Utilisateur'}</p>
                    </div>
                    <div class="profile-info mb-20">
                        <div class="profile-info-item">
                            <div class="profile-info-label">Email</div>
                            <div class="profile-info-value">${user.email}</div>
                        </div>
                        <div class="profile-info-item">
                            <div class="profile-info-label">Statut</div>
                            <div class="profile-info-value">
                                <span class="badge ${user.is_active ? 'badge-success' : 'badge-error'}">
                                    ${user.is_active ? 'Actif' : 'Inactif'}
                                </span>
                            </div>
                        </div>
                        <div class="profile-info-item">
                            <div class="profile-info-label">Téléphone</div>
                            <div class="profile-info-value">${user.phone || 'Non spécifié'}</div>
                        </div>
                        <div class="profile-info-item">
                            <div class="profile-info-label">Adresse</div>
                            <div class="profile-info-value">${user.address || 'Non spécifiée'}</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:10px; flex-wrap:wrap">
                        <button class="btn" id="edit-profile-btn">Modifier le profil</button>
                        <button class="btn btn-secondary" id="change-password-btn">Changer le mot de passe</button>
                    </div>
                </div>
            `);

            document.getElementById('edit-profile-btn').addEventListener('click', () =>
                App.loadEditProfilePage(user));
            document.getElementById('change-password-btn').addEventListener('click', () =>
                App.loadChangePasswordPage());
        } catch (_) {
            UI.setContent(`<p>Erreur lors du chargement du profil.</p>`);
        }
    },

    // ===== Édition du profil =====
    loadEditProfilePage: function(user) {
        UI.setContent(`
            <div class="form-container">
                <h2 class="text-center mb-20">Modifier le profil</h2>
                <form id="edit-profile-form">
                    <div class="form-group">
                        <label for="full_name">Nom complet</label>
                        <input type="text" id="full_name" class="form-control"
                               value="${App._escape(user.full_name)}" required>
                    </div>
                    <div class="form-group">
                        <label for="phone">Téléphone</label>
                        <input type="text" id="phone" class="form-control"
                               value="${user.phone || ''}">
                    </div>
                    <div class="form-group">
                        <label for="address">Adresse</label>
                        <textarea id="address" class="form-control">${user.address || ''}</textarea>
                    </div>
                    <button type="submit" class="btn btn-block">Enregistrer</button>
                    <button type="button" class="btn btn-secondary btn-block mt-10"
                            onclick="App.loadPage('profile')">Annuler</button>
                </form>
            </div>
        `);

        document.getElementById('edit-profile-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await Api.updateCurrentUser({
                    full_name: document.getElementById('full_name').value,
                    phone: document.getElementById('phone').value || null,
                    address: document.getElementById('address').value || null
                });
                UI.showMessage('Profil mis à jour avec succès', 'success');
                App.loadPage('profile');
            } catch (_) {}
        });
    },

    // ===== Changement de mot de passe (Ex. 7) =====
    loadChangePasswordPage: function() {
        UI.setContent(`
            <div class="form-container">
                <h2 class="text-center mb-20">Changer le mot de passe</h2>
                <form id="change-password-form">
                    <div class="form-group">
                        <label for="new_password">Nouveau mot de passe</label>
                        <input type="password" id="new_password" class="form-control"
                               minlength="8" required>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirmer le mot de passe</label>
                        <input type="password" id="confirm_password" class="form-control"
                               minlength="8" required>
                    </div>
                    <button type="submit" class="btn btn-block">Changer le mot de passe</button>
                    <button type="button" class="btn btn-secondary btn-block mt-10"
                            onclick="App.loadPage('profile')">Annuler</button>
                </form>
            </div>
        `);

        document.getElementById('change-password-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const newPwd  = document.getElementById('new_password').value;
            const confirm = document.getElementById('confirm_password').value;

            if (newPwd !== confirm) {
                UI.showMessage('Les mots de passe ne correspondent pas', 'error');
                return;
            }
            try {
                await Api.changePassword(newPwd);
                UI.showMessage('Mot de passe changé avec succès', 'success');
                App.loadPage('profile');
            } catch (_) {}
        });
    },

    // ===== Emprunts (Ex. 7) =====
    loadLoansPage: async function() {
        UI.showLoading();
        try {
            const user = Auth.getUser() || await Api.getCurrentUser();
            const loans = await Api.getUserLoans(user.id);

            let tableHtml = '';
            if (loans.length === 0) {
                tableHtml = `<p>Vous n'avez aucun emprunt.</p>`;
            } else {
                const rows = loans.map(loan => {
                    const dueDate = new Date(loan.due_date);
                    const now = new Date();
                    const isOverdue = !loan.return_date && dueDate < now;
                    const status = loan.return_date
                        ? `<span class="badge badge-success">Retourné</span>`
                        : isOverdue
                            ? `<span class="badge badge-error">En retard</span>`
                            : `<span class="badge badge-warning">En cours</span>`;

                    const returnBtn = (!loan.return_date && user.is_admin)
                        ? `<button class="btn btn-sm btn-success" onclick="App.returnLoan(${loan.id})">Retourner</button>`
                        : '';

                    return `
                        <tr>
                            <td>#${loan.id}</td>
                            <td>${loan.book_id}</td>
                            <td>${new Date(loan.loan_date).toLocaleDateString('fr-FR')}</td>
                            <td>${dueDate.toLocaleDateString('fr-FR')}</td>
                            <td>${loan.return_date ? new Date(loan.return_date).toLocaleDateString('fr-FR') : '-'}</td>
                            <td>${status}</td>
                            <td>${returnBtn}</td>
                        </tr>
                    `;
                }).join('');

                tableHtml = `
                    <table class="loans-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Livre ID</th>
                                <th>Date emprunt</th>
                                <th>Échéance</th>
                                <th>Retour</th>
                                <th>Statut</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                `;
            }

            UI.setContent(`
                <div class="page-header">
                    <h2>Mes emprunts</h2>
                </div>
                ${tableHtml}
            `);
        } catch (_) {
            UI.setContent(`<p>Erreur lors du chargement des emprunts.</p>`);
        }
    },

    returnLoan: async function(loanId) {
        if (!confirm('Confirmer le retour de cet emprunt ?')) return;
        try {
            await Api.returnLoan(loanId);
            UI.showMessage('Emprunt retourné avec succès', 'success');
            App.loadLoansPage();
        } catch (_) {}
    },

    // Utilitaire d'échappement XSS
    _escape: function(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
