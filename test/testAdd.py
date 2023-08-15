import requests
# 定义API端点和请求数据
api_url = 'http://127.0.0.1:5000/add_record'

data = {
    'AssetID': 'Test001',
    'Type': 'TEST',
    'Status': 'Avaliable'
}

response = requests.post(api_url, json=data)
if response.status_code == 200:
    # 提取并处理响应数据
    print(response)
    result = response.json()
    # 在这里处理解析后的数据
    for item in result:
        # 处理每个JSON对象
        print(item)
else:
    print('Add record failed')
