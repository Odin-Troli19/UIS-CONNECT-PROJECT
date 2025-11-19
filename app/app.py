from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os
from functools import wraps
from config import config, Config
import db_utils as db

app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])
Config.init_app(app)

DATABASE = app.config['DATABASE']

# ==================== DECORATORS ====================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_user():
    """Inject current user and unread counts into all templates"""
    if 'user_id' in session:
        user = db.get_user_by_id(DATABASE, session['user_id'])
        unread_notifications = db.get_unread_count(DATABASE, session['user_id'])
        unread_messages = sum(
            conv['unread_count'] 
            for conv in db.get_user_conversations(DATABASE, session['user_id'])
        )
        return dict(
            current_user=user,
            unread_notifications=unread_notifications,
            unread_messages=unread_messages
        )
    return dict(current_user=None, unread_notifications=0, unread_messages=0)

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        major = request.form.get('major', '').strip()
        interests = request.form.get('interests', '').strip()
        bio = request.form.get('bio', '').strip()
        study_level = request.form.get('study_level')
        campus = request.form.get('campus', '').strip()
        student_number = request.form.get('student_number', '').strip()
        
        # Validation
        if not username or not password or not email:
            flash('Username, email, and password are required.', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))
        
        # Check if username or email exists
        if db.get_user_by_username(DATABASE, username):
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
        
        # Create user
        user_id = db.create_user(
            DATABASE, username, email, password, major, interests, 
            bio, study_level, campus, student_number
        )
        
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash('Registration successful! Welcome to UIS-Connect!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Registration failed. Email might already be in use.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        user = db.authenticate_user(DATABASE, username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            db.update_last_login(DATABASE, user['id'])
            
            flash(f'Welcome back, {user["username"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('index'))

# ==================== HOME & FEED ROUTES ====================

@app.route('/')
def index():
    """Home page with post feed"""
    page = request.args.get('page', 1, type=int)
    posts_per_page = app.config['POSTS_PER_PAGE']
    offset = (page - 1) * posts_per_page
    
    user_id = session.get('user_id')
    posts = db.get_all_posts(DATABASE, user_id, limit=posts_per_page, offset=offset)
    
    trending_tags = db.get_trending_hashtags(DATABASE, limit=5)
    
    return render_template('index.html', posts=posts, page=page, trending_tags=trending_tags)

@app.route('/search')
def search():
    """Search posts and users"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    
    results = {
        'users': [],
        'posts': [],
        'hashtags': []
    }
    
    if query:
        if search_type in ['all', 'users']:
            results['users'] = db.search_users(DATABASE, query, limit=20)
        
        if search_type in ['all', 'hashtags'] and query.startswith('#'):
            tag = query[1:]
            results['posts'] = db.search_posts_by_hashtag(DATABASE, tag, limit=30)
            results['hashtags'] = [{'tag': tag}]
    
    return render_template('search.html', query=query, results=results, search_type=search_type)

# ==================== POST ROUTES ====================

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create a new post"""
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        post_type = request.form.get('post_type', 'general')
        visibility = request.form.get('visibility', 'public')
        
        if not content:
            flash('Post content cannot be empty.', 'error')
            return redirect(url_for('new_post'))
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                import time
                filename = f"{int(time.time())}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = filename
        
        post_id = db.create_post(DATABASE, session['user_id'], content, post_type, visibility, image_url)
        flash('Post created successfully!', 'success')
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('new_post.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View a single post with comments"""
    user_id = session.get('user_id')
    post = db.get_post_by_id(DATABASE, post_id, user_id)
    
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    
    comments = db.get_post_comments(DATABASE, post_id)
    
    return render_template('post.html', post=post, comments=comments)

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a post"""
    post = db.get_post_by_id(DATABASE, post_id, session['user_id'])
    
    if not post or post['user_id'] != session['user_id']:
        flash('You can only edit your own posts.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        post_type = request.form.get('post_type', 'general')
        
        if not content:
            flash('Post content cannot be empty.', 'error')
            return redirect(url_for('edit_post', post_id=post_id))
        
        db.update_post(DATABASE, post_id, content, post_type)
        flash('Post updated successfully!', 'success')
        return redirect(url_for('view_post', post_id=post_id))
    
    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post"""
    post = db.get_post_by_id(DATABASE, post_id, session['user_id'])
    
    if not post or post['user_id'] != session['user_id']:
        flash('You can only delete your own posts.', 'error')
        return redirect(url_for('index'))
    
    db.delete_post(DATABASE, post_id)
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('profile'))

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like/unlike a post"""
    action = db.toggle_like_post(DATABASE, post_id, session['user_id'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'action': action})
    
    flash(f'Post {action}!', 'info')
    return redirect(request.referrer or url_for('index'))

@app.route('/post/<int:post_id>/save', methods=['POST'])
@login_required
def save_post(post_id):
    """Save/unsave a post"""
    action = db.toggle_save_post(DATABASE, session['user_id'], post_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'action': action})
    
    flash(f'Post {action}!', 'info')
    return redirect(request.referrer or url_for('index'))

@app.route('/saved-posts')
@login_required
def saved_posts():
    """View saved posts"""
    posts = db.get_saved_posts(DATABASE, session['user_id'], limit=50)
    return render_template('saved_posts.html', posts=posts)

# ==================== COMMENT ROUTES ====================

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a post"""
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    
    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    db.add_comment(DATABASE, post_id, session['user_id'], content, parent_id)
    flash('Comment added!', 'success')
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """Like/unlike a comment"""
    action = db.toggle_like_comment(DATABASE, comment_id, session['user_id'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'action': action})
    
    flash(f'Comment {action}!', 'info')
    return redirect(request.referrer or url_for('index'))

# ==================== PROFILE ROUTES ====================

@app.route('/profile')
@login_required
def profile():
    """View own profile"""
    user = db.get_user_by_id(DATABASE, session['user_id'])
    posts = db.get_user_posts(DATABASE, session['user_id'], limit=50)
    stats = db.get_user_stats(DATABASE, session['user_id'])
    
    return render_template('profile.html', user=user, posts=posts, stats=stats, is_own_profile=True)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit profile"""
    if request.method == 'POST':
        updates = {
            'email': request.form.get('email', '').strip(),
            'major': request.form.get('major', '').strip(),
            'interests': request.form.get('interests', '').strip(),
            'bio': request.form.get('bio', '').strip(),
            'study_level': request.form.get('study_level'),
            'campus': request.form.get('campus', '').strip(),
            'student_number': request.form.get('student_number', '').strip(),
        }
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"profile_{session['user_id']}_{int(time.time())}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                updates['profile_picture'] = filename
        
        if db.update_user_profile(DATABASE, session['user_id'], **updates):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile.', 'error')
        
        return redirect(url_for('profile'))
    
    user = db.get_user_by_id(DATABASE, session['user_id'])
    return render_template('edit_profile.html', user=user)

@app.route('/user/<int:user_id>')
def view_user(user_id):
    """View another user's profile"""
    user = db.get_user_by_id(DATABASE, user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('index'))
    
    posts = db.get_user_posts(DATABASE, user_id, limit=50)
    stats = db.get_user_stats(DATABASE, user_id)
    
    # Check friendship status
    is_friend = False
    friend_request_sent = False
    if 'user_id' in session and session['user_id'] != user_id:
        is_friend = db.are_friends(DATABASE, session['user_id'], user_id)
    
    is_own_profile = 'user_id' in session and session['user_id'] == user_id
    
    return render_template(
        'profile.html', 
        user=user, 
        posts=posts, 
        stats=stats,
        is_own_profile=is_own_profile,
        is_friend=is_friend
    )

@app.route('/users')
def users():
    """View all users with filtering and sorting"""
    sort_by = request.args.get('sort', 'username')
    major_filter = request.args.get('major')
    level_filter = request.args.get('level')
    campus_filter = request.args.get('campus')
    
    # For now, just search all users
    # In a real app, you'd implement proper filtering
    from db_utils import get_db_connection
    conn = get_db_connection(DATABASE)
    
    query = """
        SELECT id, username, major, interests, study_level, campus, profile_picture
        FROM users
        WHERE is_active = 1
    """
    params = []
    
    if major_filter:
        query += " AND major LIKE ?"
        params.append(f"%{major_filter}%")
    
    if level_filter:
        query += " AND study_level = ?"
        params.append(level_filter)
    
    if campus_filter:
        query += " AND campus LIKE ?"
        params.append(f"%{campus_filter}%")
    
    allowed_sort = ['username', 'major', 'study_level', 'campus']
    if sort_by in allowed_sort:
        query += f" ORDER BY {sort_by} ASC"
    else:
        query += " ORDER BY username ASC"
    
    query += f" LIMIT {app.config['USERS_PER_PAGE']}"
    
    users_list = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('users.html', users=[dict(u) for u in users_list], sort_by=sort_by)

# ==================== FRIEND ROUTES ====================

@app.route('/friends')
@login_required
def friends():
    """View friends list"""
    friends_list = db.get_user_friends(DATABASE, session['user_id'])
    return render_template('friends.html', friends=friends_list)

@app.route('/friends/requests')
@login_required
def friend_requests():
    """View friend requests"""
    requests = db.get_friend_requests(DATABASE, session['user_id'])
    return render_template('friend_requests.html', requests=requests)

@app.route('/friends/send/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    """Send a friend request"""
    if user_id == session['user_id']:
        flash('You cannot send a friend request to yourself.', 'error')
        return redirect(url_for('users'))
    
    if db.send_friend_request(DATABASE, session['user_id'], user_id):
        flash('Friend request sent!', 'success')
        # Create notification
        user = db.get_user_by_id(DATABASE, session['user_id'])
        db.create_notification(
            DATABASE, user_id, 
            f"{user['username']} sent you a friend request",
            'friend_request', session['user_id']
        )
    else:
        flash('Friend request already sent or you are already friends.', 'info')
    
    return redirect(request.referrer or url_for('users'))

@app.route('/friends/respond/<int:friendship_id>/<action>', methods=['POST'])
@login_required
def respond_friend_request(friendship_id, action):
    """Accept or reject a friend request"""
    if action not in ['accepted', 'rejected']:
        flash('Invalid action.', 'error')
        return redirect(url_for('friend_requests'))
    
    db.respond_to_friend_request(DATABASE, friendship_id, action)
    flash(f'Friend request {action}!', 'success')
    return redirect(url_for('friend_requests'))

@app.route('/friends/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    """Remove a friend"""
    db.remove_friend(DATABASE, session['user_id'], user_id)
    flash('Friend removed.', 'info')
    return redirect(url_for('friends'))

# ==================== MESSAGING ROUTES ====================

@app.route('/messages')
@login_required
def messages():
    """View all conversations"""
    conversations = db.get_user_conversations(DATABASE, session['user_id'])
    return render_template('messages.html', conversations=conversations)

@app.route('/messages/<int:user_id>')
@login_required
def conversation(user_id):
    """View conversation with a specific user"""
    other_user = db.get_user_by_id(DATABASE, user_id)
    
    if not other_user:
        flash('User not found.', 'error')
        return redirect(url_for('messages'))
    
    conversation_messages = db.get_conversation(DATABASE, session['user_id'], user_id)
    
    # Mark messages as read
    db.mark_messages_read(DATABASE, session['user_id'], user_id)
    
    return render_template('conversation.html', other_user=other_user, messages=conversation_messages)

@app.route('/messages/send/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    """Send a message to a user"""
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Message cannot be empty.', 'error')
        return redirect(url_for('conversation', user_id=user_id))
    
    db.send_message(DATABASE, session['user_id'], user_id, content)
    
    # Create notification
    sender = db.get_user_by_id(DATABASE, session['user_id'])
    db.create_notification(
        DATABASE, user_id,
        f"New message from {sender['username']}",
        'message', session['user_id']
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    return redirect(url_for('conversation', user_id=user_id))

# ==================== NOTIFICATION ROUTES ====================

@app.route('/notifications')
@login_required
def notifications():
    """View all notifications"""
    all_notifications = db.get_user_notifications(DATABASE, session['user_id'], limit=50)
    return render_template('notifications.html', notifications=all_notifications)

@app.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    db.mark_notification_read(DATABASE, notification_id)
    return redirect(url_for('notifications'))

@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    db.mark_all_notifications_read(DATABASE, session['user_id'])
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications'))

# ==================== HASHTAG ROUTES ====================

@app.route('/hashtag/<tag>')
def hashtag(tag):
    """View posts with a specific hashtag"""
    posts = db.search_posts_by_hashtag(DATABASE, tag, limit=50)
    return render_template('hashtag.html', tag=tag, posts=posts)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)