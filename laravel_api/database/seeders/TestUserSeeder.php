<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;

class TestUserSeeder extends Seeder
{
    public function run(): void
    {
        $users = [
            [
                'name' => 'Alice Rider',
                'email' => 'alice@example.com',
                'password' => bcrypt('password'),
                'bio' => 'I love authentic travel stories and daily life posts.',
                'interests' => ['travel', 'stories', 'authenticity'],
            ],
            [
                'name' => 'Bob Walker',
                'email' => 'bob@example.com',
                'password' => bcrypt('password'),
                'bio' => 'Food, friends, and real moments in the city.',
                'interests' => ['food', 'city', 'friends'],
            ],
            [
                'name' => 'Cara Nguyen',
                'email' => 'cara@example.com',
                'password' => bcrypt('password'),
                'bio' => 'I share quiet mornings, local cafés, and small creative wins.',
                'interests' => ['coffee', 'creativity', 'community'],
            ],
            [
                'name' => 'Darius Cole',
                'email' => 'darius@example.com',
                'password' => bcrypt('password'),
                'bio' => 'Weekend hikes, photography, and honest life updates.',
                'interests' => ['hiking', 'photography', 'nature'],
            ],
            [
                'name' => 'Eva Martinez',
                'email' => 'eva@example.com',
                'password' => bcrypt('password'),
                'bio' => 'Cooking, music, and everyday stories from home.',
                'interests' => ['cooking', 'music', 'home'],
            ],
        ];

        foreach ($users as $user) {
            User::updateOrCreate(
                ['email' => $user['email']],
                [
                    'name' => $user['name'],
                    'password' => $user['password'],
                    'bio' => $user['bio'],
                    'interests' => $user['interests'],
                ]
            );
        }
    }
}
