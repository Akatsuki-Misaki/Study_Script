<?php
//允许跨域
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// 获取用户 IP 地址
$ip_address = $_SERVER['HTTP_X_FORWARDED_FOR'];
// 可能会获取到多个ip，仅此使用最前面的IP
$ip_address = explode(',', $ip_address)[0];

$info_ip = file_get_contents("https://v2.xxapi.cn/api/ip?ip=".$ip_address);
// 获取网络json的data中的address
$info_ip = json_decode($info_ip, true);
$info_ip_address = $info_ip['data']['address'];
$info_ip_isp = $info_ip['data']['isp'];
$format = $_GET['format'];

if($format === 'json'){
    if($ip_address !== ''){
        header('Content-Type: application/json');
        http_response_code(200);
        $data = array(
            'ip' => $ip_address,
            'address' => $info_ip_address,
            'isp' => $info_ip_isp
        );
        echo json_encode($data);
        exit();
    }else{
        header('Content-Type: application/json');
        http_response_code(403);
        $data = array(
            'info' => '获取失败'
        );
        echo json_encode($data);
        exit();
    }
}else if($format === 'text'){
    echo $ip_address;
    exit();
}



// 获取文件名
$file = $_SERVER['REQUEST_URI'];
// 获取文件类型
$file_info = pathinfo($file);
// 获取文件后缀名
$file_ext = $file_info['extension'];
// 定义允许的后缀
$allow_ext = array('js', 'css', 'png', 'jpg', 'jpeg', 'gif', 'ico', 'json', 'txt', 'moc', 'moc3', 'svg', 'webp' , 'hosts', 'ttf', 'woff', 'woff2', 'eot', 'sgmodule', 'apk', 'zip', 'exe');
if($_SERVER['REQUEST_URI'] == '/'){
    // 输出首页
    header('content-type: text/html;charset=utf-8');
    echo file_get_contents('jsd.html');
    exit();
}
if($_SERVER['REQUEST_URI'] == '/help'){
    header('content-type: application/json;charset=utf-8');
    echo json_encode(array(
        'code' => 200,
        'title'=> 'Welcome to use OvOfish Studio API',
        'message' => '这是一个反代接口,如有需要请联系管理员。',
        'How_to_use' => '您只需将原有的域名更改为本站域名如需要使用jsdelivr的反代请添加/jsd，如需要raw.githubusercontent.com则添加/gh',
        'support_list' => '支持的接口：'.implode(',', array('/gh', '/jsd', '/unpkg' ,'/releases')),
        'file_ext_list' => '允许的后缀列表：'.implode(',', $allow_ext)
    ));
    exit();
}
if($_SERVER['REQUEST_URI'] == '/contact'){
    header('content-type: application/json;charset=utf-8');
    echo json_encode(array(
        'code' => 200,
        'title'=> 'Welcome to use OvOfish Studio API',
        'message' => '这是一个反代接口,如有需要请联系管理员。',
        'QQnumber' => '1709964150',
        'email' => 'mirai@lolicon.team',
        'blog' => 'https://lolicon.team'
    ));
    exit();
}
if(empty($file_ext)){
    header('content-type: application/json;charset=utf-8');
    echo json_encode(array(
        'code' => 403,
        'title'=> 'Welcome to use OvOfish Studio API',
        'message' => '未能识别到文件类型',
        'file_ext' => '当前文件类型为：NULL',
        'file_ext_list' => '允许的后缀列表：'.implode(',', $allow_ext)
    ));
    exit();
}
// 判断后缀是否在允许的后缀列表中 如果不在，则返回403
if(!in_array($file_ext, $allow_ext)){
    header('content-type: application/json;charset=utf-8');
    echo json_encode(array(
        'code' => 403,
        'title'=> 'Welcome to OvOfish Studio API',
        'message' => '该文件类型不被允许, 请不要滥用本接口。',
        'file_ext' => '当前文件类型为：'.$file_ext,
        'file_ext_list' => '允许的后缀列表：'.implode(',', $allow_ext)
    ));
    exit();
}
$mimetype = get_mimetype($file_info['extension']);
header('content-type:'. $mimetype .';charset=utf-8');
// 代理的域名及使用的协议最后不用加/
$target_host = "";
$new_request_uri = "";
if (strpos($_SERVER['REQUEST_URI'], '/gh') === 0) {
    $target_host = "https://raw.githubusercontent.com";
    $new_request_uri = substr($_SERVER['REQUEST_URI'], 3);
} elseif (strpos($_SERVER['REQUEST_URI'], '/jsd') === 0) {
    $target_host = "https://cdn.jsdelivr.net";
    $new_request_uri = substr($_SERVER['REQUEST_URI'], 5);
}elseif (strpos($_SERVER['REQUEST_URI'], '/unpkg') === 0) {
        $target_host = "https://unpkg.com";
        $new_request_uri = substr($_SERVER['REQUEST_URI'], 6);
}elseif (strpos($_SERVER['REQUEST_URI'], '/releases') === 0) {
    $target_host = "https://github.com";
    $new_request_uri = substr($_SERVER['REQUEST_URI'], 9);
} else {
    header('content-type: application/json;charset=utf-8');
    // 返回404状态
    http_response_code(404);
    echo json_encode(array(
        'code' => 404,
        'title'=> 'Welcome to use OvOfish Studio API',
        'message' => '无效的请求路径'
    ));
    exit;
}
// 解析url参数
function get_request_params() 
{ 
    $url = $_SERVER["REQUEST_URI"]; 
    $refer_url = parse_url($url); 
    $params = $refer_url['query']; 
    $arr = array(); 
    if(!empty($params)) 
    { 
        $paramsArr = explode('&',$params); 
        foreach($paramsArr as $k=>$v) 
        { 
            $a = explode('=',$v); 
            $arr[$a[0]] = $a[1]; 
        } 
    } 
    return $arr; 
}
// 解析HTTP响应头
function parse_headers($headers)
{
    global $root, $top;
    foreach( $headers as $k=>$v )
    {
        $t = explode( ':', $v, 2 );
        if( isset( $t[1] ) )
        {
            if(strcasecmp('Set-Cookie',trim($t[0]))==0)
            {
                $targetcookie=trim( $t[1] ).";";
                $res_cookie=preg_replace("/domain=.*?;/","domain=".$_SERVER["SERVER_NAME"].";",$targetcookie);
                $res_cookie=substr($res_cookie,0,strlen($res_cookie)-1); 
                header("Set-Cookie: ".$res_cookie);
            }
            elseif(strcasecmp('Content-Type',trim($t[0]))==0)
            {
                header("Content-Type: ".trim( $t[1] ));
            }
            elseif(strcasecmp('Location',trim( $t[0] ))==0)
            {
                $relocation=str_replace($protocal_host['host'],$_SERVER["SERVER_NAME"],trim( $t[1] ));
                header("Location: ".$relocation);
            }
            elseif(strcasecmp('cache-control',trim( $t[0] ))==0)
            {
                header("cache-control: ".trim( $t[1] ));
            }
            else
                continue;
        }
    }
    return;
}
// 组装HTTP请求头
$opts = array(
    'http'=>array(
        'method'=>$_SERVER['REQUEST_METHOD'],
        'header'=>"Accept-language: zh-CN\r\n" .
                "user-agent: {$_SERVER['HTTP_USER_AGENT']}\r\n".
                "Cookie: ".array_to_str($_COOKIE)."\r\n"
    )
);
$context = stream_context_create($opts);
// 发送请求
$homepage = file_get_contents($target_host.'/'.$new_request_uri,false,$context);
if ($homepage === FALSE) {
    header('content-type: application/json;charset=utf-8');
    echo json_encode(array(
        'code' => 404,
        'title'=> 'Welcome to use OvOfish Studio API',
        'message' => '未能找到文件',
        'file_ext' => '当前文件类型为：'.$file_ext
    ));
    exit;
}
function get_mimetype($extension) {
    // MIME类型数组
    $ct = array(
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
        'zip' => 'application/zip',
        'exe' => 'application/octet-stream',
        'apk' => 'application/vnd.android.package-archive'
    );
    return isset($ct[strtolower($extension)]) ? $ct[strtolower($extension)] : 'text/plain';
}
function array_to_str($array)  
{  
    $string="";
    if (is_array($array)) 
    {  
        foreach ($array as $key => $value) 
        {   
            if(!empty($string))
                $string.="; ".$key."=".$value;
            else
                $string.=$key."=".$value;
        }   
    } else 
    {  
            $string = $array;  
    }      
    return $string;  
}  
// 输出网页内容
echo $homepage;



?>