<?php

namespace Tests\Feature;

use App\Models\Post;
use App\Models\User;
use App\Services\EmbeddingService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Laravel\Sanctum\Sanctum;
use Tests\TestCase;

class FeedAndSearchTest extends TestCase
{
    use RefreshDatabase;

    public function test_feed_ranking_returns_highest_scoring_posts_first(): void
    {
        $user = User::factory()->create([
            'bio' => 'Travel stories and authentic local life.',
            'interests' => ['travel', 'authenticity'],
        ]);

        $highValuePost = Post::factory()->create([
            'user_id' => $user->id,
            'text' => 'A beautiful travel memory from a calm train station.',
            'embedding' => [0.95, 0.91, 0.89, 0.88, 0.86],
            'authenticity_score' => 0.95,
        ]);

        $lowValuePost = Post::factory()->create([
            'user_id' => $user->id,
            'text' => 'A generic update about a meeting.',
            'embedding' => [0.10, 0.11, 0.12, 0.13, 0.14],
            'authenticity_score' => 0.20,
        ]);

        $service = new EmbeddingService();
        $userProfile = trim($user->bio . ' ' . implode(' ', $user->interests ?? []));
        $userVector = $service->generate($userProfile);
        $highEmbedding = $highValuePost->embedding->toArray();
        $lowEmbedding = $lowValuePost->embedding->toArray();

        $highScore = $service->computeFeedScore(
            $service->authenticityScore($highValuePost),
            $service->relationshipScore($user, $highValuePost),
            $service->similarity($userVector, $highEmbedding),
            $service->timeDecay($highValuePost->created_at),
            $service->engagementScore($highValuePost),
        );

        $lowScore = $service->computeFeedScore(
            $service->authenticityScore($lowValuePost),
            $service->relationshipScore($user, $lowValuePost),
            $service->similarity($userVector, $lowEmbedding),
            $service->timeDecay($lowValuePost->created_at),
            $service->engagementScore($lowValuePost),
        );

        $this->assertGreaterThan($lowScore, $highScore);
    }

    public function test_search_scoring_prioritizes_semantic_similarity(): void
    {
        $user = User::factory()->create();
        $service = new EmbeddingService();

        $travelPost = Post::factory()->create([
            'user_id' => $user->id,
            'text' => 'A beautiful journey through the mountains.',
            'embedding' => [0.91, 0.90, 0.88, 0.87, 0.85],
            'authenticity_score' => 0.80,
        ]);

        $financePost = Post::factory()->create([
            'user_id' => $user->id,
            'text' => 'A market update and investment commentary.',
            'embedding' => [0.12, 0.13, 0.14, 0.15, 0.16],
            'authenticity_score' => 0.75,
        ]);

        $queryVector = $service->generate('travel and adventure');
        $travelEmbedding = $travelPost->embedding->toArray();
        $financeEmbedding = $financePost->embedding->toArray();

        $travelScore = $service->computeSearchScore(
            $service->authenticityScore($travelPost),
            $service->relationshipScore($user, $travelPost),
            $service->similarity($queryVector, $travelEmbedding),
            $service->timeDecay($travelPost->created_at),
            $service->engagementScore($travelPost),
        );

        $financeScore = $service->computeSearchScore(
            $service->authenticityScore($financePost),
            $service->relationshipScore($user, $financePost),
            $service->similarity($queryVector, $financeEmbedding),
            $service->timeDecay($financePost->created_at),
            $service->engagementScore($financePost),
        );

        $this->assertGreaterThan($financeScore, $travelScore);
    }

    public function test_authenticity_score_is_clamped_between_zero_and_one(): void
    {
        $service = new EmbeddingService();
        $post = new Post();
        $post->authenticity_score = 1.5;

        $this->assertSame(1.0, $service->authenticityScore($post));

        $post->authenticity_score = -0.2;
        $this->assertSame(0.0, $service->authenticityScore($post));
    }

    public function test_similarity_tolerates_missing_embedding_vectors(): void
    {
        $service = new EmbeddingService();

        $this->assertSame(0.0, $service->similarity([0.1, 0.2, 0.3], null));
        $this->assertSame(0.0, $service->similarity([], [0.1, 0.2, 0.3]));
    }

    public function test_feed_endpoint_returns_json_when_post_embedding_is_missing(): void
    {
        $user = User::factory()->create();
        Post::factory()->create([
            'user_id' => $user->id,
            'text' => 'A post without an embedding.',
            'embedding' => null,
        ]);

        Sanctum::actingAs($user, ['*']);

        $response = $this->getJson('/api/feed');

        $response->assertOk()
            ->assertJsonStructure([
                ['post_id', 'author_id', 'author' => ['id', 'name'], 'text', 'image_url', 'created_at', 'score', 'reasons'],
            ]);
    }
}
