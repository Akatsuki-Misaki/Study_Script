<?php
//允许跨域
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// 获取ip
$ip_address = $_SERVER['X-Real-IP'];


// 将获取到的IP进行地址查询 小小API

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
    }else{
        header('Content-Type: application/json');
        http_response_code(403);
        $data = array(
            'info' => '获取失败'
        );
        echo json_encode($data);
    }
}else if($format === 'text'){
    echo $ip_address;
}else{
    header('Content-Type: application/json');
    http_response_code(403);
    $data = array(
        'info' => '服务器认为格式有误(EC: 3).ο(=•ω＜=)ρ⌒☆'
    );
    echo json_encode($data);
}
?>