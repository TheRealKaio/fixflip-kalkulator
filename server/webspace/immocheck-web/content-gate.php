<?php
declare(strict_types=1);

/**
 * STRATO HTML gate: suppress admin-disabled content before HTML reaches the browser.
 * Static assets remain direct. GitHub Pages cannot execute this PHP endpoint.
 */
ini_set('display_errors', '0');
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');

function nic_gate_fail(): never {
    http_response_code(503);
    echo '<!doctype html><meta charset="utf-8"><title>Vorübergehend nicht verfügbar</title><p>Die Seite ist vorübergehend nicht verfügbar.</p>';
    exit;
}

try {
    $relative = $_GET['path'] ?? '';
    if (!is_string($relative) || !preg_match('~^(?:[A-Za-z0-9_-][A-Za-z0-9_.-]*/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*\.html$~D', $relative)
        || str_contains($relative, '..') || $relative === 'content-gate.php') {
        http_response_code(404);
        exit;
    }

    $root = realpath(__DIR__);
    $page = realpath(__DIR__ . DIRECTORY_SEPARATOR . $relative);
    if ($root === false || $page === false || !str_starts_with($page, $root . DIRECTORY_SEPARATOR) || !is_file($page)) {
        http_response_code(404);
        exit;
    }

    $configFile = dirname(__DIR__) . '/immocheck-private/config.php';
    if (!is_file($configFile)) nic_gate_fail();
    $config = require $configFile;
    if (!is_array($config) || !isset($config['db']['host'], $config['db']['name'], $config['db']['user'], $config['db']['password'])) nic_gate_fail();
    $pdo = new PDO(
        'mysql:host=' . $config['db']['host'] . ';dbname=' . $config['db']['name'] . ';charset=utf8mb4',
        $config['db']['user'],
        $config['db']['password'],
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_EMULATE_PREPARES => false]
    );
    $payload = $pdo->query('SELECT payload FROM nic_settings WHERE id=1')->fetchColumn();
    if (!is_string($payload) || $payload === '') nic_gate_fail();
    $settings = json_decode($payload, true, 32, JSON_THROW_ON_ERROR);
    $rules = $settings['contentSections'] ?? [];
    if (!is_array($rules)) nic_gate_fail();

    $html = file_get_contents($page);
    if (!is_string($html)) nic_gate_fail();
    if (class_exists(DOMDocument::class)) {
        $dom = new DOMDocument('1.0', 'UTF-8');
        $previous = libxml_use_internal_errors(true);
        $loaded = $dom->loadHTML('<?xml encoding="UTF-8">' . $html, LIBXML_NONET | LIBXML_COMPACT);
        libxml_clear_errors();
        libxml_use_internal_errors($previous);
        if (!$loaded) nic_gate_fail();

        $xpath = new DOMXPath($dom);
        $nodes = $xpath->query('//*[@data-nic-content-key]');
        if ($nodes === false) nic_gate_fail();
        for ($i = $nodes->length - 1; $i >= 0; $i--) {
            $node = $nodes->item($i);
            if (!$node instanceof DOMElement) continue;
            $key = $node->getAttribute('data-nic-content-key');
            if (($rules[$key]['visible'] ?? true) === false && $node->parentNode) {
                $node->parentNode->removeChild($node);
            }
        }
        $output = $dom->saveHTML();
        if (!is_string($output)) nic_gate_fail();
        $html = preg_replace('/^<\?xml encoding="UTF-8">/', '', $output) ?? $output;
    } else {
        // Fail closed: without an HTML parser we cannot reliably remove nested content.
        nic_gate_fail();
    }

    echo $html;
} catch (Throwable $error) {
    error_log('ImmoCheck HTML gate failure: ' . get_class($error));
    nic_gate_fail();
}
