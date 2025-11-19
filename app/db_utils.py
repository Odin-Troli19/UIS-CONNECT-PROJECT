import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

def get_db_connection(database_path):
    """Create and return a database connection"""
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== USER FUNCTIONS ====================

def create_user(db_path, username, email, password, major=None, interests=None, 
                bio=None, study_level=None, campus=None, student_number=None):
    """Create a new user"""
    conn = get_db_connection(db_path)
    password_hash = generate_password_hash(password)
    
    try:
        cursor = conn.execute("""
            INSERT INTO users (username, email, password_hash, major, interests, bio, 
                             study_level, campus, student_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, major, interests, bio, 
              study_level, campus, student_number))
        user_id = cursor.lastrowid
        
        # Create default user settings
        conn.execute("INSERT INTO user_settings (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return None
    finally:
        conn.close()

def authenticate_user(db_path, username, password):
    """Authenticate user with username and password"""
    conn = get_db_connection(db_path)
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1", 
        (username,)
    ).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user_by_id(db_path, user_id):
    """Get user by ID"""
    conn = get_db_connection(db_path)
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_username(db_path, username):
    """Get user by username"""
    conn = get_db_connection(db_path)
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_profile(db_path, user_id, **kwargs):
    """Update user profile"""
    allowed_fields = ['email', 'major', 'interests', 'bio', 'study_level', 
                     'campus', 'student_number', 'profile_picture']
    
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not updates:
        return False
    
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [user_id]
    
    conn = get_db_connection(db_path)
    try:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()

def update_last_login(db_path, user_id):
    """Update user's last login time"""
    conn = get_db_connection(db_path)
    conn.execute(
        "UPDATE users SET last_login = datetime('now') WHERE id = ?", 
        (user_id,)
    )
    conn.commit()
    conn.close()

def search_users(db_path, query, limit=50):
    """Search users by username, major, or interests"""
    conn = get_db_connection(db_path)
    search_pattern = f"%{query}%"
    users = conn.execute("""
        SELECT id, username, major, interests, study_level, campus, profile_picture
        FROM users
        WHERE (username LIKE ? OR major LIKE ? OR interests LIKE ?)
        AND is_active = 1
        ORDER BY username ASC
        LIMIT ?
    """, (search_pattern, search_pattern, search_pattern, limit)).fetchall()
    conn.close()
    return [dict(user) for user in users]

# ==================== POST FUNCTIONS ====================

def create_post(db_path, user_id, content, post_type='general', 
                visibility='public', image_url=None):
    """Create a new post"""
    conn = get_db_connection(db_path)
    cursor = conn.execute("""
        INSERT INTO posts (user_id, content, post_type, visibility, image_url)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, content, post_type, visibility, image_url))
    post_id = cursor.lastrowid
    
    # Extract and save hashtags
    hashtags = extract_hashtags(content)
    for tag in hashtags:
        save_hashtag(conn, post_id, tag)
    
    conn.commit()
    conn.close()
    return post_id

def get_all_posts(db_path, user_id=None, limit=50, offset=0, visibility_filter=None):
    """Get all posts with likes and comment counts"""
    conn = get_db_connection(db_path)
    
    query = """
        SELECT p.*, u.username, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count,
               (SELECT COUNT(*) > 0 FROM likes WHERE post_id = p.id AND user_id = ?) AS user_liked,
               (SELECT COUNT(*) > 0 FROM saved_posts WHERE post_id = p.id AND user_id = ?) AS user_saved
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE u.is_active = 1
    """
    
    params = [user_id, user_id]
    
    if visibility_filter:
        query += " AND p.visibility = ?"
        params.append(visibility_filter)
    
    query += " ORDER BY p.is_pinned DESC, p.timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    posts = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(post) for post in posts]

def get_post_by_id(db_path, post_id, user_id=None):
    """Get a single post by ID"""
    conn = get_db_connection(db_path)
    post = conn.execute("""
        SELECT p.*, u.username, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count,
               (SELECT COUNT(*) > 0 FROM likes WHERE post_id = p.id AND user_id = ?) AS user_liked,
               (SELECT COUNT(*) > 0 FROM saved_posts WHERE post_id = p.id AND user_id = ?) AS user_saved
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    """, (user_id, user_id, post_id)).fetchone()
    conn.close()
    return dict(post) if post else None

def get_user_posts(db_path, user_id, limit=50):
    """Get all posts by a specific user"""
    conn = get_db_connection(db_path)
    posts = conn.execute("""
        SELECT p.*, u.username, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = ?
        ORDER BY p.timestamp DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(post) for post in posts]

def update_post(db_path, post_id, content, post_type=None):
    """Update a post"""
    conn = get_db_connection(db_path)
    if post_type:
        conn.execute("""
            UPDATE posts SET content = ?, post_type = ?, edited_at = datetime('now')
            WHERE id = ?
        """, (content, post_type, post_id))
    else:
        conn.execute("""
            UPDATE posts SET content = ?, edited_at = datetime('now')
            WHERE id = ?
        """, (content, post_id))
    conn.commit()
    conn.close()

def delete_post(db_path, post_id):
    """Delete a post"""
    conn = get_db_connection(db_path)
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def toggle_pin_post(db_path, post_id):
    """Toggle pin status of a post"""
    conn = get_db_connection(db_path)
    conn.execute("""
        UPDATE posts SET is_pinned = NOT is_pinned WHERE id = ?
    """, (post_id,))
    conn.commit()
    conn.close()

# ==================== COMMENT FUNCTIONS ====================

def add_comment(db_path, post_id, user_id, content, parent_comment_id=None):
    """Add a comment to a post"""
    conn = get_db_connection(db_path)
    cursor = conn.execute("""
        INSERT INTO comments (post_id, user_id, content, parent_comment_id)
        VALUES (?, ?, ?, ?)
    """, (post_id, user_id, content, parent_comment_id))
    comment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return comment_id

def get_post_comments(db_path, post_id):
    """Get all comments for a post"""
    conn = get_db_connection(db_path)
    comments = conn.execute("""
        SELECT c.*, u.username, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE comment_id = c.id) AS like_count
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.timestamp ASC
    """, (post_id,)).fetchall()
    conn.close()
    return [dict(comment) for comment in comments]

def update_comment(db_path, comment_id, content):
    """Update a comment"""
    conn = get_db_connection(db_path)
    conn.execute("""
        UPDATE comments SET content = ?, edited_at = datetime('now')
        WHERE id = ?
    """, (content, comment_id))
    conn.commit()
    conn.close()

def delete_comment(db_path, comment_id):
    """Delete a comment"""
    conn = get_db_connection(db_path)
    conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()

# ==================== LIKE FUNCTIONS ====================

def toggle_like_post(db_path, post_id, user_id):
    """Toggle like on a post"""
    conn = get_db_connection(db_path)
    existing = conn.execute("""
        SELECT id FROM likes WHERE post_id = ? AND user_id = ?
    """, (post_id, user_id)).fetchone()
    
    if existing:
        conn.execute("DELETE FROM likes WHERE id = ?", (existing['id'],))
        action = 'unliked'
    else:
        conn.execute("""
            INSERT INTO likes (post_id, user_id) VALUES (?, ?)
        """, (post_id, user_id))
        action = 'liked'
    
    conn.commit()
    conn.close()
    return action

def toggle_like_comment(db_path, comment_id, user_id):
    """Toggle like on a comment"""
    conn = get_db_connection(db_path)
    existing = conn.execute("""
        SELECT id FROM likes WHERE comment_id = ? AND user_id = ?
    """, (comment_id, user_id)).fetchone()
    
    if existing:
        conn.execute("DELETE FROM likes WHERE id = ?", (existing['id'],))
        action = 'unliked'
    else:
        conn.execute("""
            INSERT INTO likes (comment_id, user_id) VALUES (?, ?)
        """, (comment_id, user_id))
        action = 'liked'
    
    conn.commit()
    conn.close()
    return action

# ==================== FRIENDSHIP FUNCTIONS ====================

def send_friend_request(db_path, from_user_id, to_user_id):
    """Send a friend request"""
    if from_user_id == to_user_id:
        return False
    
    conn = get_db_connection(db_path)
    try:
        # Check if friendship already exists
        existing = conn.execute("""
            SELECT * FROM friendships 
            WHERE (user_id_1 = ? AND user_id_2 = ?) 
               OR (user_id_1 = ? AND user_id_2 = ?)
        """, (from_user_id, to_user_id, to_user_id, from_user_id)).fetchone()
        
        if existing:
            return False
        
        conn.execute("""
            INSERT INTO friendships (user_id_1, user_id_2, status)
            VALUES (?, ?, 'pending')
        """, (from_user_id, to_user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_friend_requests(db_path, user_id):
    """Get pending friend requests for a user"""
    conn = get_db_connection(db_path)
    requests = conn.execute("""
        SELECT f.id, f.requested_at, u.id as user_id, u.username, 
               u.profile_picture, u.major, u.study_level
        FROM friendships f
        JOIN users u ON f.user_id_1 = u.id
        WHERE f.user_id_2 = ? AND f.status = 'pending'
        ORDER BY f.requested_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(req) for req in requests]

def respond_to_friend_request(db_path, friendship_id, status):
    """Respond to a friend request (accept/reject)"""
    if status not in ['accepted', 'rejected']:
        return False
    
    conn = get_db_connection(db_path)
    conn.execute("""
        UPDATE friendships 
        SET status = ?, responded_at = datetime('now')
        WHERE id = ?
    """, (status, friendship_id))
    conn.commit()
    conn.close()
    return True

def get_user_friends(db_path, user_id):
    """Get all accepted friends of a user"""
    conn = get_db_connection(db_path)
    friends = conn.execute("""
        SELECT u.id, u.username, u.profile_picture, u.major, u.study_level, u.campus
        FROM friendships f
        JOIN users u ON (
            (f.user_id_1 = ? AND u.id = f.user_id_2) OR 
            (f.user_id_2 = ? AND u.id = f.user_id_1)
        )
        WHERE f.status = 'accepted' AND u.is_active = 1
        ORDER BY u.username ASC
    """, (user_id, user_id)).fetchall()
    conn.close()
    return [dict(friend) for friend in friends]

def are_friends(db_path, user_id1, user_id2):
    """Check if two users are friends"""
    conn = get_db_connection(db_path)
    friendship = conn.execute("""
        SELECT * FROM friendships
        WHERE ((user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?))
        AND status = 'accepted'
    """, (user_id1, user_id2, user_id2, user_id1)).fetchone()
    conn.close()
    return friendship is not None

def remove_friend(db_path, user_id1, user_id2):
    """Remove friendship between two users"""
    conn = get_db_connection(db_path)
    conn.execute("""
        DELETE FROM friendships
        WHERE (user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?)
    """, (user_id1, user_id2, user_id2, user_id1))
    conn.commit()
    conn.close()

# ==================== MESSAGING FUNCTIONS ====================

def send_message(db_path, sender_id, receiver_id, content):
    """Send a direct message"""
    conn = get_db_connection(db_path)
    cursor = conn.execute("""
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (?, ?, ?)
    """, (sender_id, receiver_id, content))
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id

def get_conversation(db_path, user_id1, user_id2, limit=50):
    """Get conversation between two users"""
    conn = get_db_connection(db_path)
    messages = conn.execute("""
        SELECT m.*, 
               u1.username as sender_username,
               u2.username as receiver_username
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.id
        JOIN users u2 ON m.receiver_id = u2.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?)
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.timestamp DESC
        LIMIT ?
    """, (user_id1, user_id2, user_id2, user_id1, limit)).fetchall()
    conn.close()
    return [dict(msg) for msg in messages]

def get_user_conversations(db_path, user_id):
    """Get all conversations for a user"""
    conn = get_db_connection(db_path)
    conversations = conn.execute("""
        SELECT DISTINCT
            CASE 
                WHEN m.sender_id = ? THEN m.receiver_id
                ELSE m.sender_id
            END as other_user_id,
            u.username as other_username,
            u.profile_picture,
            MAX(m.timestamp) as last_message_time,
            (SELECT COUNT(*) FROM messages 
             WHERE receiver_id = ? AND sender_id = other_user_id AND is_read = 0) as unread_count
        FROM messages m
        JOIN users u ON u.id = (
            CASE 
                WHEN m.sender_id = ? THEN m.receiver_id
                ELSE m.sender_id
            END
        )
        WHERE m.sender_id = ? OR m.receiver_id = ?
        GROUP BY other_user_id
        ORDER BY last_message_time DESC
    """, (user_id, user_id, user_id, user_id, user_id)).fetchall()
    conn.close()
    return [dict(conv) for conv in conversations]

def mark_messages_read(db_path, user_id, other_user_id):
    """Mark all messages from another user as read"""
    conn = get_db_connection(db_path)
    conn.execute("""
        UPDATE messages SET is_read = 1
        WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
    """, (user_id, other_user_id))
    conn.commit()
    conn.close()

# ==================== NOTIFICATION FUNCTIONS ====================

def create_notification(db_path, user_id, content, notification_type, related_id=None):
    """Create a notification"""
    conn = get_db_connection(db_path)
    cursor = conn.execute("""
        INSERT INTO notifications (user_id, content, notification_type, related_id)
        VALUES (?, ?, ?, ?)
    """, (user_id, content, notification_type, related_id))
    notification_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return notification_id

def get_user_notifications(db_path, user_id, limit=50, unread_only=False):
    """Get notifications for a user"""
    conn = get_db_connection(db_path)
    query = "SELECT * FROM notifications WHERE user_id = ?"
    params = [user_id]
    
    if unread_only:
        query += " AND is_read = 0"
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    notifications = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(notif) for notif in notifications]

def mark_notification_read(db_path, notification_id):
    """Mark a notification as read"""
    conn = get_db_connection(db_path)
    conn.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()

def mark_all_notifications_read(db_path, user_id):
    """Mark all notifications as read for a user"""
    conn = get_db_connection(db_path)
    conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_unread_count(db_path, user_id):
    """Get count of unread notifications"""
    conn = get_db_connection(db_path)
    count = conn.execute("""
        SELECT COUNT(*) as count FROM notifications 
        WHERE user_id = ? AND is_read = 0
    """, (user_id,)).fetchone()
    conn.close()
    return count['count'] if count else 0

# ==================== SAVED POSTS FUNCTIONS ====================

def toggle_save_post(db_path, user_id, post_id):
    """Toggle save status of a post"""
    conn = get_db_connection(db_path)
    existing = conn.execute("""
        SELECT id FROM saved_posts WHERE user_id = ? AND post_id = ?
    """, (user_id, post_id)).fetchone()
    
    if existing:
        conn.execute("DELETE FROM saved_posts WHERE id = ?", (existing['id'],))
        action = 'unsaved'
    else:
        conn.execute("""
            INSERT INTO saved_posts (user_id, post_id) VALUES (?, ?)
        """, (user_id, post_id))
        action = 'saved'
    
    conn.commit()
    conn.close()
    return action

def get_saved_posts(db_path, user_id, limit=50):
    """Get all saved posts for a user"""
    conn = get_db_connection(db_path)
    posts = conn.execute("""
        SELECT p.*, u.username, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count,
               sp.saved_at
        FROM saved_posts sp
        JOIN posts p ON sp.post_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE sp.user_id = ?
        ORDER BY sp.saved_at DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(post) for post in posts]

# ==================== HASHTAG FUNCTIONS ====================

def extract_hashtags(content):
    """Extract hashtags from content"""
    return re.findall(r'#(\w+)', content)

def save_hashtag(conn, post_id, tag):
    """Save hashtag for a post"""
    tag = tag.lower()
    
    # Check if hashtag exists
    hashtag = conn.execute("SELECT id FROM hashtags WHERE tag = ?", (tag,)).fetchone()
    
    if hashtag:
        hashtag_id = hashtag['id']
        conn.execute("UPDATE hashtags SET use_count = use_count + 1 WHERE id = ?", (hashtag_id,))
    else:
        cursor = conn.execute("INSERT INTO hashtags (tag) VALUES (?)", (tag,))
        hashtag_id = cursor.lastrowid
    
    try:
        conn.execute("INSERT INTO post_hashtags (post_id, hashtag_id) VALUES (?, ?)", 
                    (post_id, hashtag_id))
    except sqlite3.IntegrityError:
        pass

def get_trending_hashtags(db_path, limit=10):
    """Get trending hashtags"""
    conn = get_db_connection(db_path)
    hashtags = conn.execute("""
        SELECT tag, use_count FROM hashtags
        ORDER BY use_count DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(tag) for tag in hashtags]

def search_posts_by_hashtag(db_path, tag, limit=50):
    """Search posts by hashtag"""
    conn = get_db_connection(db_path)
    posts = conn.execute("""
        SELECT p.*, u.username, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count
        FROM posts p
        JOIN users u ON p.user_id = u.id
        JOIN post_hashtags ph ON p.id = ph.post_id
        JOIN hashtags h ON ph.hashtag_id = h.id
        WHERE h.tag = ?
        ORDER BY p.timestamp DESC
        LIMIT ?
    """, (tag.lower(), limit)).fetchall()
    conn.close()
    return [dict(post) for post in posts]

# ==================== UTILITY FUNCTIONS ====================

def get_user_stats(db_path, user_id):
    """Get statistics for a user"""
    conn = get_db_connection(db_path)
    
    stats = {}
    stats['post_count'] = conn.execute(
        "SELECT COUNT(*) as count FROM posts WHERE user_id = ?", 
        (user_id,)
    ).fetchone()['count']
    
    stats['friend_count'] = conn.execute("""
        SELECT COUNT(*) as count FROM friendships 
        WHERE (user_id_1 = ? OR user_id_2 = ?) AND status = 'accepted'
    """, (user_id, user_id)).fetchone()['count']
    
    stats['total_likes_received'] = conn.execute("""
        SELECT COUNT(*) as count FROM likes l
        JOIN posts p ON l.post_id = p.id
        WHERE p.user_id = ?
    """, (user_id,)).fetchone()['count']
    
    conn.close()
    return stats