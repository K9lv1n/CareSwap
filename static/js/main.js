/**
 * CareSwap JavaScript Utilities
 * Includes accessibility, dark mode, and interactive features
 */

(function () {
    'use strict';

    // ===================================
    // Theme Management (Dark Mode)
    // ===================================

    const Theme = {
        init() {
            // Get saved theme or detect system preference
            const savedTheme = localStorage.getItem('careswap-theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

            if (savedTheme) {
                this.setTheme(savedTheme);
            } else if (prefersDark) {
                this.setTheme('dark');
            } else {
                this.setTheme('light');
            }

            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('careswap-theme')) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });

            // Bind toggle buttons
            document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
                btn.addEventListener('click', () => this.toggle());
            });
        },

        setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            document.body.classList.remove('dark-mode', 'light-mode');
            document.body.classList.add(theme + '-mode');
            localStorage.setItem('careswap-theme', theme);

            // Update toggle icons
            document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
                btn.textContent = theme === 'dark' ? '☀️' : '🌙';
                btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
            });
        },

        toggle() {
            const current = localStorage.getItem('careswap-theme') || 'light';
            this.setTheme(current === 'dark' ? 'light' : 'dark');
        },

        get() {
            return localStorage.getItem('careswap-theme') || 'light';
        }
    };

    // ===================================
    // Accessibility Settings
    // ===================================

    const Accessibility = {
        defaults: {
            fontSize: 'medium',
            highContrast: false,
            reducedMotion: false
        },

        init() {
            this.load();
            this.bindEvents();
        },

        load() {
            const settings = this.getSettings();
            this.applyFontSize(settings.fontSize);
            this.applyHighContrast(settings.highContrast);
            this.applyReducedMotion(settings.reducedMotion);
        },

        getSettings() {
            try {
                const saved = localStorage.getItem('careswap-accessibility');
                return saved ? { ...this.defaults, ...JSON.parse(saved) } : this.defaults;
            } catch (e) {
                return this.defaults;
            }
        },

        saveSettings(settings) {
            localStorage.setItem('careswap-accessibility', JSON.stringify(settings));
        },

        applyFontSize(size) {
            document.body.classList.remove('font-size-small', 'font-size-medium', 'font-size-large', 'font-size-xlarge');
            document.body.classList.add('font-size-' + size);

            // Update active state on buttons
            document.querySelectorAll('[data-font-size]').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.fontSize === size);
            });

            // Update settings
            const settings = this.getSettings();
            settings.fontSize = size;
            this.saveSettings(settings);
        },

        applyHighContrast(enabled) {
            document.body.classList.toggle('high-contrast', enabled);

            // Update toggles
            document.querySelectorAll('[name="high_contrast"]').forEach(input => {
                input.checked = enabled;
            });

            const settings = this.getSettings();
            settings.highContrast = enabled;
            this.saveSettings(settings);
        },

        applyReducedMotion(enabled) {
            document.body.classList.toggle('reduced-motion', enabled);

            // Update toggles
            document.querySelectorAll('[name="reduced_motion"]').forEach(input => {
                input.checked = enabled;
            });

            const settings = this.getSettings();
            settings.reducedMotion = enabled;
            this.saveSettings(settings);
        },

        bindEvents() {
            // Font size buttons
            document.querySelectorAll('[data-font-size]').forEach(btn => {
                btn.addEventListener('click', () => {
                    this.applyFontSize(btn.dataset.fontSize);
                    Toast.success('Font size changed to ' + btn.dataset.fontSize);
                });
            });

            // High contrast toggle
            document.querySelectorAll('[name="high_contrast"]').forEach(input => {
                input.addEventListener('change', () => {
                    this.applyHighContrast(input.checked);
                });
            });

            // Reduced motion toggle
            document.querySelectorAll('[name="reduced_motion"]').forEach(input => {
                input.addEventListener('change', () => {
                    this.applyReducedMotion(input.checked);
                });
            });

            // Font size radio buttons (for settings page)
            document.querySelectorAll('input[name="font_size"]').forEach(input => {
                input.addEventListener('change', () => {
                    this.applyFontSize(input.value);
                });
            });
        }
    };

    // ===================================
    // Toast Notifications
    // ===================================

    const Toast = {
        container: null,

        init() {
            this.container = document.querySelector('.toast-container');
            if (!this.container) {
                this.container = document.createElement('div');
                this.container.className = 'toast-container';
                this.container.setAttribute('aria-live', 'polite');
                document.body.appendChild(this.container);
            }
        },

        show(message, type = 'info', duration = 4000) {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;

            const icons = {
                success: '✅',
                error: '❌',
                warning: '⚠️',
                info: 'ℹ️'
            };

            toast.innerHTML = `
                <span class="toast-icon">${icons[type] || icons.info}</span>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.remove()" aria-label="Close">&times;</button>
            `;

            this.container.appendChild(toast);

            // Auto remove
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.style.animation = 'fadeOut 0.3s ease forwards';
                    setTimeout(() => toast.remove(), 300);
                }
            }, duration);

            return toast;
        },

        success(message) { return this.show(message, 'success'); },
        error(message) { return this.show(message, 'error'); },
        warning(message) { return this.show(message, 'warning'); },
        info(message) { return this.show(message, 'info'); }
    };

    // ===================================
    // Modal Management
    // ===================================

    const Modal = {
        activeModal: null,

        open(id) {
            const modal = document.getElementById(id);
            const backdrop = document.querySelector('.modal-backdrop');

            if (modal) {
                modal.classList.add('active');
                if (backdrop) backdrop.classList.add('active');
                this.activeModal = modal;

                // Focus trap
                const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                if (focusable.length) focusable[0].focus();

                // Close on escape
                document.addEventListener('keydown', this.handleEscape);
            }
        },

        close(id) {
            const modal = id ? document.getElementById(id) : this.activeModal;
            const backdrop = document.querySelector('.modal-backdrop');

            if (modal) {
                modal.classList.remove('active');
                if (backdrop) backdrop.classList.remove('active');
                this.activeModal = null;
                document.removeEventListener('keydown', this.handleEscape);
            }
        },

        handleEscape(e) {
            if (e.key === 'Escape') {
                Modal.close();
            }
        },

        init() {
            // Close modal on backdrop click
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                backdrop.addEventListener('click', () => this.close());
            });

            // Close buttons
            document.querySelectorAll('[data-modal-close]').forEach(btn => {
                btn.addEventListener('click', () => this.close(btn.dataset.modalClose));
            });

            // Open buttons
            document.querySelectorAll('[data-modal-open]').forEach(btn => {
                btn.addEventListener('click', () => this.open(btn.dataset.modalOpen));
            });
        }
    };

    // ===================================
    // Dropdown Management
    // ===================================

    const Dropdown = {
        init() {
            document.querySelectorAll('[data-dropdown-toggle]').forEach(trigger => {
                trigger.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const dropdown = trigger.closest('.dropdown');

                    // Close other dropdowns
                    document.querySelectorAll('.dropdown.active').forEach(d => {
                        if (d !== dropdown) d.classList.remove('active');
                    });

                    dropdown.classList.toggle('active');
                });
            });

            // Close on outside click
            document.addEventListener('click', () => {
                document.querySelectorAll('.dropdown.active').forEach(d => {
                    d.classList.remove('active');
                });
            });
        }
    };

    // ===================================
    // Mobile Navigation
    // ===================================

    const MobileNav = {
        init() {
            const toggle = document.querySelector('.navbar-toggle');
            const nav = document.querySelector('.navbar-nav');

            if (toggle && nav) {
                toggle.addEventListener('click', () => {
                    nav.classList.toggle('active');
                    const expanded = nav.classList.contains('active');
                    toggle.setAttribute('aria-expanded', expanded);
                });
            }
        }
    };

    // ===================================
    // Form Validation
    // ===================================

    const FormValidation = {
        init() {
            document.querySelectorAll('form[data-validate]').forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!this.validateForm(form)) {
                        e.preventDefault();
                    }
                });

                // Real-time validation
                form.querySelectorAll('input, textarea, select').forEach(input => {
                    input.addEventListener('blur', () => this.validateField(input));
                    input.addEventListener('input', () => {
                        if (input.classList.contains('is-invalid')) {
                            this.validateField(input);
                        }
                    });
                });
            });
        },

        validateForm(form) {
            let isValid = true;
            form.querySelectorAll('[required], [data-validate]').forEach(input => {
                if (!this.validateField(input)) isValid = false;
            });
            return isValid;
        },

        validateField(input) {
            let isValid = true;
            let message = '';

            // Required check
            if (input.hasAttribute('required') && !input.value.trim()) {
                isValid = false;
                message = 'This field is required';
            }

            // Email check
            if (isValid && input.type === 'email' && input.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value)) {
                    isValid = false;
                    message = 'Please enter a valid email address';
                }
            }

            // Min length check
            if (isValid && input.minLength > 0 && input.value.length < input.minLength) {
                isValid = false;
                message = `Must be at least ${input.minLength} characters`;
            }

            // Update UI
            input.classList.toggle('is-invalid', !isValid);
            input.classList.toggle('is-valid', isValid && input.value);

            // Show/hide error message
            let errorEl = input.parentElement.querySelector('.form-error');
            if (!isValid) {
                if (!errorEl) {
                    errorEl = document.createElement('div');
                    errorEl.className = 'form-error';
                    input.parentElement.appendChild(errorEl);
                }
                errorEl.textContent = message;
            } else if (errorEl) {
                errorEl.remove();
            }

            return isValid;
        }
    };

    // ===================================
    // Password Toggle
    // ===================================

    const PasswordToggle = {
        init() {
            document.querySelectorAll('[data-toggle-password]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const input = document.getElementById(btn.dataset.togglePassword);
                    if (input) {
                        const isPassword = input.type === 'password';
                        input.type = isPassword ? 'text' : 'password';
                        btn.textContent = isPassword ? '🙈' : '👁️';
                        btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
                    }
                });
            });
        }
    };

    // ===================================
    // Animated Counter
    // ===================================

    const AnimatedCounter = {
        init() {
            const counters = document.querySelectorAll('[data-counter]');

            if ('IntersectionObserver' in window && counters.length) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.animate(entry.target);
                            observer.unobserve(entry.target);
                        }
                    });
                }, { threshold: 0.5 });

                counters.forEach(counter => observer.observe(counter));
            } else {
                counters.forEach(counter => this.animate(counter));
            }
        },

        animate(el) {
            const target = parseInt(el.dataset.counter, 10);
            const duration = parseInt(el.dataset.duration, 10) || 1500;
            const start = 0;
            const startTime = performance.now();

            const step = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic

                el.textContent = Math.floor(eased * target);

                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    el.textContent = target;
                }
            };

            requestAnimationFrame(step);
        }
    };

    // ===================================
    // Smooth Scroll
    // ===================================

    const SmoothScroll = {
        init() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => {
                    const targetId = anchor.getAttribute('href');
                    if (targetId !== '#') {
                        const target = document.querySelector(targetId);
                        if (target) {
                            e.preventDefault();
                            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }
                });
            });
        }
    };

    // ===================================
    // Character Counter
    // ===================================

    const CharacterCounter = {
        init() {
            document.querySelectorAll('[data-maxlength]').forEach(input => {
                const max = parseInt(input.dataset.maxlength, 10);

                // Create counter element
                const counter = document.createElement('div');
                counter.className = 'character-counter';
                counter.style.cssText = 'font-size: 0.85rem; color: var(--text-muted); text-align: right; margin-top: 4px;';
                input.parentElement.appendChild(counter);

                const update = () => {
                    const remaining = max - input.value.length;
                    counter.textContent = `${input.value.length}/${max}`;
                    counter.style.color = remaining < 20 ? 'var(--color-warning)' : 'var(--text-muted)';
                    if (remaining < 0) counter.style.color = 'var(--color-danger)';
                };

                input.addEventListener('input', update);
                update();
            });
        }
    };

    // ===================================
    // Confirm Actions
    // ===================================

    const ConfirmAction = {
        init() {
            document.querySelectorAll('[data-confirm]').forEach(el => {
                el.addEventListener('click', (e) => {
                    const message = el.dataset.confirm;
                    if (!confirm(message)) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                });
            });
        }
    };

    // ===================================
    // Initialize Everything
    // ===================================

    document.addEventListener('DOMContentLoaded', () => {
        Theme.init();
        Accessibility.init();
        Toast.init();
        Modal.init();
        Dropdown.init();
        MobileNav.init();
        FormValidation.init();
        PasswordToggle.init();
        AnimatedCounter.init();
        SmoothScroll.init();
        CharacterCounter.init();
        ConfirmAction.init();
    });

    // ===================================
    // Expose Global API
    // ===================================

    window.CareSwap = {
        Theme,
        Accessibility,
        Toast,
        Modal,
        Dropdown
    };

})();
