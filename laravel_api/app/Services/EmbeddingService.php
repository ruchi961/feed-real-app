<?php

namespace App\Services;

use Illuminate\Support\Str;

class EmbeddingService
{
    public function generate(string $text): array
    {
        $hash = md5(trim(strtolower($text)));
        return array_map(fn ($value) => ord($value) / 255, str_split(substr($hash, 0, 32)));
    }

    public function similarity(array $vectorA, ?array $vectorB = null): float
    {
        $vectorA = is_array($vectorA) ? $vectorA : [];
        $vectorB = is_array($vectorB) ? $vectorB : [];

        if (empty($vectorA) || empty($vectorB)) {
            return 0.0;
        }

        $length = min(count($vectorA), count($vectorB));
        $dot = 0.0;
        $normA = 0.0;
        $normB = 0.0;

        for ($i = 0; $i < $length; $i++) {
            $dot += $vectorA[$i] * $vectorB[$i];
            $normA += $vectorA[$i] ** 2;
            $normB += $vectorB[$i] ** 2;
        }

        if ($normA === 0.0 || $normB === 0.0) {
            return 0.0;
        }

        return round($dot / (sqrt($normA) * sqrt($normB)), 4);
    }

    public function authenticityScore($post): float
    {
        return round(min(1.0, max(0.0, $post->authenticity_score ?? 0.7)), 4);
    }

    public function relationshipScore($user, $post): float
    {
        if ($user->id === $post->user_id) {
            return 0.2;
        }

        return $user->id && $post->user_id ? 0.5 : 0.1;
    }

    public function timeDecay($createdAt): float
    {
        $ageHours = max(1, now()->diffInHours($createdAt));
        return round(1.0 / (1.0 + ($ageHours / 36.0)), 4);
    }

    public function engagementScore($post): float
    {
        $reactions = $post->interactions->where('type', 'reaction')->count();
        $views = $post->interactions->where('type', 'view')->count();
        $replies = $post->interactions->where('type', 'reply')->count();

        return round(min(1.0, ($reactions * 0.5 + $replies * 0.8 + $views * 0.1) / 10), 4);
    }

    public function computeFeedScore(float $authenticity, float $relationship, float $semantic, float $recency, float $engagement): float
    {
        return round((0.30 * $authenticity) + (0.25 * $relationship) + (0.25 * $semantic) + (0.10 * $recency) + (0.10 * $engagement), 4);
    }

    public function computeSearchScore(float $authenticity, float $relationship, float $semantic, float $recency, float $engagement): float
    {
        return round((0.25 * $authenticity) + (0.20 * $relationship) + (0.35 * $semantic) + (0.10 * $recency) + (0.10 * $engagement), 4);
    }
}
