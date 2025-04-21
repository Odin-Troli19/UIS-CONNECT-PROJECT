import sqlite3
from config import DATABASE

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_posts():
    conn = get_db_connection()
    posts = conn.execute("""
        SELECT posts.id, posts.content, posts.timestamp, users.username,
            (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.timestamp DESC
    """).fetchall()
    conn.close()
    return posts

def get_user_profile(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    posts = conn.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()
    conn.close()
    return user, posts

def get_post_with_comments(post_id):
    conn = get_db_connection()
    post = conn.execute("""
        SELECT posts.id, posts.content, posts.timestamp, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.id = ?
    """, (post_id,)).fetchone()

    comments = conn.execute("""
        SELECT comments.content, comments.timestamp, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = ?
        ORDER BY comments.timestamp ASC
    """, (post_id,)).fetchall()
    conn.close()
    return post, comments

def add_comment(post_id, user_id, content):
    conn = get_db_connection()
    conn.execute("INSERT INTO comments (post_id, user_id, content, timestamp) VALUES (?, ?, ?, datetime('now'))",
                 (post_id, user_id, content))
    conn.commit()
    conn.close()

def add_post(user_id, content):
    conn = get_db_connection()
    conn.execute("INSERT INTO posts (user_id, content, timestamp) VALUES (?, ?, datetime('now'))",
                 (user_id, content))
    conn.commit()
    conn.close()

def like_post(post_id, user_id):
    conn = get_db_connection()
    conn.execute("INSERT INTO likes (post_id, user_id, timestamp) VALUES (?, ?, datetime('now'))",
                 (post_id, user_id))
    conn.commit()
    conn.close()

def authenticate_user(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def send_friend_request(user_id_1, user_id_2):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO friendships (user_id_1, user_id_2, status)
        VALUES (?, ?, 'pending')
    """, (user_id_1, user_id_2))
    conn.commit()
    conn.close()

def get_friend_requests_for_user(user_id):
    conn = get_db_connection()
    requests = conn.execute("""
        SELECT f.id, u1.username AS requester
        FROM friendships f
        JOIN users u1 ON f.user_id_1 = u1.id
        WHERE f.user_id_2 = ? AND f.status = 'pending'
    """, (user_id,)).fetchall()
    conn.close()
    return requests

def update_friend_request(friendship_id, new_status):
    conn = get_db_connection()
    conn.execute("""
        UPDATE friendships SET status = ?
        WHERE id = ?
    """, (new_status, friendship_id))
    conn.commit()
    conn.close()
