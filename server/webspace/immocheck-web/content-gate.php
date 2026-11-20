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

    $root = realpath(defined('NIC_CONTENT_ROOT') ? NIC_CONTENT_ROOT : __DIR__);
    $page = realpath($root . DIRECTORY_SEPARATOR . $relative);
    if ($root === false || $page === false || !str_starts_with($page, $root . DIRECTORY_SEPARATOR) || !is_file($page)) {
        http_response_code(404);
        exit;
    }

    $publicRoot = defined('NIC_PUBLIC_ROOT') ? NIC_PUBLIC_ROOT : __DIR__;
    $configFile = dirname($publicRoot) . '/immocheck-private/config.php';
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
        // libxml's HTML serializer can turn Unicode in raw-text elements into
        // HTML entities. Browsers do not decode those in JavaScript or CSS.
        // Mask only their bodies, preserving their attributes and ancestry so
        // disabled script/style elements are still removed by the same filter.
        $rawBodies = [];
        do {
            $rawPrefix = 'NIC_RAW_' . bin2hex(random_bytes(16)) . '_';
        } while (str_contains($html, $rawPrefix));
        $rawPattern = <<<'NIC_RAW_PATTERN'
~<!--.*?-->|(<(script|style)\b(?:[^>"']|"[^"]*"|'[^']*')*>)(.*?)(</\2\s*>)~is
NIC_RAW_PATTERN;
        $masked = preg_replace_callback($rawPattern, static function (array $match) use (&$rawBodies, $rawPrefix): string {
            if (!isset($match[1]) || $match[1] === '') return $match[0];
            $placeholder = $rawPrefix . count($rawBodies);
            $rawBodies[$placeholder] = $match[3];
            return $match[1] . $placeholder . $match[4];
        }, $html);
        if (!is_string($masked)) nic_gate_fail();
        $dom = new DOMDocument('1.0', 'UTF-8');
        $previous = libxml_use_internal_errors(true);
        $loaded = $dom->loadHTML('<?xml encoding="UTF-8">' . $masked, LIBXML_NONET | LIBXML_COMPACT);
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
        // Remove menu tiles disabled in both viewport categories before HTML delivery.
        // Viewport-specific permissions are enforced by initial critical CSS below;
        // a server cannot reliably infer CSS viewport width on a first HTTP request.
        $navVisibility = $settings['navigationVisibility'] ?? [];
        $navOptions = $xpath->query('//*[contains(concat(" ", normalize-space(@class), " "), " deal-type-option ")]');
        if ($navOptions === false) nic_gate_fail();
        $menuKeys = ['budget','own','rent','flip','finance','settlement'];
        $hideOnMobile = [];
        $hideOnDesktop = [];
        for ($i = $navOptions->length - 1; $i >= 0; $i--) {
            $option = $navOptions->item($i);
            if (!$option instanceof DOMElement) continue;
            $key = $option->getAttribute('data-calculator');
            if (!in_array($key, $menuKeys, true)) {
                $href = $option->getAttribute('href') ?: $option->getAttribute('data-href');
                $byPath = ['/budget/'=>'budget','/eigennutzung/'=>'own','/vermietung/'=>'rent','/fix-flip/'=>'flip','/finanzierungsrechner/'=>'finance','/nebenkostenabrechnung/'=>'settlement'];
                $key = $byPath[$href] ?? '';
            }
            if (!in_array($key, $menuKeys, true)) continue;
            $mobile = ($navVisibility['mobile'][$key] ?? true) !== false;
            $desktop = ($navVisibility['desktop'][$key] ?? true) !== false;
            if (!$mobile && !$desktop) {
                $option->parentNode?->removeChild($option);
            } else {
                // Add a stable attribute even to legacy tiles without data-calculator.
                $option->setAttribute('data-nic-nav-key', $key);
                if (!$mobile) $hideOnMobile[$key] = true;
                if (!$desktop) $hideOnDesktop[$key] = true;
            }
        }
        $criticalNavCss = [];
        foreach (array_keys($hideOnMobile) as $key) $criticalNavCss[] = '@media(max-width:700px){[data-nic-nav-key="' . $key . '"]{display:none!important}}';
        foreach (array_keys($hideOnDesktop) as $key) $criticalNavCss[] = '@media(min-width:701px){[data-nic-nav-key="' . $key . '"]{display:none!important}}';
        $output = $dom->saveHTML();
        if (!is_string($output)) nic_gate_fail();
        // Restore only placeholders that survived removal of disabled nodes.
        $html = strtr($output, $rawBodies);
        $html = preg_replace('/<\?xml encoding="UTF-8">/', '', $html, 1) ?? $html;
        if ($criticalNavCss) {
            $html = str_replace('</head>', '<style id="nic-server-menu-visibility">' . implode('', $criticalNavCss) . '</style></head>', $html);
        }

    } else {
        // Fail closed: without an HTML parser we cannot reliably remove nested content.
        nic_gate_fail();
    }

    header('X-NIC-Filtered: 1');
    echo $html;
} catch (Throwable $error) {
    error_log('ImmoCheck HTML gate failure: ' . get_class($error));
    nic_gate_fail();
}
