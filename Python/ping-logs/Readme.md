# 用于监听本机网络波动

- 监测网络波动
- URL传输到服务器数据库中存储日志
- 可本地文件存储
- 仅检测

## 该项目有什么用

方便投诉你的运营商，让其网络保持稳定

## 如何使用

所需环境`ping3`

```python
pip install ping3
```

你需要准备一个`config.json`

```json
{
    "target_ips": {
      "需要ping的IP": {"location": "位置", "threshold_ms": 设置阈值, "log_method": "触发"},
      "需要ping的IP": {"location": "位置", "threshold_ms": 设置阈值, "log_method": "触发"},
      "需要ping的IP": {"location": "位置", "threshold_ms": 设置阈值, "log_method": "触发"}
    }
}
```

示例

```json
{
    "target_ips": {
      "10.10.50.1": {"location": "Home", "threshold_ms": 10, "log_method": "url"},
      "10.10.51.1": {"location": "Home2", "threshold_ms": 30, "log_method": "url"},
      "10.10.92.1": {"location": "Home3", "threshold_ms": 100, "log_method": "url"}
    }
}
```

阈值单位为MS，请根据你的网络环境进行调整

超出该阈值时则触发条件

log_method：`file`,`url`,`console`

