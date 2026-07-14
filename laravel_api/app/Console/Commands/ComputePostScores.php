<?php

namespace App\Console\Commands;

use App\Models\Post;
use App\Models\User;
use App\Services\EmbeddingService;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class ComputePostScores extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'compute:post-scores {user_id?}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Compute feed score components for posts and store in post_scores table';

    public function handle(): int
    {
        $userId = $this->argument('user_id');
        $embeddingService = new EmbeddingService();

        if ($userId) {
            $user = User::find($userId);
            if (! $user) {
                $this->error("User {$userId} not found");
                return 1;
            }
            $this->info("Computing scores for user {$user->id}");
            $this->computeForUser($user, $embeddingService);
        } else {
            $this->info('Computing scores for all users (will compute generic semantic score using post embeddings)');
            $posts = Post::with('interactions')->get();
            foreach ($posts as $post) {
                $this->computeAndSave(null, $post, $embeddingService);
            }
        }

        $this->info('Done');
        return 0;
    }

    protected function computeForUser(User $user, EmbeddingService $embeddingService): void
    {
        // Build interactions_by_user_on_author: count of interactions where current user interacted with posts of each author
        $rows = DB::table('interactions')
            ->join('posts', 'interactions.post_id', '=', 'posts.id')
            ->where('interactions.user_id', $user->id)
            ->select('posts.user_id as author_id', DB::raw('count(*) as cnt'))
            ->groupBy('posts.user_id')
            ->get();

        $interactionsByAuthor = [];
        foreach ($rows as $r) {
            $interactionsByAuthor[$r->author_id] = (int) $r->cnt;
        }

        $userProfile = trim($user->bio . ' ' . implode(' ', $user->interests ?? []));
        $userVector = $embeddingService->generate($userProfile);

        $posts = Post::with('interactions')->get();
        foreach ($posts as $post) {
            $this->computeAndSave($user, $post, $embeddingService, $userVector, $interactionsByAuthor);
        }
    }

    protected function computeAndSave(?User $user, Post $post, EmbeddingService $embeddingService, $userVector = null, array $interactionsByAuthor = [])
    {
        $authenticity = $embeddingService->authenticityScore($post);
        $relationship = $user ? $embeddingService->relationshipScore($user, $post) : 0.1;
        $semantic = 0.0;
        if ($user && $userVector && is_array($post->embedding)) {
            $semantic = $embeddingService->similarity($userVector, $post->embedding);
        }
        $recency = $embeddingService->timeDecay($post->created_at);
        $engagement = $embeddingService->engagementScore($post);

        $final = $embeddingService->computeFeedScore($authenticity, $relationship, $semantic, $recency, $engagement);

        // compute views from interactions where type = view
        $views = $post->interactions->where('type', 'view')->count();

        DB::table('post_scores')->updateOrInsert(
            ['post_id' => $post->id],
            [
                'post_views' => $views,
                'post_authenticity_score' => $authenticity,
                'post_semantic_score' => $semantic,
                'post_time_decay_score' => $recency,
                'post_relationship_score' => $relationship,
                'post_final_score' => $final,
                'updated_at' => now(),
                'created_at' => now(),
            ]
        );

        $this->info("Saved scores for post {$post->id}: final={$final}");
    }
}
