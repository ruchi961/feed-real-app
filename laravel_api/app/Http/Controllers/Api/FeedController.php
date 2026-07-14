<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Services\EmbeddingService;
use Illuminate\Http\Request;

class FeedController extends Controller
{
    public function index(Request $request, EmbeddingService $embeddingService)
    {
        $user = $request->user();
        $posts = Post::with('author', 'interactions')->get();
        $userProfile = trim($user->bio . ' ' . implode(' ', $user->interests ?? []));
        $userVector = $embeddingService->generate($userProfile);

        $ranked = $posts->map(function (Post $post) use ($user, $userVector, $embeddingService) {
            $authenticity = $embeddingService->authenticityScore($post);
            $relationship = $embeddingService->relationshipScore($user, $post);
            $postEmbedding = $post->embedding;
            $postEmbedding = is_array($postEmbedding) ? $postEmbedding : [];
            $semantic = $embeddingService->similarity($userVector, $postEmbedding);
            $recency = $embeddingService->timeDecay($post->created_at);
            $engagement = $embeddingService->engagementScore($post);

            return [
                'post_id' => $post->id,
                'author_id' => $post->user_id,
                'author' => [
                    'id' => $post->author->id ?? null,
                    'name' => $post->author->name ?? null,
                ],
                'text' => $post->text,
                'image_url' => $post->image_url,
                'created_at' => $post->created_at,
                'score' => $embeddingService->computeFeedScore($authenticity, $relationship, $semantic, $recency, $engagement),
                'reasons' => compact('authenticity', 'relationship', 'semantic', 'recency', 'engagement'),
            ];
        })
        ->sortByDesc('score')
        ->values()
        ->take(10);

        return response()->json($ranked);
    }
}
