from flask import Flask, render_template, request, redirect, url_for
from db_utils import get_all_posts, get_user_profile, get_post_with_comments, add_comment

app = Flask(__name__)

@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user, user_posts = get_user_profile(user_id)
    if not user:
        return "User not found", 404
    return render_template('profile.html', user=user, user_posts=user_posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    if request.method == 'POST':
        # In real app, get user_id from session/login. For now, use dummy ID 1.
        user_id = 1
        content = request.form['content']
        add_comment(post_id, user_id, content)
        return redirect(url_for('post', post_id=post_id))

    post, comments = get_post_with_comments(post_id)
    if not post:
        return "Post not found", 404
    return render_template('post.html', post=post, comments=comments)

if __name__ == '__main__':
    app.run(debug=True)
