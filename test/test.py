import requests
import time


def woshishabi():
    print("wo bu shi sha bi")

# 定义要测试的 URL
url = 'http://localhost:5000/update_asset'

# 准备要发送的数据，以 JSON 格式
data = {'AssetID': 'test03', 'Comments': 'hhh'}  # 假设要删除的记录的 ID 列表

# 发送 POST 请求
response = requests.post(url, json=data)

# 处理响应
if response.status_code == 200:
    print('删除成功:', response.json())
else:
    print('请求失败:', response.status_code, response.text)