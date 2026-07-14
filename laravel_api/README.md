# Laravel Social Feed API — Scoring & Ranking

This repository contains a Laravel API backend that returns a personalized feed for mobile clients. It includes a Python `tools/ranking_engine.py` (optional) and a Laravel Artisan command to compute and persist post score components into MySQL (`post_scores` table).

Tests and sql queries are included too  unit and feature test with sql queries as in assignments given

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

- Login: `POST /api/login` body `{ "email":"alice@example.com","password":"password" }`
- Feed: `GET /api/feed` (requires `Authorization: Bearer <token>`)

---

## What this does

- `ComputePostScores` (Artisan) computes per-post components and writes them into `post_scores`:
  - `post_authenticity_score`, `post_semantic_score`, `post_time_decay_score`, `post_relationship_score`, `post_final_score`, `post_views`.
- `tools/ranking_engine.py` contains a Python implementation with image + caption authenticity heuristics and optional Chroma + sentence-transformers integration. Use it if you want identical Python scoring or to prototype advanced models.

---

**System Architecture (rough ASCII diagram)**

```
[React Native client]
        |
        | HTTP JSON (Bearer token)
        v
   [Laravel API - routes/api.php]
        |
        | Eloquent models (User, Post, Interaction, PostScore)
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

## Database schema (relevant tables)

- `users` (id, name, email, password, bio, interests JSON)
- `posts` (id, user_id -> users.id, text, image_url, embedding JSON, authenticity_score, created_at)
- `interactions` (id, user_id -> users.id, post_id -> posts.id, type, payload JSON)
- `post_scores` (id, post_id -> posts.id, post_views INT, post_authenticity_score FLOAT,
  post_semantic_score FLOAT, post_time_decay_score FLOAT, post_relationship_score FLOAT,
  post_final_score FLOAT, created_at, updated_at)

Indexes:
- `posts.user_id` (FK) — used for author lookups
- `interactions.post_id` and `interactions.user_id` for counting views/reactions
- `post_scores.post_id` unique index

---

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

- Authenticity heuristics are heuristic-based (image statistics + caption rules) — they are fast but not as robust as dedicated models.
- The PHP `EmbeddingService` contains simplified mock embedding functionality for dev/testing; production should use real embeddings stored in a vector DB.
- Using Chroma simplifies local development; for large-scale production, consider a more robust, horizontally scalable vector DB.

---
