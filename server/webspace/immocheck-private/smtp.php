<?php
declare(strict_types=1);
// Minimal SMTP client: implicit TLS on 465 or mandatory STARTTLS on 587.
// Certificate and peer-name verification are enabled; no cleartext fallback.
function nic_send_code(array $smtp, string $to, string $code): void {
    foreach ([$to, $smtp['from'], $smtp['user'], $smtp['host'], $smtp['from_name']] as $value) {
        if (!is_string($value) || preg_match('/[\r\n\x00]/', $value)) throw new RuntimeException('SMTP configuration');
    }
    if (!filter_var($to, FILTER_VALIDATE_EMAIL) || !filter_var($smtp['from'], FILTER_VALIDATE_EMAIL)) throw new RuntimeException('SMTP address');
    $implicit = $smtp['encryption'] === 'tls' && (int)$smtp['port'] === 465;
    $starttls = $smtp['encryption'] === 'starttls' && (int)$smtp['port'] === 587;
    if (!$implicit && !$starttls) throw new RuntimeException('SMTP TLS required');
    $ctx = stream_context_create(['ssl' => ['verify_peer' => true, 'verify_peer_name' => true, 'peer_name' => $smtp['host'], 'allow_self_signed' => false]]);
    $socket = stream_socket_client(($implicit ? 'tls://' : 'tcp://') . $smtp['host'] . ':' . $smtp['port'], $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx);
    if (!$socket) throw new RuntimeException('SMTP unavailable');
    stream_set_timeout($socket, 15);
    $read = function (array $allowed) use ($socket): void {
        $lines = 0;
        do {
            $line = fgets($socket, 4096);
            if ($line === false || ++$lines > 100) throw new RuntimeException('SMTP response');
            $status = (int)substr($line, 0, 3);
            $more = isset($line[3]) && $line[3] === '-';
        } while ($more);
        if (!in_array($status, $allowed, true)) throw new RuntimeException('SMTP rejected');
    };
    $write = function (string $data) use ($socket): void {
        $offset = 0;
        while ($offset < strlen($data)) {
            $n = fwrite($socket, substr($data, $offset));
            if (!$n) throw new RuntimeException('SMTP write');
            $offset += $n;
        }
    };
    $command = function (string $line, array $allowed) use ($write, $read): void { $write($line . "\r\n"); $read($allowed); };
    try {
        $read([220]); $command('EHLO immocheck.local', [250]);
        if ($starttls) {
            $command('STARTTLS', [220]);
            if (stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLS_CLIENT) !== true) throw new RuntimeException('SMTP TLS');
            $command('EHLO immocheck.local', [250]);
        }
        $command('AUTH LOGIN', [334]);
        $command(base64_encode($smtp['user']), [334]);
        $command(base64_encode($smtp['password']), [235]);
        $command('MAIL FROM:<' . $smtp['from'] . '>', [250]);
        $command('RCPT TO:<' . $to . '>', [250, 251]);
        $command('DATA', [354]);
        $name = '=?UTF-8?B?' . base64_encode($smtp['from_name']) . '?=';
        $headers = 'From: ' . $name . ' <' . $smtp['from'] . ">\r\nTo: <" . $to . ">\r\nSubject: Dein ImmoCheck-Anmeldecode\r\nDate: " . date(DATE_RFC2822) . "\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n";
        $body = "Dein Anmeldecode lautet: $code\n\nEr ist 10 Minuten gültig und nur einmal verwendbar.\nWenn du diesen Code nicht angefordert hast, ignoriere diese E-Mail.\n";
        $command($headers . "\r\n" . rtrim(chunk_split(base64_encode($body), 76, "\r\n")) . "\r\n.", [250]);
        $command('QUIT', [221]);
    } finally { fclose($socket); }
}
