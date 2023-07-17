# -*- coding: utf-8 -*-
import requests

# 定义API端点和请求数据
api_url = 'http://127.0.0.1:5000/add_record'
data = {
    'AssetID': 'HD000480',
    'Type': 'test',
}

#  发送POST请求调用API
response = requests.post(api_url, json=data)

# 检查响应状态码
if response.status_code == 200:
    # 提取并处理响应数据

    # 处理结果
    print(result)
else:
    print('API调用失败')


