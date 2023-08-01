import json
from flask import Flask, render_template, request, redirect, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:\\sqlite3\\asset.db'
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)


# 新建模型 用户、管理员、资产的ORM
class User(db.Model):  # 表名将会是 user（自动生成，小写）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))
    email = db.Column(db.String(60))
    password = db.Column(db.String(80))


class Admin(db.Model):  # 表名将会是 admin（自动生成，小写）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(60))
    password = db.Column(db.String(80))


class Asset(db.Model):
    AssetID = db.Column(db.String, primary_key=True)
    Type = db.Column(db.String)
    Status = db.Column(db.String)
    Cost = db.Column(db.Integer)
    Owner = db.Column(db.String)
    ProjectID = db.Column(db.String)
    Project = db.Column(db.String)
    Rack = db.Column(db.Integer)
    BarCode = db.Column(db.String)
    SN = db.Column(db.String)
    Model = db.Column(db.String)
    BMChostname = db.Column(db.String)
    IP = db.Column(db.String)
    ChangeTime = db.Column(db.Integer)
    Location = db.Column(db.String)
    ReleaseTime = db.Column(db.String)
    User = db.Column(db.String)
    AssetType = db.Column(db.String)
    Vendor = db.Column(db.String)
    Comments = db.Column(db.String)
    Quantity = db.Column(db.Integer)
    Bandwidth = db.Column(db.Integer)


# with app.app_context():
#     db.create_all()
#     db.session.commit()


def user_login(username, password):
    user = User.query.filter(and_(User.name == username, User.password == password)).first()
    if user:
        return True
    else:
        return False


def admin_login(email, password):
    administrator = Admin.query.filter(and_(Admin.email == email, Admin.password == password)).first()
    if administrator:
        return True
    else:
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('Email')
        password = request.form.get('Password')
        print('data from Server', email, password)
        # 访问数据库，查询验证数据
        with app.app_context():
            if admin_login(email, password):
                flash("管理员" + email + "登录成功")
                return redirect('/admin')
            elif user_login(email, password):
                flash("用户" + email + "登录成功")
                return redirect('/user')
            else:
                flash("用户名或密码错误")
    return render_template('auth-cover-login.html')


@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    return render_template('auth-cover-forgot-password.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth-cover-register.html')


# 登录成功，跳转到管理员页面
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    try:
        # 将所有列名存到列表里
        all_columns = [column.key for column in Asset.__table__.columns]
        # 查询"Asset"表的所有数据
        all_assets = Asset.query.all()
        # 将查询到的数据转换为列表的列表格式
        table_data = []
        for asset in all_assets:
            row_data = [getattr(asset, column) for column in all_columns]
            table_data.append(row_data)
    except Exception as e:
        # 处理可能发生的错误, 打印错误信息
        return jsonify({'error': str(e)}), 500
    return render_template('ecommerce-products.html', table_data=table_data, table_columns=all_columns)


# 登录成功，跳转到用户页面
@app.route('/user', methods=['GET', 'POST'])
def user():
    return render_template('user.html')


# 向数据库添加记录的方法
@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.json        # 获取json格式的数据
    new_asset = Asset()
    new_asset.AssetID = data.get('AssetID')
    new_asset.Type = data.get('Type')
    db.session.add(new_asset)
    db.session.commit()

    # 整合数据成json格式
    data = {'message': 'Records are added successfully'}
    return Response(json.dumps(data), status=200, mimetype='application/json')


# 根据条件筛选查询数据库记录
@app.route('/query_record', methods=['POST'])
def query_record():
    data = request.json
    type_ = data.get('Type', None)
    status_ = data.get('Status', None)
    owner_ = data.get('Owner', None)
    project_ = data.get('Project', None)
    sn_ = data.get('SN', None)
    barcode_ = data.get('BarCode', None)

# 复选条件，如果输入了该条件，将属性加入选择条件的列表
    conditions = []
    if type_:
        conditions.append(Asset.Type == type_)
    if status_:
        conditions.append(Asset.Status == status_)
    if owner_:
        conditions.append(Asset.Owner == status_)
    if project_:
        conditions.append(Asset.Project == project_)
    if sn_:
        conditions.append(Asset.SN == sn_)
    if barcode_:
        conditions.append(Asset.BarCode == barcode_)

    # 查询列表包含的条件
    records = Asset.query.filter(and_(*conditions)).all()
    asset_list = []
    for asset_ in records:
        record_data = {
            'AssetID': asset_.AssetID,
            'Type': asset_.Type,
            'Status': asset_.Status,
            'Cost': asset_.Cost,
            'Owner': asset_.Owner,
            'ProjectID': asset_.ProjectID,
            'Project': asset_.Project,
            'Rack':asset_.Rack,
            'BarCode': asset_.BarCode,
            'SN': asset_.SN,
            'Model': asset_.Model,
            'BMChostname': asset_.BMChostname,
            'IP': asset_.IP,
            'ChangeTime': asset_.ChangeTime,
            'Location': asset_.Location,
            'ReleaseTime': asset_.ReleaseTime,
            'User': asset_.User,
            'AssetType': asset_.AssetType,
            'Vendor': asset_.Vendor,
            'Comments': asset_.Comments,
            'Quantity': asset_.Quantity,
            'Bandwidth': asset_.Bandwidth,
            # 添加其他字段...
        }
        asset_list.append(record_data)
    return Response(jsonify(asset_list), status=200, mimetype='application/json')


# 根据选择删除数据库记录
# def del_record():



if __name__ == '__main__':
    app.run(debug=True)
