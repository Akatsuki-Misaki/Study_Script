<?php
header('Access-Control-Allow-Origin: *');

// 获取请求路径和文件信息
$file = $_SERVER['REQUEST_URI'];
$file_info = pathinfo($file);
$file_ext = isset($file_info['extension']) ? $file_info['extension'] : '';

// 允许的文件后缀
$allow_ext = ['js', 'css', 'png', 'jpg', 'jpeg', 'gif', 'ico', 'json', 'txt', 'moc', 'moc3', 'svg', 'webp', 'hosts', 'ttf', 'woff', 'woff2', 'eot', 'sgmodule'];

// 首页和帮助页
if ($_SERVER['REQUEST_URI'] == '/') {
    header('content-type: text/html;charset=utf-8');
    echo file_get_contents('jsd.html');
    exit();
}

if ($_SERVER['REQUEST_URI'] == '/help') {
    header('content-type: application/json;charset=utf-8');
    echo json_encode([
        'code' => 200,
        'title' => 'Welcome to use OvOfish Studio API',
        'message' => '这是一个反代接口，如有需要请联系管理员。',
        'How_to_use' => '您只需将原有的域名更改为本站域名，如需要使用jsdelivr的反代请添加/jsd，如需要raw.githubusercontent.com则添加/gh',
        'support_list' => '支持的接口：' . implode(',', ['/gh', '/jsd', '/unpkg']),
        'file_ext_list' => '允许的后缀列表：' . implode(',', $allow_ext)
    ]);
    exit();
}

if ($_SERVER['REQUEST_URI'] == '/contact') {
    header('content-type: application/json;charset=utf-8');
    echo json_encode([
        'code' => 200,
        'title' => 'Welcome to use OvOfish Studio API',
        'message' => '这是一个反代接口，如有需要请联系管理员。',
        'QQnumber' => '1709964150',
        'email' => 'i@ovofish.com',
	    'blog' => 'https://blog.ovofish.com'
    ]);
    exit();
}

// 检查文件类型是否允许
if (empty($file_ext)) {
    header('content-type: application/json;charset=utf-8');
    echo json_encode([
        'code' => 403,
        'title' => 'Welcome to use OvOfish Studio API',
        'message' => '未能识别到文件类型',
        'file_ext' => '当前文件类型为：NULL',
        'file_ext_list' => '允许的后缀列表：' . implode(',', $allow_ext)
    ]);
    exit();
}

if (!in_array($file_ext, $allow_ext)) {
    header('content-type: application/json;charset=utf-8');
    echo json_encode([
        'code' => 403,
        'title' => 'Welcome to OvOfish Studio API',
        'message' => '该文件类型不被允许，请不要滥用本接口。',
        'file_ext' => '当前文件类型为：' . $file_ext,
        'file_ext_list' => '允许的后缀列表：' . implode(',', $allow_ext)
    ]);
    exit();
}

// 获取 MIME 类型
function get_mimetype($extension) {
    $mime_types = [
        'js' => 'application/javascript',
        'css' => 'text/css',
        'png' => 'image/png',
        'jpg' => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'gif' => 'image/gif',
        'ico' => 'image/vnd.microsoft.icon',
        'json' => 'application/json',
        'txt' => 'text/plain',
        'moc' => 'text/plain',
        'moc3' => 'text/plain',
        'svg' => 'image/svg+xml',
        'webp' => 'image/webp',
        'ttf' => 'font/ttf',
        'woff' => 'font/woff',
        'woff2' => 'font/woff2',
        'eot' => 'application/vnd.ms-fontobject'
    ];
    return $mime_types[strtolower($extension)] ?? 'text/plain';
}

$mimetype = get_mimetype($file_ext);
header('content-type:' . $mimetype . ';charset=utf-8');

// 代理目标域名
$target_host = "";
$new_request_uri = "";

if (strpos($_SERVER['REQUEST_URI'], '/gh') === 0) {
    $target_host = "https://raw.githubusercontent.com";
    $new_request_uri = substr($_SERVER['REQUEST_URI'], 3);
} elseif (strpos($_SERVER['REQUEST_URI'], '/jsd') === 0) {
    $target_host = "https://cdn.jsdelivr.net";
    $new_request_uri = substr($_SERVER['REQUEST_URI'], 4);
} elseif (strpos($_SERVER['REQUEST_URI'], '/unpkg') === 0) {
    $target_host = "https://unpkg.com";
    $new_request_uri = substr($_SERVER['REQUEST_URI'], 6);
} else {
    header('content-type: application/json;charset=utf-8');
    http_response_code(404);
    echo json_encode([
        'code' => 404,
        'title' => 'Welcome to use OvOfish Studio API',
        'message' => '无效的请求路径'
    ]);
    exit;
}

// 确保路径以 / 开头
$new_request_uri = '/' . ltrim($new_request_uri, '/');

// 使用 curl 获取远程文件（支持自动重定向）
function fetch_url($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // 跟随 301/302 重定向
    curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT'] ?? 'Mozilla/5.0');
    $result = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return $http_code == 200 ? $result : false;
}

// 发起请求
$homepage = fetch_url($target_host . $new_request_uri);

if ($homepage === false) {
    header('content-type: application/json;charset=utf-8');
    http_response_code(404);
    echo json_encode([
        'code' => 404,
        'title' => 'Welcome to use OvOfish Studio API',
        'message' => '文件获取失败',
        'debug' => [
            'target_url' => $target_host . $new_request_uri,
        ]
    ]);
    exit;
}

// 输出文件内容
echo $homepage;
?>