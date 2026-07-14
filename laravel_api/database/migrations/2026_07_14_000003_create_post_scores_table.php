<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('post_scores', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('post_id');
            $table->integer('post_views')->default(0);
            $table->float('post_authenticity_score')->default(0);
            $table->float('post_semantic_score')->default(0);
            $table->float('post_time_decay_score')->default(0);
            $table->float('post_relationship_score')->default(0);
            $table->float('post_final_score')->default(0);
            $table->timestamps();

            $table->foreign('post_id')->references('id')->on('posts')->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('post_scores');
    }
};
