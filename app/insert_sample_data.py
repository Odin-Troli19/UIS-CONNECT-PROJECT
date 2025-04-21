from db_utils import get_db_connection

def insert_sample_data():
    conn = get_db_connection()
    cur = conn.cursor()

    # USERS
    users = [
        (1, 'odin01', 'Computer Science', 'Gaming, AI'),
        (2, 'kellyS', 'Mechanical Engineering', 'Design, CAD'),
        (3, 'max123', 'Data Science', 'Machine Learning'),
        (4, 'stureT', 'IT', 'Coding, Linux'),
        (5, 'lena99', 'Biology', 'Nature'),
        (6, 'emmaX', 'Economics', 'Finance, Books'),
        (7, 'alex10', 'Physics', 'Astronomy'),
        (8, 'saraD', 'Mathematics', 'Puzzles'),
        (9, 'chrisB', 'Cybersecurity', 'Networks'),
        (10, 'tinaV', 'Architecture', 'Drawing')
    ]
    cur.executemany("INSERT INTO Users (id, username, major, interests) VALUES (?, ?, ?, ?);", users)

    # POSTS
    posts = [
        (1, 1, 'Hello world! First post.', '2025-04-01 10:00'),
        (2, 2, 'Anyone up for a study group in mechanics?', '2025-04-01 11:00'),
        (3, 3, 'Check out my ML model results!', '2025-04-02 09:30'),
        (4, 4, 'Linux is life ', '2025-04-02 12:45'),
        (5, 5, 'Biology notes for the exam ', '2025-04-03 08:15'),
        (6, 6, 'Which book to read next?', '2025-04-03 13:20'),
        (7, 7, 'My physics homework is wild ', '2025-04-04 14:05'),
        (8, 8, 'Cool math riddle: ...', '2025-04-04 16:00'),
        (9, 9, 'Network attack trends', '2025-04-05 09:45'),
        (10, 10, 'Architecture sketch of campus', '2025-04-05 17:00')
    ]
    cur.executemany("INSERT INTO Posts (id, user_id, content, timestamp) VALUES (?, ?, ?, ?);", posts)

    # COMMENTS
    comments = [
        (1, 1, 2, 'Welcome to UIS-Connect!', '2025-04-01 10:05'),
        (2, 2, 3, 'I’m in for the study group!', '2025-04-01 11:30'),
        (3, 3, 1, 'Nice work on that model.', '2025-04-02 09:45'),
        (4, 4, 5, 'Totally agree!', '2025-04-02 13:00'),
        (5, 5, 6, 'Thanks for sharing.', '2025-04-03 08:30'),
        (6, 6, 8, 'Try "Rich Dad Poor Dad".', '2025-04-03 14:00'),
        (7, 7, 9, 'Physics gang ', '2025-04-04 14:30'),
        (8, 8, 10, 'Love that puzzle!', '2025-04-04 16:15'),
        (9, 9, 4, 'Good stuff.', '2025-04-05 10:00'),
        (10, 10, 7, 'That’s beautiful!', '2025-04-05 17:30')
    ]
    cur.executemany("INSERT INTO Comments (id, post_id, user_id, content, timestamp) VALUES (?, ?, ?, ?, ?);", comments)

    # LIKES
    likes = [
        (1, 1, 2), (2, 1, 3), (3, 2, 4), (4, 3, 5), (5, 3, 6),
        (6, 4, 7), (7, 5, 8), (8, 6, 9), (9, 7, 10), (10, 8, 1)
    ]
    cur.executemany("INSERT INTO Likes (id, post_id, user_id) VALUES (?, ?, ?);", likes)

    # FRIENDSHIPS
    friendships = [
        (1, 1, 2), (2, 1, 3), (3, 2, 4), (4, 3, 5), (5, 4, 6),
        (6, 5, 7), (7, 6, 8), (8, 7, 9), (9, 8, 10), (10, 9, 1)
    ]
    cur.executemany("INSERT INTO Friendships (id, user_id_1, user_id_2) VALUES (?, ?, ?);", friendships)

    conn.commit()
    conn.close()
    print(" Sample data inserted successfully.")

# Run it
if __name__ == '__main__':
    insert_sample_data()
