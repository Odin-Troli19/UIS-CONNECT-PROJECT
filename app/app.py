from flask import Flask, render_template, request, redirect, url_for, flash, session
from db_utils import (
    get_db_connection,
    get_all_posts,
    get_user_profile,
    get_post_with_comments,
    add_comment,
    add_post,
    like_post,
    authenticate_user,
    get_friend_requests_for_user
)




from config import DATABASE

app = Flask(__name__)
app.secret_key = 'secret-key-for-demo'  # Change this for production

@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = authenticate_user(username)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('User not found.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        major = request.form['major']
        interests = request.form['interests']
        study_level = request.form['study_level']
        campus = request.form['campus']
        student_number = request.form['student_number']

        existing_user = authenticate_user(username)
        if existing_user:
            flash("Username already exists.", "error")
            return redirect(url_for('register'))

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO users (username, major, interests, study_level, campus, student_number)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, major, interests, study_level, campus, student_number))
        conn.commit()

        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        session['user_id'] = user['id']
        session['username'] = user['username']
        flash("Registration successful! You are now logged in.", "success")
        return redirect(url_for('index'))

    return render_template('register.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("You have to register or login to be able to see your profile.", "error")
        return redirect(url_for('login'))
    
    user, user_posts = get_user_profile(user_id)
    if not user:
        flash("Profile not found.", "error")
        return redirect(url_for('index'))
    
    return render_template('profile.html', user=user, user_posts=user_posts)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to comment.", 'error')
            return redirect(url_for('login'))
        content = request.form['content']
        add_comment(post_id, user_id, content)
        flash("Comment added!", "success")
        return redirect(url_for('post', post_id=post_id))

    post, comments = get_post_with_comments(post_id)
    return render_template('post.html', post=post, comments=comments)

@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        flash("Login to create a post.", "error")
        return redirect(url_for('login'))
    if request.method == 'POST':
        content = request.form['content']
        add_post(session['user_id'], content)
        flash("Post created!", "success")
        return redirect(url_for('index'))
    return render_template('new_post.html')

@app.route('/like/<int:post_id>')
def like(post_id):
    if 'user_id' not in session:
        flash("Login to like posts.", "error")
        return redirect(url_for('login'))
    like_post(post_id, session['user_id'])
    flash("Post liked!", "info")
    return redirect(url_for('index'))

@app.route('/friendships')
def friendships():
    conn = get_db_connection()
    friendships = conn.execute("""
        SELECT u1.username AS user1, u2.username AS user2, f.status
        FROM friendships f
        JOIN users u1 ON f.user_id_1 = u1.id
        JOIN users u2 ON f.user_id_2 = u2.id
        ORDER BY u1.username, u2.username
    """).fetchall()
    conn.close()
    return render_template('friendships.html', friendships=friendships)

@app.route('/send_friend_request/<int:to_user_id>')
def send_friend_request_route(to_user_id):
    from_user_id = session.get('user_id')
    if not from_user_id:
        flash("Please login to send friend requests.", "error")
        return redirect(url_for('login'))

    # Avoid sending request to self
    if from_user_id == to_user_id:
        flash("You can't send a request to yourself.", "error")
        return redirect(url_for('profile'))

    send_friend_request(from_user_id, to_user_id)
    flash("Friend request sent!", "success")
    return redirect(url_for('index'))

@app.route('/friend_requests', methods=['GET', 'POST'])
def friend_requests():
    user_id = session.get('user_id')
    if not user_id:
        flash("Login required to view friend requests.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form['action']
        friendship_id = request.form['friendship_id']
        if action in ['accepted', 'rejected']:
            update_friend_request(friendship_id, action)
            flash(f"Request {action}!", "info")

    requests = get_friend_requests_for_user(user_id)
    return render_template('friend_requests.html', requests=requests)

@app.route('/users')
def users():
    sort_by = request.args.get('sort', 'username')  # Default to sorting by name
    if sort_by not in ['username', 'major']:
        sort_by = 'username'

    conn = get_db_connection()
    users = conn.execute(f"""
        SELECT id, username, major, interests
        FROM users
        ORDER BY {sort_by} ASC
    """).fetchall()
    conn.close()
    return render_template('users.html', users=users, sort_by=sort_by)

@app.route('/users/<int:user_id>')
def view_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    posts = conn.execute("""
        SELECT p.*, 
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count
        FROM posts p
        WHERE p.user_id = ?
        ORDER BY p.timestamp DESC
    """, (user_id,)).fetchall()
    conn.close()

    if not user:
        flash("User not found", "error")
        return redirect(url_for('users'))

    return render_template('user_profile.html', user=user, posts=posts)


if __name__ == '__main__':
    app.run(debug=True)
