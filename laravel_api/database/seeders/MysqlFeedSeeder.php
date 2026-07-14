<?php

namespace Database\Seeders;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class MysqlFeedSeeder extends Seeder
{
    public function run(): void
    {
        $users = User::all();
        if ($users->isEmpty()) {
            $this->call(TestUserSeeder::class);
            $users = User::all();
        }

        $texts = [
            'Funny travel story from last week with a tiny cafe and jazz band.',
            'Quiet morning coffee and rainy city streets in my favorite neighborhood.',
            'Weekend hike with sunrise views and a surprising picnic at the summit.',
            'A simple dinner party with friends, candles, and warm conversation.',
            'Morning run through the park and a beautiful sunrise over the lake.',
            'A spontaneous road trip, bad maps, and the best local bakery.',
            'A little garden update with fresh herbs and tiny handmade pottery.',
            'An honest photo from the beach with wind in my hair and no filters.',
            'A cozy evening reading by the window with tea and soft music.',
            'Travel memories from an old train station and a long conversation.',
            'Autumn walk with bright leaves, warm jackets, and a dog crossing the road.',
            'A candid story about a missed flight and a lucky hostel surprise.',
            'Cooking a simple meal with homemade bread and a favorite playlist.',
            'Small weekend win: finishing a painting after weeks of waiting.',
            'The city felt calm after the storm and everyone seemed lighter.',
            'An honest reflection on balancing work, rest, and being present.',
            'A perfect evening with street music, dim lights, and an old friend.',
            'Sunset over the coast and the feeling that time slows down.',
            'A tiny notebook filled with sketches from a long train ride.',
            'The kind of day that makes you believe small moments matter.',
        ];

        foreach ($texts as $index => $text) {
            $user = $users[$index % $users->count()];
            $post = Post::create([
                'user_id' => $user->id,
                'text' => $text,
                'image_url' => 'https://example.com/images/' . ($index + 1) . '.jpg',
            ]);

            $post->load('author');

            $storageDir = public_path('uploads/posts/' . $post->user_id);
            if (!is_dir($storageDir)) {
                mkdir($storageDir, 0777, true);
            }

            $fileName = 'post_' . $post->id . '.jpg';
            file_put_contents($storageDir . '/' . $fileName, 'dummy');

            DB::table('post_images')->insert([
                'post_id' => $post->id,
                'image_folderpath' => 'uploads/posts/' . $post->user_id,
                'imagefilename' => $fileName,
                'width' => 1200,
                'height' => 800,
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            DB::table('post_scores')->insert([
                'post_id' => $post->id,
                'post_views' => 80 + ($index * 3),
                'post_authenticity_score' => round(0.55 + ($index % 5) * 0.08, 4),
                'post_semantic_score' => round(0.4 + ($index % 6) * 0.09, 4),
                'post_time_decay_score' => round(0.6 + ($index % 4) * 0.08, 4),
                'post_relationship_score' => round(0.4 + ($index % 4) * 0.1, 4),
                'post_final_score' => round(0.55 + ($index % 5) * 0.07, 4),
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            DB::table('post_authenticity_scores')->insert([
                'post_id' => $post->id,
                'filter_score' => round(0.2 + ($index % 4) * 0.1, 4),
                'image_quality' => round(0.6 + ($index % 5) * 0.07, 4),
                'caption_originality' => round(0.7 + ($index % 4) * 0.06, 4),
                'created_at' => now(),
                'updated_at' => now(),
            ]);

            foreach (range(1, 2) as $reactionIndex) {
                DB::table('post_reactions')->insert([
                    'post_id' => $post->id,
                    'user_id_of_post' => $user->id,
                    'current_user_id' => $users[($index + $reactionIndex) % $users->count()]->id,
                    'reaction_type' => ['like', 'love', 'laugh', 'wow'][$reactionIndex % 4],
                    'created_at' => now(),
                    'updated_at' => now(),
                ]);
            }

            DB::table('post_comments')->insert([
                'post_id' => $post->id,
                'user_id_of_user' => $user->id,
                'current_user_id' => $users[($index + 1) % $users->count()]->id,
                'comment' => 'Nice post #' . ($index + 1),
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }
    }
}
