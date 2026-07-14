<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return ['status' => 'ok', 'message' => 'Laravel API is running'];
});
