import mysql.connector

# ----------------------------
# DATABASE CONFIGURATION
# ----------------------------

HOST = "localhost"
USER = "root"
PASSWORD = "password"
DATABASE = "social_feed"

# ----------------------------
# CONNECT TO MYSQL SERVER
# ----------------------------

connection = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD
)

cursor = connection.cursor()

print("Connected to MySQL")

# ----------------------------
# CREATE DATABASE
# ----------------------------

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
print(f"✓ {DATABASE} database created")
cursor.execute(f"USE {DATABASE}")

print(f"Using database: {DATABASE}")

# ============================================================
# USERS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(100) UNIQUE NOT NULL,

    full_name VARCHAR(150),

    email VARCHAR(255),

    password VARCHAR(255),

    avatar VARCHAR(500),

    bio TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")
print("✓ users table created")
# ============================================================
# POSTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    text_content TEXT,

    authenticity_score FLOAT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
    REFERENCES users(id)
    ON DELETE CASCADE

)
""")
print("✓ posts table created")
# ============================================================
# POST IMAGES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS post_images (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    post_id BIGINT NOT NULL,

    image_url VARCHAR(500),

    image_order INT DEFAULT 1,

    FOREIGN KEY(post_id)
    REFERENCES posts(id)
    ON DELETE CASCADE

)
""")
print("✓ post_images table created")
# ============================================================
# REACTIONS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS reactions (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    post_id BIGINT,

    user_id BIGINT,

    reaction_type ENUM(
        'like',
        'love',
        'laugh',
        'wow'
    ),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
    REFERENCES posts(id)
    ON DELETE CASCADE,

    FOREIGN KEY(user_id)
    REFERENCES users(id)
    ON DELETE CASCADE

)
""")
print("✓ reactions table created")
# ============================================================
# COMMENTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    post_id BIGINT,

    user_id BIGINT,

    comment TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
    REFERENCES posts(id)
    ON DELETE CASCADE,

    FOREIGN KEY(user_id)
    REFERENCES users(id)
    ON DELETE CASCADE

)
""")
print("✓ comments table created")
# ============================================================
# FOLLOWS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS follows (

    follower_id BIGINT,

    following_id BIGINT,

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

)
""")
print("✓ follows table created")
# ============================================================
# USER INTERACTIONS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_interactions (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT,

    target_user BIGINT,

    interaction_type ENUM(

        'view',

        'like',

        'comment',

        'share',

        'save',

        'message'

    ),

    interaction_weight FLOAT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    FOREIGN KEY(target_user)
    REFERENCES users(id)
    ON DELETE CASCADE

)
""")
print("✓ user_interactions table created")
# ============================================================
# POST EMBEDDINGS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS post_embeddings (

    post_id BIGINT PRIMARY KEY,

    embedding JSON,

    model_name VARCHAR(100),

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
    REFERENCES posts(id)
    ON DELETE CASCADE

)
""")
print("✓ post_embeddings table created")
# ============================================================
# USER EMBEDDINGS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_embeddings (

    user_id BIGINT PRIMARY KEY,

    embedding JSON,

    model_name VARCHAR(100),

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
    REFERENCES users(id)
    ON DELETE CASCADE

)
""")
print("✓ user_embeddings table created")
# ============================================================
# AUTHENTICITY FEATURES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS authenticity_features (

    post_id BIGINT PRIMARY KEY,

    filter_score FLOAT,

    image_quality FLOAT,

    face_edit_score FLOAT,

    caption_originality FLOAT,

    authenticity_score FLOAT,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(post_id)
    REFERENCES posts(id)
    ON DELETE CASCADE

)
""")
print("✓ authenticity_features table created")
# ============================================================
# FEED CACHE (OPTIONAL)
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS feed_cache (

    user_id BIGINT,

    post_id BIGINT,

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

)
""")
print("✓ feed_cache table created")
# ============================================================
# RELATIONSHIP SCORES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS relationship_scores (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    related_user_id BIGINT NOT NULL,

    interaction_score FLOAT DEFAULT 0,

    likes_given INT DEFAULT 0,

    comments_given INT DEFAULT 0,

    shares_given INT DEFAULT 0,

    messages_sent INT DEFAULT 0,

    profile_visits INT DEFAULT 0,

    last_interaction TIMESTAMP NULL,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY(related_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    UNIQUE(user_id, related_user_id)

)
""")

print("✓ relationship_scores table created")

# ============================================================
# USER INTERESTS (Semantic Similarity)
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_interests (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    topic VARCHAR(100) NOT NULL,

    embedding JSON,

    interest_score FLOAT DEFAULT 0,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE

)
""")

print("✓ user_interests table created")

connection.commit()

print()
print("========================================")
print("Social Feed Database Created Successfully")
print("========================================")

cursor.close()
connection.close()