import mysql.connector

# ============================================================
# DATABASE CONFIG
# ============================================================

HOST = "localhost"
USER = "root"
PASSWORD = "password"
DATABASE = "social_feed"

# ============================================================
# CONNECT
# ============================================================

connection = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD
)

cursor = connection.cursor()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
cursor.execute(f"USE {DATABASE}")

print("Database Ready")

# ============================================================
# USERS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS users(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(100) UNIQUE NOT NULL,

    full_name VARCHAR(150),

    email VARCHAR(255) UNIQUE,

    password VARCHAR(255),

    avatar VARCHAR(500),

    bio TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP

);

""")

print("Users ✓")

# ============================================================
# POSTS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS posts(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    text_content TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    deleted_at TIMESTAMP NULL,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);

""")

print("Posts ✓")

# ============================================================
# POST IMAGES
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS post_images(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    post_id BIGINT NOT NULL,

    image_url VARCHAR(500),

    image_order INT DEFAULT 1,

    width INT,

    height INT,

    is_cover BOOLEAN DEFAULT FALSE,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE

);

""")

print("Images ✓")

# ============================================================
# POST STATISTICS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS post_statistics(

    post_id BIGINT PRIMARY KEY,

    views INT DEFAULT 0,

    likes INT DEFAULT 0,

    comments INT DEFAULT 0,

    shares INT DEFAULT 0,

    saves INT DEFAULT 0,

    reactions INT DEFAULT 0,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE

);

""")

print("Statistics ✓")

# ============================================================
# REACTIONS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS reactions(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    post_id BIGINT,

    user_id BIGINT,

    reaction VARCHAR(30),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);

""")

print("Reactions ✓")

# ============================================================
# COMMENTS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS comments(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    post_id BIGINT,

    user_id BIGINT,

    parent_comment_id BIGINT NULL,

    comment TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY(parent_comment_id)
        REFERENCES comments(id)
        ON DELETE CASCADE

);

""")

print("Comments ✓")

# ============================================================
# FOLLOWS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS follows(

    follower_id BIGINT,

    following_id BIGINT,

    status ENUM(
        'pending',
        'accepted',
        'blocked'
    ) DEFAULT 'accepted',

    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY(
        follower_id,
        following_id
    ),

    FOREIGN KEY(follower_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY(following_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);

""")

print("Follows ✓")

# ============================================================
# USER INTERACTIONS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS user_interactions(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT,

    post_id BIGINT,

    target_user BIGINT,

    interaction_type ENUM(

        'view',
        'like',
        'comment',
        'share',
        'save',
        'message'

    ),

    interaction_weight FLOAT DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE,

    FOREIGN KEY(target_user)
        REFERENCES users(id)
        ON DELETE CASCADE

);

""")

print("Interactions ✓")
```python
# ============================================================
# POST EMBEDDINGS
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS post_embeddings(

    post_id BIGINT PRIMARY KEY,

    embedding JSON,

    embedding_dimension INT,

    model_name VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE

);

""")

print("Post Embeddings ✓")

# ============================================================
# SEMANTIC PROFILES (USER INTERESTS)
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS semantic_profiles(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    topic VARCHAR(150),

    embedding JSON,

    embedding_dimension INT,

    model_name VARCHAR(100),

    interest_score FLOAT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);

""")

print("Semantic Profiles ✓")

# ============================================================
# RELATIONSHIP SCORES
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS relationship_scores(

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    related_user_id BIGINT NOT NULL,

    relationship_score FLOAT DEFAULT 0,

    likes_given INT DEFAULT 0,

    comments_given INT DEFAULT 0,

    shares_given INT DEFAULT 0,

    messages_sent INT DEFAULT 0,

    profile_visits INT DEFAULT 0,

    total_interactions INT DEFAULT 0,

    last_interaction TIMESTAMP NULL,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY(related_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    UNIQUE(user_id, related_user_id)

);

""")

print("Relationship Scores ✓")

# ============================================================
# AUTHENTICITY FEATURES
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS authenticity_features(

    post_id BIGINT PRIMARY KEY,

    filter_score FLOAT DEFAULT 0,

    image_quality FLOAT DEFAULT 0,

    face_edit_score FLOAT DEFAULT 0,

    caption_originality FLOAT DEFAULT 0,

    authenticity_score FLOAT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE

);

""")

print("Authenticity ✓")

# ============================================================
# POST SCORES
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS post_scores(

    post_id BIGINT PRIMARY KEY,

    authenticity_score FLOAT DEFAULT 0,

    time_decay_score FLOAT DEFAULT 0,

    engagement_score FLOAT DEFAULT 0,

    final_score FLOAT DEFAULT 0,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE

);

""")

print("Post Scores ✓")

# ============================================================
# FEED CACHE
# ============================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS feed_cache(

    user_id BIGINT,

    post_id BIGINT,

    rank_position INT,

    feed_score FLOAT,

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY(
        user_id,
        post_id
    ),

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON DELETE CASCADE

);

""")

print("Feed Cache ✓")

# ============================================================
# INDEXES
# ============================================================

cursor.execute("""
CREATE INDEX idx_posts_created_at
ON posts(created_at)
""")

cursor.execute("""
CREATE INDEX idx_posts_user
ON posts(user_id)
""")

cursor.execute("""
CREATE INDEX idx_comments_post
ON comments(post_id)
""")

cursor.execute("""
CREATE INDEX idx_reactions_post
ON reactions(post_id)
""")

cursor.execute("""
CREATE INDEX idx_statistics_views
ON post_statistics(views)
""")

cursor.execute("""
CREATE INDEX idx_scores_final
ON post_scores(final_score)
""")

cursor.execute("""
CREATE INDEX idx_relationship_user
ON relationship_scores(user_id)
""")

cursor.execute("""
CREATE INDEX idx_semantic_user
ON semantic_profiles(user_id)
""")

cursor.execute("""
CREATE INDEX idx_feed_user
ON feed_cache(user_id)
""")

print("Indexes ✓")

# ============================================================
# COMMIT
# ============================================================

connection.commit()

print()
print("======================================")
print("SOCIAL FEED DATABASE CREATED")
print("======================================")

cursor.close()
connection.close()


