<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Services\EmbeddingService;
use Illuminate\Http\Request;

class SearchController extends Controller
{
    public function index(Request $request, EmbeddingService $embeddingService)
    {
        $request->validate([
            'q' => ['required', 'string'],
        ]);

        $query = $request->input('q');
        $queryVector = $embeddingService->generate($query);

        $posts = Post::with('author', 'interactions')->get();

        $results = $posts->map(function (Post $post) use ($request, $query, $queryVector, $embeddingService) {
            $authenticity = $embeddingService->authenticityScore($post);
            $relationship = $embeddingService->relationshipScore($request->user(), $post);
            $semantic = $embeddingService->similarity(
    $queryVector,
    $post->embedding ? $post->embedding->toArray() : null
);
            $recency = $embeddingService->timeDecay($post->created_at);
            $engagement = $embeddingService->engagementScore($post);

            return [
                'post_id' => $post->id,
                'author_id' => $post->user_id,
                'author_name' => $post->author->name ?? null,
                'text' => $post->text,
                'image_url' => $post->image_url,
                'score' => $embeddingService->computeSearchScore($authenticity, $relationship, $semantic, $recency, $engagement),
                'reasons' => compact('authenticity', 'relationship', 'semantic', 'recency', 'engagement'),
            ];
        })
        ->sortByDesc('score')
        ->values()
        ->take(10);

        return response()->json($results);
    }
}
