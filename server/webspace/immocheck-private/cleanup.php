<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require __DIR__.'/app.php';
$db=nic_db(nic_config());
nic_query($db,'DELETE FROM nic_sessions WHERE expires_at<?',[nic_now()]);
nic_query($db,'DELETE FROM nic_challenges WHERE expires_at<?',[nic_now()]);
nic_query($db,'DELETE FROM nic_rate_limits WHERE window_start<?',[nic_now(-86400)]);
nic_query($db,"DELETE FROM nic_users WHERE verified_at IS NULL AND role='user' AND created_at<?",[nic_now(-86400*7)]);
nic_query($db,'DELETE FROM nic_audit WHERE created_at<?',[nic_now(-86400*180)]);
echo "Bereinigung abgeschlossen.\n";
