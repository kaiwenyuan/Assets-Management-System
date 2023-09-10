import requests
# 定义API端点和请求数据
api_url = 'http://127.0.0.1:5000/delete_asset'
data = {
    'assetid_list': ['test003', 'test004']
}
response = requests.post(api_url, json=data)
if response.status_code == 200:
    # 提取并处理响应数据
    result = response.json()
    print(result)
else:
    print('sorry, delete failed...')