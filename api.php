<?php
// API do painel (hospedagem com PHP, ex.: HostGator). Mesma função do server.py.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
$dir = __DIR__;
$passFile = $dir . '/admin_password.txt';
if (!file_exists($passFile)) file_put_contents($passFile, 'admin123');
$pass = trim(file_get_contents($passFile));
$given = $_SERVER['HTTP_X_PASS'] ?? '';
$ok = hash_equals($pass, $given);
$a = $_GET['a'] ?? '';

function out($code, $arr) { http_response_code($code); echo json_encode($arr); exit; }

if ($a === 'check') out($ok ? 200 : 401, ['ok' => $ok]);
if (!$ok) out(401, ['error' => 'senha incorreta']);
if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['error' => 'método inválido']);

if ($a === 'config') {
    $data = json_decode(file_get_contents('php://input'), true);
    if (!is_array($data)) out(400, ['error' => 'json inválido']);
    file_put_contents($dir . '/config.json', json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    out(200, ['ok' => true]);
}

if ($a === 'upload') {
    $name = preg_replace('/[^A-Za-z0-9._-]/', '_', basename($_GET['name'] ?? 'video.mp4'));
    $ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));
    if (!in_array($ext, ['mp4', 'webm', 'mov', 'm4v'])) out(400, ['error' => 'use mp4, webm, mov ou m4v']);
    if (!is_dir($dir . '/videos')) mkdir($dir . '/videos', 0755, true);
    if (file_exists($dir . "/videos/$name")) $name = pathinfo($name, PATHINFO_FILENAME) . '_' . bin2hex(random_bytes(2)) . ".$ext";
    $in = fopen('php://input', 'rb');
    $outf = fopen($dir . "/videos/$name", 'wb');
    if (!$outf) out(500, ['error' => 'sem permissão na pasta videos']);
    stream_copy_to_stream($in, $outf);
    fclose($in); fclose($outf);
    out(200, ['src' => "videos/$name"]);
}
out(404, ['error' => 'not found']);
