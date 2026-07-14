<?php

namespace Database\Factories;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Post>
 */
class PostFactory extends Factory
{
    protected $model = Post::class;

    public function definition(): array
    {
        return [
            'user_id' => User::factory(),
            'text' => fake()->sentence(),
            'image_url' => fake()->imageUrl(),
            'embedding' => ['score' => fake()->randomFloat(2, 0.1, 0.99)],
            'authenticity_score' => fake()->randomFloat(2, 0.2, 0.95),
        ];
    }
}
