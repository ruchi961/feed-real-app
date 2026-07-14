<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interaction;
use Illuminate\Http\Request;

class InteractionController extends Controller
{
    public function store(Request $request)
    {
        $request->validate([
            'post_id' => ['required', 'integer', 'exists:posts,id'],
            'type' => ['required', 'string', 'in:view,reply,reaction,comment'],
            'payload' => ['nullable', 'array'],
        ]);

        $type = $request->input('type');
        $payload = $request->input('payload') ?? [];

        if ($type === 'reaction') {
            $allowed = ['like', 'love', 'laugh', 'wow'];
            $rt = $payload['reaction_type'] ?? null;
            if (!in_array($rt, $allowed, true)) {
                return response()->json(['message' => 'Invalid reaction type'], 422);
            }
        }

        if ($type === 'comment') {
            $comment = $payload['comment'] ?? null;
            if (!is_string($comment) || trim($comment) === '') {
                return response()->json(['message' => 'Comment cannot be empty'], 422);
            }
        }

        $interaction = Interaction::create([
            'user_id' => $request->user()->id,
            'post_id' => $request->input('post_id'),
            'type' => $type,
            'payload' => $payload,
        ]);

        return response()->json($interaction, 201);
    }
}
