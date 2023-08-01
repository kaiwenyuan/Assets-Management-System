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

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn
def get_table_columns(table_name):
    conn = get_db()
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    conn.close()
    return columns # 获取所有表单数据
    def get_table_data():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM assets')
    data = cursor.fetchall()
    conn.close()
    return data


@app.route('/')
def index():
    table_data = get_table_data()
    table_columns = get_table_columns('my_table')
    return render_template('ecommerce-products.html', table_data=table_data, table_columns=table_columns)

    if __name__ == '__main__':    app.run()
