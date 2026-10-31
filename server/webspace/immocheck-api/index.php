<?php
declare(strict_types=1);
ini_set('display_errors', '0');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
try {
    require dirname(__DIR__) . '/immocheck-private/app.php';
    nic_run();
} catch (Throwable $e) {
    if (isset($GLOBALS['nic_db']) && $GLOBALS['nic_db']->inTransaction()) $GLOBALS['nic_db']->rollBack();
    // Never send credentials, SQL errors, email codes or stack traces to clients.
    error_log('ImmoCheck API failure: ' . get_class($e));
    http_response_code(503);
    echo json_encode(['error' => 'Der Dienst ist derzeit nicht verfügbar. Bitte später erneut versuchen.']);
}
