# Laravel/React Social Feed API — Scoring & Ranking

This repository contains a Laravel API backend that returns a personalized feed for mobile clients. It includes a Python `tools/ranking_engine.py` (optional) and a Laravel Artisan command to compute and persist post score components into MySQL (`post_scores` table).
video link : 
https://drive.google.com/file/d/1iln-V3bUYmUj93_Qvp1fV-JAJX5xS3AN/view?usp=sharing
## Quick start

1. Start MySQL and ensure `.env` DB settings are correct.
2. Start the Laravel server:

```bash
cd laravel_api
php artisan serve --host=127.0.0.1 --port=8000
```

3. Seed demo data (already included):

```bash
php artisan db:seed --class=DatabaseSeeder
```

4. Compute and store post scores (per-user or global):

```bash
# For a specific user (user id 1):
php artisan compute:post-scores 1

# For all posts (generic scores):
php artisan compute:post-scores
```

5. Test endpoints (example):

Start the server with:

- In your terminal:
  - cd C:\Users\Ruchi\Documents\Backend\laravel_api
  - php artisan serve --host=127.0.0.1 --port=8000

Then use these Postman URLs:

- Base URL:
  - http://127.0.0.1:8000/api

### 1) Login
- Method: POST
- URL: http://127.0.0.1:8000/api/login
- Body (JSON):
  {
    "email": "alice@example.com",
    "password": "password"
  }

### 2) Get feed
- Method: GET
- URL: http://127.0.0.1:8000/api/feed
- Header:
  - Authorization: Bearer <token_from_login>

### 3) Search posts
- Method: GET
- URL: http://127.0.0.1:8000/api/search?q=travel
- Header:
  - Authorization: Bearer <token_from_login>

### 4) Create post
- Method: POST
- URL: http://127.0.0.1:8000/api/posts
- Header:
  - Authorization: Bearer <token_from_login>
- Body (JSON):
  {
    "text": "A beautiful morning walk with coffee",
    "image_url": "https://example.com/image.jpg"
  }

### 5) Log interaction
- Method: POST
- URL: http://127.0.0.1:8000/api/interactions
- Header:
  - Authorization: Bearer <token_from_login>
- Body (JSON):
  {
    "post_id": 1,
    "type": "view"
  }

--------

**System Architecture (rough ASCII diagram)**

```
[React Native client]
        |
        | HTTP JSON (Bearer token)
        v
   [Laravel API - routes/api.php]
        |
        | models (User, Post, Interaction, PostScore)
        v
   [MySQL - social_feed database]
        |
        | (optional) embeddings/metadata -> Chroma
        v
   [Chroma Vector DB (optional) for semantic search]

Optional offline worker:
   compute:post-scores -> reads posts/interactions -> writes `post_scores`
```

---
## system design 


                               USER
                                │
                                │
                                ▼
                     +----------------------+
                     | React Native (Expo)  |
                     |      Mobile App      |
                     +----------------------+
                     | - Feed Screen        |
                     | - Search             |
                     | - Reactions          |
                     | - Comments           |
                     +----------------------+
                                │
                     HTTPS REST API Requests
                                │
                                ▼
                  +------------------------------+
                  |        Laravel Backend        |
                  |                              |
                  | Feed Controller              |
                  | Search Controller            |
                  | Comment Controller           |
                  | Reaction Controller          |
                  | Authentication               |
                  +------------------------------+
                     │                     │
                     │                     │
         SQL Queries │                     │ Recommendation Request
                     │                     ▼
                     │         +----------------------------+
                     │         | Python Recommendation      |
                     │         | Engine                     |
                     │         |                            |
                     │         | - Feed Ranking             |
                     │         | - Authenticity Analysis    |
                     │         | - Relationship Score       |
                     │         | - Semantic Similarity      |
                     │         | - Time Decay              |
                     │         +----------------------------+
                     │                     │
                     │                     │
                     ▼                     ▼
           +----------------+      +----------------+
           |     MySQL      |      |   Chroma DB    |
           |                |      |                |
           | Users          |      | Post Vectors   |
           | Posts          |      | Topic Vectors  |
           | Images         |      | Embeddings     |
           | Comments       |      | Similarity     |
           | Reactions      |      +----------------+
           | Relationships  |
           | Interests      |
           +----------------+



## Database schema (relevant tables)

- `users` (id, name, email, password, bio, interests JSON)
- `posts` (id, user_id -> users.id, text, image_url, embedding JSON, authenticity_score, created_at)
- `interactions` (id, user_id -> users.id, post_id -> posts.id, type, payload JSON)
- `post_scores` (id, post_id -> posts.id, post_views INT, post_authenticity_score FLOAT,
  post_semantic_score FLOAT, post_time_decay_score FLOAT, post_relationship_score FLOAT,
  post_final_score FLOAT, created_at, updated_at)

  +----------------------+
|        USERS         |
+----------------------+
| PK id                |
| username             |
| full_name            |
| email                |
| password             |
| avatar               |
| bio                  |
| created_at           |
+----------------------+
          |
          | 1
          |
          | N
+----------------------+
|        POSTS         |
+----------------------+
| PK id                |
| FK user_id           |
| text_content         |
| created_at           |
+----------------------+
          |
      +---+----+
      |   |    |
      |   |    |
      ▼   ▼    ▼

Images  Comments Reactions

Also post statics and authenticity and other metrics calcualtions 
and posts token calclualtion 

---
## Flow

User opens app
      │
      ▼
React Native
      │
GET /api/feed
      │
      ▼
Laravel Backend
      │
Fetch candidate posts
      │
      ▼
MySQL
      │
Return posts
      │
      ▼
Python Recommendation Engine
      │
      ├── Calculate Authenticity
      ├── Calculate Relationship Score
      ├── Calculate Semantic Similarity
      ├── Calculate Time Decay
      │
      ▼
Compute Final Feed Score
      │
Sort Posts
      │
      ▼
Laravel
      │
JSON Response
      │
      ▼
React Native Feed


## Vector embeddings plan

- Use `sentence-transformers` (model: `all-MiniLM-L6-v2`) to generate 384-d embeddings for post text and user profiles.
- Store post embeddings in the database (JSON column) for simple similarity calculations.
- For scale & efficient nearest-neighbor queries, use a vector DB such as **Chroma**:
  - Rationale: lightweight, embeddable, easy to run locally, good Python support.
  - At write time (post create/update), insert embedding + metadata into Chroma collection.
  - At feed time, query Chroma with user profile embedding to get top-K semantically similar posts and use similarity as the semantic component.

Trade-offs: Chroma is simple and developer-friendly; for production at large scale consider FAISS/HNSWlib, Milvus, or Pinecone for managed service and better scaling.

---

## API design (summary)

- `POST /api/login` — body `{ email, password }` -> returns Sanctum token
- `GET /api/feed` — header `Authorization: Bearer <token>` -> returns array of ranked posts with `score` and `reasons` object
- `GET /api/search?q=...` — header `Authorization: Bearer <token>` -> semantic search results
- `POST /api/posts` — create a post (text, image_url) — authenticated
- `POST /api/interactions` — record view/reaction/comment — authenticated

Response shape (feed/search item):

```json
{
  "post_id": 12,
  "author_id": 4,
  "author_name": "Alice",
  "text": "...",
  "image_url": "...",
  "score": 0.8234,
  "reasons": {"authenticity":0.7,"relationship":0.4,"semantic":0.6,"recency":0.8,"engagement":0.1}
}
```

Auth strategy: Laravel Sanctum token-based authentication, short-lived tokens for mobile apps.

---

## Feed ranking algorithm — plain English

The final feed score is a weighted combination of:

- Authenticity (30%): prefers posts that look natural — low filter saturation, natural contrast, realistic noise levels, and original captions.
- Relationship depth (30%): ranks higher posts from authors the user has genuinely interacted with (replies/reactions/views); repeated interactions increase score.
- Semantic similarity (30%): measures topical alignment between the user's interests/profile and the post using vector similarity.
- Time decay (10%): favors newer posts but reduces influence over time so relevance matters more than recency alone.

Posts with higher final scores are surfaced. Posts are filtered or thresholded as needed (e.g., return only score > 0.2).

## Feed ranking algorithm — pseudocode

```
for each post in candidate_posts:
    authenticity = compute_authenticity(post.image, post.caption)   # 0..1
    relationship = compute_relationship(user, post.author)          # 0..1
    semantic = semantic_similarity(user_profile_embedding, post.embedding)  # 0..1
    recency = time_decay(post.created_at)                           # 0..1
    engagement = compute_engagement(post.interactions)              # 0..1

    final_score = 0.30*authenticity + 0.30*relationship + 0.30*semantic + 0.10*recency

sort candidate_posts by final_score desc
return top N
```

Notes: engagement can be used to break ties or to boost posts separately; the Artisan command stores each component in `post_scores`.

---

## How the implementation stores scores

- Use `php artisan compute:post-scores {user_id?}` to compute and write component scores per-post to `post_scores` using the existing `EmbeddingService` logic.
- For production, run this as a scheduled worker or on post-create/update hooks to keep `post_scores` fresh.

---

## AI / agentic tools used

- chatgpt assiatance
- GitHub Copilot (developer assisted) helped write and iterate code during development.

---

## Trade-offs & assumptions

- Authenticity heuristics are heuristic-based (image statistics + caption rules) — they are fast but not as robust as probably dedicated models ai.
- The PHP `EmbeddingService` contains simplified mock embedding functionality for dev/testing; production should use real embeddings stored in a vector DB.
- Using Chroma simplifies local development; for large-scale production, consider a more robust, horizontally scalable vector DB like qdrant.

