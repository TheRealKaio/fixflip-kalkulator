<?php
// Copy to config.php ON THE SERVER. Never commit the filled file.
return [
    'db' => ['host' => '', 'name' => '', 'user' => '', 'password' => ''],
    'api_origin' => 'https://api.neustart-immocheck.de',
    'allowed_origins' => ['https://neustart-immocheck.de', 'https://www.neustart-immocheck.de', 'https://api.neustart-immocheck.de'],
    'smtp' => ['host' => 'smtp.strato.de', 'port' => 465, 'encryption' => 'tls', 'user' => '', 'password' => '', 'from' => '', 'from_name' => 'Neustart ImmoCheck'],
    'admin' => ['first_name' => '', 'last_name' => '', 'email' => ''],
    // Generate independently: at least 64 random characters each. Keep both secret.
    'pepper' => '',
    'setup_key' => '',
];
