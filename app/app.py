from flask import Flask, render_template, request, redirect, url_for, flash, session
from db_utils import (
    get_db_connection,
    get_all_posts,
    get_user_profile,
    get_post_with_comments,
    add_comment,
    add_post,
    like_post,
    authenticate_user
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
        user = authenticate_user(username)
        if user:
            flash("Username already exists.", "error")
            return redirect(url_for('register'))
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, major, interests) VALUES (?, ?, ?)",
                     (username, major, interests))
        conn.commit()
        conn.close()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
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

if __name__ == '__main__':
    app.run(debug=True)
