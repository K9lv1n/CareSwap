"""
CareSwap - Intergenerational Help & Skill Exchange Platform
Flask Application with Admin System
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ========================================
# Mock Database
# ========================================

# Users Database
users_db = {
    'senior@test.com': {
        'id': 1,
        'email': 'senior@test.com',
        'password': 'password123',
        'name': 'Mdm Tan Ah Lian',
        'type': 'senior',
        'phone': '+65 9123 4567',
        'bio': 'Retired teacher who loves cooking traditional dishes. Looking forward to learning technology from the young generation!',
        'aura_points': 550,
        'level': 3,
        'badges': [
            {'id': 'first_helper', 'name': 'First Helper', 'icon': '🌟', 'earned': '2024-01-15'},
            {'id': 'tech_learner', 'name': 'Tech Learner', 'icon': '📱', 'earned': '2024-02-20'},
            {'id': 'wisdom_sharer', 'name': 'Wisdom Sharer', 'icon': '📚', 'earned': '2024-03-10'}
        ],
        'rating': 4.8,
        'rating_count': 12,
        'completed_tasks': 12,
        'joined_date': '2024-01-10',
        'last_active': datetime.now().isoformat(),
        'status': 'active',  # active, banned, timeout
        'timeout_until': None,
        'ban_reason': None,
        'accessibility': {
            'font_size': 'large',
            'high_contrast': False,
            'voice_enabled': True,
            'reduced_motion': False
        },
        'privacy': {
            'profile_visibility': 'registered',  # public, registered, private
            'show_email': False,
            'show_phone': False,
            'allow_contact': True,
            'show_activity': True
        },
        'notifications': {
            'email_new_match': True,
            'email_messages': True,
            'email_weekly': False,
            'app_all': True
        },
        'skills_teach': ['Cooking', 'Dialect', 'History'],
        'skills_learn': ['Smartphone', 'Social Media', 'Online Banking']
    },
    'youth@test.com': {
        'id': 2,
        'email': 'youth@test.com',
        'password': 'password123',
        'name': 'Alex Tan Wei Ming',
        'type': 'youth',
        'phone': '+65 8765 4321',
        'bio': 'NUS Computer Science student passionate about helping seniors bridge the digital divide. Always happy to teach and learn!',
        'aura_points': 1820,
        'level': 8,
        'badges': [
            {'id': 'helper_star', 'name': 'Helper Star', 'icon': '⭐', 'earned': '2024-01-20'},
            {'id': 'tech_guru', 'name': 'Tech Guru', 'icon': '💻', 'earned': '2024-02-15'},
            {'id': 'community_champion', 'name': 'Community Champion', 'icon': '🏆', 'earned': '2024-03-01'},
            {'id': 'patient_teacher', 'name': 'Patient Teacher', 'icon': '🎓', 'earned': '2024-03-15'}
        ],
        'rating': 4.9,
        'rating_count': 35,
        'completed_tasks': 35,
        'joined_date': '2024-01-05',
        'last_active': datetime.now().isoformat(),
        'status': 'active',
        'timeout_until': None,
        'ban_reason': None,
        'accessibility': {
            'font_size': 'medium',
            'high_contrast': False,
            'voice_enabled': False,
            'reduced_motion': False
        },
        'privacy': {
            'profile_visibility': 'public',
            'show_email': True,
            'show_phone': False,
            'allow_contact': True,
            'show_activity': True
        },
        'notifications': {
            'email_new_match': True,
            'email_messages': True,
            'email_weekly': True,
            'app_all': True
        },
        'skills_teach': ['Technology', 'English', 'Social Media', 'Apps'],
        'skills_learn': ['Cooking', 'Gardening', 'Life Skills']
    }
}

# Admin Database
admins_db = {
    'admin@careswap.sg': {
        'id': 100,
        'email': 'admin@careswap.sg',
        'password': 'admin123',
        'name': 'System Administrator',
        'role': 'super_admin',  # super_admin, moderator
        'permissions': ['ban', 'kick', 'timeout', 'view_reports', 'manage_content', 'manage_admins'],
        'last_login': None
    }
}

# Requests Database
requests_db = [
    {
        'id': 1,
        'title': 'Help me set up WhatsApp',
        'description': 'I bought a new phone and don\'t know how to set up WhatsApp for my grandchildren. Need someone patient to teach me step by step.',
        'category': 'technology',
        'aura_points': 50,
        'difficulty': 'Easy',
        'status': 'Open',
        'user_type': 'Senior',
        'location': 'Online / Video Call',
        'posted_by': 'senior@test.com',
        'posted_date': '2024-12-08',
        'accepted_by': None
    },
    {
        'id': 2,
        'title': 'Need help with heavy groceries',
        'description': 'Cannot carry rice and oil back from the market. Need strong youth to help carry - will pay for transport.',
        'category': 'errands',
        'aura_points': 80,
        'difficulty': 'Medium',
        'status': 'Open',
        'user_type': 'Senior',
        'location': 'Blk 123 Tampines Ave 4',
        'posted_by': 'senior@test.com',
        'posted_date': '2024-12-07',
        'accepted_by': None
    },
    {
        'id': 3,
        'title': 'Teach me basic phone camera + I teach you Hainanese Chicken Rice',
        'description': 'Would like to learn how to take a clear photo of my cat. Can teach you how to cook authentic Hainanese Chicken Rice in return - secret family recipe!',
        'category': 'skill_swap',
        'aura_points': 120,
        'difficulty': 'Medium',
        'status': 'Open',
        'user_type': 'CareSwap',
        'location': 'My Home Kitchen (Bedok)',
        'posted_by': 'senior@test.com',
        'posted_date': '2024-12-06',
        'accepted_by': None
    }
]

# Admin Action Logs
admin_logs = []

# Available Badges
all_badges = {
    'first_helper': {'name': 'First Helper', 'icon': '🌟', 'description': 'Completed your first help request'},
    'tech_learner': {'name': 'Tech Learner', 'icon': '📱', 'description': 'Learned 5 tech skills'},
    'tech_guru': {'name': 'Tech Guru', 'icon': '💻', 'description': 'Taught 10 tech sessions'},
    'wisdom_sharer': {'name': 'Wisdom Sharer', 'icon': '📚', 'description': 'Shared traditional knowledge'},
    'helper_star': {'name': 'Helper Star', 'icon': '⭐', 'description': 'Received 5-star ratings 10 times'},
    'community_champion': {'name': 'Community Champion', 'icon': '🏆', 'description': 'Top helper of the month'},
    'patient_teacher': {'name': 'Patient Teacher', 'icon': '🎓', 'description': 'Praised for patience 5 times'},
    'super_helper': {'name': 'Super Helper', 'icon': '🦸', 'description': 'Completed 50 tasks'},
    'first_swap': {'name': 'First Swap', 'icon': '🔄', 'description': 'Completed first skill swap'},
    'social_butterfly': {'name': 'Social Butterfly', 'icon': '🦋', 'description': 'Connected with 10 users'}
}


# ========================================
# Helper Functions
# ========================================

def get_current_user():
    """Get the current logged in user from session."""
    if 'user_email' in session:
        return users_db.get(session['user_email'])
    return None

def get_current_admin():
    """Get the current logged in admin from session."""
    if 'admin_email' in session:
        return admins_db.get(session['admin_email'])
    return None

def is_user_accessible(user):
    """Check if user can access the platform (not banned/timed out)."""
    if user['status'] == 'banned':
        return False, 'Your account has been banned.'
    if user['status'] == 'timeout':
        if user['timeout_until']:
            timeout_end = datetime.fromisoformat(user['timeout_until'])
            if datetime.now() < timeout_end:
                remaining = timeout_end - datetime.now()
                return False, f'Your account is in timeout. Access will be restored in {remaining.seconds // 3600} hours.'
            else:
                # Timeout expired, restore access
                user['status'] = 'active'
                user['timeout_until'] = None
    return True, None

def log_admin_action(admin_email, action, target_user, details=''):
    """Log an admin action for audit trail."""
    admin_logs.append({
        'timestamp': datetime.now().isoformat(),
        'admin': admin_email,
        'action': action,
        'target': target_user,
        'details': details
    })


# ========================================
# Decorators
# ========================================

def login_required(f):
    """Require user login to access route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = get_current_user()
        if user:
            accessible, message = is_user_accessible(user)
            if not accessible:
                session.clear()
                flash(message, 'danger')
                return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Require admin login to access route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_email' not in session:
            flash('Admin access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ========================================
# Context Processors
# ========================================

@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {
        'current_user': get_current_user(),
        'current_admin': get_current_admin(),
        'now': datetime.now()
    }


# ========================================
# Public Routes
# ========================================

@app.route('/')
def landing():
    """Landing page."""
    stats = {
        'users': len(users_db),
        'tasks': sum(1 for r in requests_db if r['status'] == 'Completed'),
        'active_requests': sum(1 for r in requests_db if r['status'] == 'Open')
    }
    return render_template('landing.html', stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        if email in users_db and users_db[email]['password'] == password:
            user = users_db[email]
            
            # Check if user is banned or timed out
            accessible, message = is_user_accessible(user)
            if not accessible:
                flash(message, 'danger')
                return render_template('login.html')
            
            # Set session
            session['user_email'] = email
            session['user_type'] = user['type']
            session['user_name'] = user['name']
            
            # Update last active
            user['last_active'] = datetime.now().isoformat()
            
            flash(f'Welcome back, {user["name"]}!', 'success')
            
            if user['type'] == 'senior':
                return redirect(url_for('senior_dashboard'))
            else:
                return redirect(url_for('youth_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page."""
    user_type = request.args.get('type', '')
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        user_type = request.form.get('user_type', 'youth')
        
        if email in users_db:
            flash('Email already exists. Please login instead.', 'warning')
            return redirect(url_for('login'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html', user_type=user_type)
        
        # Create new user
        new_user = {
            'id': len(users_db) + 1,
            'email': email,
            'password': password,
            'name': name,
            'type': user_type,
            'phone': '',
            'bio': '',
            'aura_points': 100,  # Welcome bonus
            'level': 1,
            'badges': [{'id': 'newcomer', 'name': 'Newcomer', 'icon': '🌱', 'earned': datetime.now().strftime('%Y-%m-%d')}],
            'rating': 0,
            'rating_count': 0,
            'completed_tasks': 0,
            'joined_date': datetime.now().strftime('%Y-%m-%d'),
            'last_active': datetime.now().isoformat(),
            'status': 'active',
            'timeout_until': None,
            'ban_reason': None,
            'accessibility': {
                'font_size': 'large' if user_type == 'senior' else 'medium',
                'high_contrast': user_type == 'senior',
                'voice_enabled': user_type == 'senior',
                'reduced_motion': False
            },
            'privacy': {
                'profile_visibility': 'registered',
                'show_email': False,
                'show_phone': False,
                'allow_contact': True,
                'show_activity': True
            },
            'notifications': {
                'email_new_match': True,
                'email_messages': True,
                'email_weekly': False,
                'app_all': True
            },
            'skills_teach': [],
            'skills_learn': []
        }
        
        users_db[email] = new_user
        
        # Set session
        session['user_email'] = email
        session['user_type'] = user_type
        session['user_name'] = name
        
        flash('Welcome to CareSwap! You earned 100 AURA points as a welcome bonus! 🎉', 'success')
        return redirect(url_for('onboarding'))
    
    return render_template('signup.html', user_type=user_type)

@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('landing'))


# ========================================
# User Routes
# ========================================

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    """Onboarding page for new users."""
    user = get_current_user()
    
    if request.method == 'POST':
        # Update accessibility settings
        user['accessibility']['font_size'] = request.form.get('font_size', 'medium')
        user['accessibility']['high_contrast'] = request.form.get('high_contrast') == 'on'
        user['accessibility']['voice_enabled'] = request.form.get('voice_enabled') == 'on'
        
        # Update bio
        user['bio'] = request.form.get('bio', '')
        
        # Update skills
        skills_teach = request.form.getlist('skills_teach')
        skills_learn = request.form.getlist('skills_learn')
        user['skills_teach'] = skills_teach
        user['skills_learn'] = skills_learn
        
        flash('Setup complete! Start exploring CareSwap.', 'success')
        
        if user['type'] == 'senior':
            return redirect(url_for('senior_dashboard'))
        else:
            return redirect(url_for('youth_dashboard'))
    
    return render_template('onboarding.html', user=user)

@app.route('/profile')
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id=None):
    """User profile page."""
    current_user = get_current_user()
    
    if user_id:
        # Viewing another user's profile
        target_user = None
        for email, user in users_db.items():
            if user['id'] == user_id:
                target_user = user
                break
        
        if not target_user:
            flash('User not found.', 'danger')
            return redirect(url_for('landing'))
        
        # Check privacy settings
        visibility = target_user['privacy']['profile_visibility']
        if visibility == 'private' and target_user['id'] != current_user['id']:
            flash('This profile is private.', 'warning')
            return redirect(url_for('landing'))
        
        return render_template('profile.html', user=target_user, is_own_profile=False, all_badges=all_badges)
    
    return render_template('profile.html', user=current_user, is_own_profile=True, all_badges=all_badges)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page."""
    user = get_current_user()
    
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'accessibility':
            user['accessibility']['font_size'] = request.form.get('font_size', 'medium')
            user['accessibility']['high_contrast'] = request.form.get('high_contrast') == 'on'
            user['accessibility']['voice_enabled'] = request.form.get('voice_enabled') == 'on'
            user['accessibility']['reduced_motion'] = request.form.get('reduced_motion') == 'on'
            flash('Accessibility settings updated!', 'success')
        
        elif action == 'account':
            user['name'] = request.form.get('name', user['name'])
            user['phone'] = request.form.get('phone', '')
            user['bio'] = request.form.get('bio', '')
            session['user_name'] = user['name']
            flash('Account information updated!', 'success')
        
        elif action == 'privacy':
            user['privacy']['profile_visibility'] = request.form.get('profile_visibility', 'registered')
            user['privacy']['show_email'] = request.form.get('show_email') == 'on'
            user['privacy']['show_phone'] = request.form.get('show_phone') == 'on'
            user['privacy']['allow_contact'] = request.form.get('allow_contact') == 'on'
            user['privacy']['show_activity'] = request.form.get('show_activity') == 'on'
            flash('Privacy settings updated!', 'success')
        
        elif action == 'notifications':
            user['notifications']['email_new_match'] = request.form.get('email_new_match') == 'on'
            user['notifications']['email_messages'] = request.form.get('email_messages') == 'on'
            user['notifications']['email_weekly'] = request.form.get('email_weekly') == 'on'
            user['notifications']['app_all'] = request.form.get('app_all') == 'on'
            flash('Notification preferences updated!', 'success')
        
        elif action == 'password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if user['password'] != current_password:
                flash('Current password is incorrect.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
            else:
                user['password'] = new_password
                flash('Password changed successfully!', 'success')
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', user=user)


# ========================================
# Dashboard Routes
# ========================================

@app.route('/dashboard/senior')
@login_required
def senior_dashboard():
    """Senior dashboard."""
    user = get_current_user()
    if user['type'] != 'senior':
        return redirect(url_for('youth_dashboard'))
    
    my_requests = [r for r in requests_db if r['posted_by'] == session['user_email']]
    return render_template('senior_dashboard.html', user=user, requests=my_requests)

@app.route('/dashboard/youth')
@login_required
def youth_dashboard():
    """Youth dashboard."""
    user = get_current_user()
    if user['type'] != 'youth':
        return redirect(url_for('senior_dashboard'))
    
    open_requests = [r for r in requests_db if r['status'] == 'Open']
    my_accepted = [r for r in requests_db if r.get('accepted_by') == session['user_email']]
    
    return render_template('youth_dashboard.html', user=user, requests=open_requests, my_tasks=my_accepted)


# ========================================
# Request Routes
# ========================================

@app.route('/request/new', methods=['GET', 'POST'])
@login_required
def post_request():
    """Create a new help request."""
    user = get_current_user()
    
    if request.method == 'POST':
        # Calculate AURA points based on difficulty
        difficulty = request.form.get('difficulty', 'Medium')
        points_map = {'Easy': 50, 'Medium': 70, 'Hard': 120}
        aura_points = points_map.get(difficulty, 50)
        
        new_request = {
            'id': len(requests_db) + 1,
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'category': request.form.get('category', 'general'),
            'aura_points': aura_points,
            'difficulty': difficulty,
            'status': 'Open',
            'user_type': 'CareSwap' if request.form.get('is_swap') else 'Senior',
            'location': request.form.get('location', 'Online'),
            'posted_by': session['user_email'],
            'posted_date': datetime.now().strftime('%Y-%m-%d'),
            'accepted_by': None
        }
        
        requests_db.append(new_request)
        flash('Your request has been posted!', 'success')
        
        if user['type'] == 'senior':
            return redirect(url_for('senior_dashboard'))
        return redirect(url_for('youth_dashboard'))
    
    return render_template('post_request.html', user=user)

@app.route('/request/<int:request_id>/accept')
@login_required
def accept_request(request_id):
    """Accept a help request."""
    user = get_current_user()
    
    for req in requests_db:
        if req['id'] == request_id and req['status'] == 'Open':
            req['status'] = 'In Progress'
            req['accepted_by'] = session['user_email']
            
            # Award points
            user['aura_points'] += req['aura_points']
            
            flash(f'Request accepted! You earned {req["aura_points"]} AURA points!', 'success')
            break
    
    return redirect(url_for('youth_dashboard'))

@app.route('/request/<int:request_id>/complete')
@login_required
def complete_request(request_id):
    """Mark a request as completed."""
    for req in requests_db:
        if req['id'] == request_id:
            req['status'] = 'Completed'
            flash('Task marked as complete! Great job!', 'success')
            break
    
    user = get_current_user()
    if user['type'] == 'senior':
        return redirect(url_for('senior_dashboard'))
    return redirect(url_for('youth_dashboard'))


# ========================================
# Admin Routes
# ========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        if email in admins_db and admins_db[email]['password'] == password:
            session['admin_email'] = email
            admins_db[email]['last_login'] = datetime.now().isoformat()
            flash('Welcome, Administrator!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_email', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    admin = get_current_admin()
    
    # Stats
    stats = {
        'total_users': len(users_db),
        'seniors': sum(1 for u in users_db.values() if u['type'] == 'senior'),
        'youths': sum(1 for u in users_db.values() if u['type'] == 'youth'),
        'active_users': sum(1 for u in users_db.values() if u['status'] == 'active'),
        'banned_users': sum(1 for u in users_db.values() if u['status'] == 'banned'),
        'timeout_users': sum(1 for u in users_db.values() if u['status'] == 'timeout'),
        'total_requests': len(requests_db),
        'open_requests': sum(1 for r in requests_db if r['status'] == 'Open'),
        'completed_requests': sum(1 for r in requests_db if r['status'] == 'Completed')
    }
    
    # User list
    user_list = list(users_db.values())
    
    # Recent admin actions
    recent_logs = admin_logs[-10:][::-1]  # Last 10, reversed
    
    return render_template('admin_dashboard.html', 
                         admin=admin, 
                         stats=stats, 
                         users=user_list,
                         logs=recent_logs)

@app.route('/admin/user/<int:user_id>/ban', methods=['POST'])
@admin_required
def admin_ban_user(user_id):
    """Ban a user."""
    reason = request.form.get('reason', 'Violation of community guidelines')
    
    for email, user in users_db.items():
        if user['id'] == user_id:
            user['status'] = 'banned'
            user['ban_reason'] = reason
            
            log_admin_action(session['admin_email'], 'ban', email, reason)
            flash(f'User {user["name"]} has been banned.', 'warning')
            break
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/unban', methods=['POST'])
@admin_required
def admin_unban_user(user_id):
    """Unban a user."""
    for email, user in users_db.items():
        if user['id'] == user_id:
            user['status'] = 'active'
            user['ban_reason'] = None
            
            log_admin_action(session['admin_email'], 'unban', email)
            flash(f'User {user["name"]} has been unbanned.', 'success')
            break
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/timeout', methods=['POST'])
@admin_required
def admin_timeout_user(user_id):
    """Timeout a user for a specified duration."""
    hours = int(request.form.get('hours', 24))
    reason = request.form.get('reason', 'Temporary restriction')
    
    for email, user in users_db.items():
        if user['id'] == user_id:
            user['status'] = 'timeout'
            user['timeout_until'] = (datetime.now() + timedelta(hours=hours)).isoformat()
            user['ban_reason'] = reason
            
            log_admin_action(session['admin_email'], 'timeout', email, f'{hours} hours - {reason}')
            flash(f'User {user["name"]} has been put in timeout for {hours} hours.', 'warning')
            break
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/kick', methods=['POST'])
@admin_required
def admin_kick_user(user_id):
    """Force logout a user (kick)."""
    for email, user in users_db.items():
        if user['id'] == user_id:
            # In a real app, you'd invalidate their session token
            # For now, we just log the action
            log_admin_action(session['admin_email'], 'kick', email, 'Force logout')
            flash(f'User {user["name"]} has been kicked (session invalidated).', 'info')
            break
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/warn', methods=['POST'])
@admin_required
def admin_warn_user(user_id):
    """Send a warning to a user."""
    message = request.form.get('message', 'Please follow community guidelines.')
    
    for email, user in users_db.items():
        if user['id'] == user_id:
            log_admin_action(session['admin_email'], 'warn', email, message)
            flash(f'Warning sent to {user["name"]}.', 'info')
            break
    
    return redirect(url_for('admin_dashboard'))


# ========================================
# API Routes (for AJAX)
# ========================================

@app.route('/api/user/accessibility', methods=['POST'])
@login_required
def api_update_accessibility():
    """Update accessibility settings via AJAX."""
    user = get_current_user()
    data = request.get_json()
    
    if 'font_size' in data:
        user['accessibility']['font_size'] = data['font_size']
    if 'high_contrast' in data:
        user['accessibility']['high_contrast'] = data['high_contrast']
    if 'voice_enabled' in data:
        user['accessibility']['voice_enabled'] = data['voice_enabled']
    if 'reduced_motion' in data:
        user['accessibility']['reduced_motion'] = data['reduced_motion']
    
    return jsonify({'success': True, 'message': 'Settings updated'})


# ========================================
# Error Handlers
# ========================================

@app.errorhandler(404)
def not_found(e):
    """404 error handler."""
    return render_template('landing.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    """500 error handler."""
    return render_template('landing.html', error='Something went wrong'), 500


# ========================================
# Run Application
# ========================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)