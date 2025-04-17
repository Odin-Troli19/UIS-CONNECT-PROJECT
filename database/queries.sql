
-- 1. Join: Posts with usernames
SELECT posts.id, posts.content, posts.timestamp, users.username
FROM posts
JOIN users ON posts.user_id = users.id;

-- 2. Join: Comments with commenter names and post content
SELECT comments.content AS comment, comments.timestamp, users.username AS commenter, posts.content AS post
FROM comments
JOIN users ON comments.user_id = users.id
JOIN posts ON comments.post_id = posts.id;

-- 3. Aggregation: Count of likes per post
SELECT post_id, COUNT(*) AS total_likes
FROM likes
GROUP BY post_id;

-- 4. Grouping: Count of comments per user
SELECT user_id, COUNT(*) AS total_comments
FROM comments
GROUP BY user_id;

-- 5. Filtering: Posts by a specific user
SELECT * FROM posts
WHERE user_id = 3;

-- 6. Filtering: Comments in a specific date range
SELECT * FROM comments
WHERE timestamp BETWEEN '2025-03-01' AND '2025-03-05';

-- 7. Filtering: Search posts with keyword
SELECT * FROM posts
WHERE content LIKE '%project%';

-- 8. Join and Group: Count of posts per user
SELECT users.username, COUNT(posts.id) AS total_posts
FROM posts
JOIN users ON posts.user_id = users.id
GROUP BY posts.user_id;
