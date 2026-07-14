<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Post;
use App\Services\EmbeddingService;
use Illuminate\Http\Request;

class PostController extends Controller
{
    public function store(Request $request, EmbeddingService $embeddingService)
    {
        $request->validate([
            'text' => ['required', 'string'],
            'image_url' => ['nullable', 'url'],
        ]);

        $post = Post::create([
            'user_id' => $request->user()->id,
            'text' => $request->input('text'),
            'image_url' => $request->input('image_url'),
            'authenticity_score' => $request->input('authenticity_score', null),
        ]);

        $vector = $embeddingService->generate($post->text);
        $post->embedding = $vector;
        $post->save();

        return response()->json($post, 201);
    }
}
