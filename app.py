import json, psycopg2
import datetime
from flask import Flask, render_template, request, redirect, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, DateTime, event, func
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote_plus


# TODO: 整理代码，统一接口
def get_formated_time():
    current_time = datetime.datetime.now()
    return current_time.strftime('%Y-%m-%d %H:%M:%S')


app = Flask(__name__)

# 要连接的数据库信息
username = 'admin_ww'
password = 'Password@123.'
host = '10.67.124.22'
port = '5432'
database_name = 'ams'

# 对密码进行 URL 编码
encoded_password = quote_plus(password)

# 配置 SQLAlchemy 连接数据库的 URL
connection_uri = f'postgresql://{username}:{encoded_password}@{host}:{port}/{database_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = connection_uri

# 添加 SECRET_KEY
app.config['SECRET_KEY'] = '%$#$GReu#!RAvdoO23RmDFdSC'
db = SQLAlchemy(app)

#全局变量 生成log
log_str = ""

class User(db.Model):  # table user
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))


class Asset(db.Model):  # table asset
    assetid = db.Column(db.String, primary_key=True)
    assettype = db.Column(db.String)
    barcode = db.Column(db.String)
    bandwidth = db.Column(db.Integer)
    bmchostname = db.Column(db.String)
    cost = db.Column(db.Integer)
    comments = db.Column(db.String)
    ip = db.Column(db.String)
    type = db.Column(db.String)
    location = db.Column(db.String)
    model = db.Column(db.String)
    owner = db.Column(db.String)
    projectid = db.Column(db.String)
    project = db.Column(db.String)
    rack = db.Column(db.String)
    sn = db.Column(db.String)
    status = db.Column(db.String)
    user = db.Column(db.String)
    vendor = db.Column(db.String)
    quantity = db.Column(db.Integer)
    changetime = db.Column(db.DateTime)
    releasetime = db.Column(db.DateTime)
    serverid = db.Column(db.String)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True )
    log = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=func.now())


def user_login(email, password):
    current_user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if current_user:
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
            if user_login(email, password):
                flash("用户" + email + "登录成功")
                return redirect('/user')
            else:
                flash("用户名或密码错误")
    return render_template('auth-cover-login.html')


# 添加新用户
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['Username']
        email = request.form['Email']
        password = request.form['Password']
        # 判断用户是否已经存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            response = {
                "status": "failed",
                "message": "User with this email already exists. Please choose a different email."
            }
            return jsonify(response)
        # 创建向数据库添加的新用户信息
        new_user = User()
        new_user.email = email
        new_user.username = username
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        response = {
            "status": "success",
            "message": "Registration successful!"
        }
        return jsonify(response)
    return render_template('auth-cover-register.html')


# 用户首页展示
@app.route('/user', methods=['GET', 'POST'])
def user_profile():
    try:
        # 将所有列名存到列表里
        all_columns = [column.key for column in Asset.__table__.columns]
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


@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        user_email = request.form['Email']
        new_password = request.form['Password']
        # existing user
        exist_user = User.query.filter_by(email=user_email).first()
        if exist_user:
            exist_user.password = new_password
        else:
            response = {
                "status": "failed",
                "message": "User with this email doesn't exist, please check your email or sign up a new one."
            }
            return jsonify(response)
    return render_template('auth-cover-forgot-password.html')

# 增加新的资产记录
@app.route('/add_record', methods=['POST'])
def add_record():
    try:
        data = request.json        # 从request中获取数据
        new_asset = Asset()
        new_asset.assetid = data.get('AssetID')
        new_asset.barcode = data.get('BarCode', '')
        new_asset.bandwidth = data.get('Bandwidth', 0)
        new_asset.bmchostname = data.get('BMChostname', '')
        new_asset.cost = data.get('Cost', 0)
        new_asset.comments = data.get('Comments', '')
        new_asset.ip = data.get('IP', '')
        new_asset.owner= data.get('Owner', '(admin)')
        new_asset.project = data.get('Project', '')
        new_asset.sn = data.get('SN', '')
        new_asset.type = data.get('Type', '')
        new_asset.user = data.get('User', '')
        new_asset.assettype = data.get('AssetType', '')
        new_asset.status = data.get('Status', '')
        new_asset.location = data.get('Location', '')
        new_asset.model = data.get('Model', '')
        new_asset.rack = data.get('Rack', '')
        new_asset.quantity = data.get('Quantity', 0)
        new_asset.vendor = data.get('Vendor', '')
        new_asset.releasetime = data.get('ReleaseTime', '')
        new_asset.projectid = data.get('ProjectID', '')
        new_asset.serverid = data.get('ServerID', '')
        db.session.add(new_asset)
        db.session.commit()
        new_log = Log()
        new_log.log = log_str
        db.session.add(new_log)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': '更新失败：' + str(e)}), 500
    data = {'message': 'Records are added successfully'}
    return Response(json.dumps(data), status=200, mimetype='application/json')


@app.route('/query_asset', methods=['POST', 'GET'])
def query_record():
    data = request.json
    assetid_ = data.get('AssetID', '')
    type_ = data.get('Type', '')
    status_ = data.get('Status', '')
    owner_ = data.get('Owner', '')
    project_ = data.get('Project', '')
    sn_ = data.get('SN', '')
    barcode_ = data.get('BarCode', '')

# 复选条件，如果输入了该条件，将属性加入选择条件的列表
    conditions = []
    if assetid_:
        conditions.append(Asset.assetid == assetid_)
    if type_:
        conditions.append(Asset.type == type_)
    if status_:
        conditions.append(Asset.status == status_)
    if owner_:
        conditions.append(Asset.owner == owner_)
    if project_:
        conditions.append(Asset.project == project_)
    if sn_:
        conditions.append(Asset.sn == sn_)
    if barcode_:
        conditions.append(Asset.barcode == barcode_)

    # 查询列表包含的条件的记录
    records = Asset.query.filter(and_(*conditions)).all()
    asset_list = []
    for asset_ in records:
        record_data = {
            'AssetID': asset_.assetid,
            'Type': asset_.type,
            'Status': asset_.status,
            'Cost': asset_.cost,
            'Owner': asset_.owner,
            'ProjectID': asset_.projectid,
            'Project': asset_.project,
            'Rack': asset_.rack,
            'BarCode': asset_.barcode,
            'SN': asset_.sn,
            'Model': asset_.model,
            'BMChostname': asset_.bmchostname,
            'IP': asset_.ip,
            'ChangeTime': asset_.changetime,
            'Location': asset_.location,
            'ReleaseTime': asset_.releasetime,
            'User': asset_.user,
            'AssetType': asset_.assettype,
            'Vendor': asset_.vendor,
            'Comments': asset_.comments,
            'Quantity': asset_.quantity,
            'Bandwidth': asset_.bandwidth,
            'ServerID':asset_.serverid,
            # 添加其他字段...
        }
        asset_list.append(record_data)
    return jsonify(asset_list)

@app.route('/update_asset', methods=['POST'])
def update_record():
    try:
        data = request.json
        AssetID = data.get("AssetID")
        record = Asset.query.filter_by(AssetID=AssetID).first()
        attributes = {
            'Comments': '',
            'BarCode': '',
            'Bandwidth': 0,
            'BMChostname': '',
            'Cost': 0,
            'IP': '',
            'Owner': '(admin)',
            'Project': '',
            'SN': '',
            'Type': '',
            'User': '',
            'AssetType': '',
            'Status': '',
            'Location': '',
            'Model': '',
            'Rack': '',
            'Quantity': 0,
            'Vendor': '',
            'ProjectID': '',
            'ReleaseTime': ''
        }

        change_time = get_formated_time()
        record.ChangeTime = change_time

        for attr, default_value in attributes.items():
            new_value = data.get(attr, default_value)
            setattr(record, attr, new_value)
        db.session.commit()
        # add into log table
        new_log = Log()
        new_log.log = log_str
        db.session.add(new_log)
        db.session.commit()
        return jsonify({'message': '记录已成功更新'})
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚事务
        return jsonify({'message': '更新失败：数据库错误'}), 500

    except Exception as e:
        return jsonify({'message': '更新失败：' + str(e)}), 500


@app.route('/delete_asset', methods=['POST'])
def delete_record():
    try:
        data = request.json
        assetid_list = data.get('assetid_list', [])
        if not assetid_list:
            return jsonify({'message': '删除失败，未选中信息'}), 400
        records = Asset.query.filter(Asset.assetid.in_(assetid_list)).all()
        for record in records:
            db.session.delete(record)
        db.session.commit()

        # TODO: add into log table
        log_list = log_str.split(',')
        for log in log_list:
            new_log = Log()
            new_log.log = log
            db.session.add(new_log)
            db.session.commit()

        return jsonify({'message': '记录已成功删除'})
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚事务
        return jsonify({'message': '删除失败：数据库错误'}), 500

    except Exception as e:
        return jsonify({'message': '删除失败：' + str(e)}), 500


# 添加listener,对增删改查的操作监听并写入log表
@event.listens_for(db.session, 'before_flush')
def log_changes(session, flush_context, instances):
    global log_str
    log_str = ""
    for obj in session.new:
        if isinstance(obj, Asset):
            log_str = f"Add asset_id: {obj.assetid}"
    for obj in session.deleted:
        if isinstance(obj, Asset):
            if log_str:
                log_str = f"Deleted asset_id: {obj.assetid}"
            else:
                log_str += f",Deleted asset_id: {obj.assetid}"
    for obj in session.dirty:
        if isinstance(obj, Asset):
            log_str = f"Update asset_id: {obj.assetid}"
        for attr in db.inspect(obj).attrs:
            if attr.history.has_changes():
                log_str += f" change {attr.key} from {attr.history.deleted[0]} to {attr.value}"


if __name__ == '__main__':
    app.run(debug=True)
