import json
import datetime
from flask import Flask, render_template, request, redirect, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, DateTime, event, func
from sqlalchemy.exc import SQLAlchemyError


# TODO: PostgreSQL in Server
# TODO: 整理代码，统一接口

def get_formated_time():
    current_time = datetime.datetime.now()
    return current_time.strftime('%Y-%m-%d %H:%M:%S')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:\\sqlite3\\asset.db'
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)

log_str = ""


# 新建模型 用户、管理员、资产的ORM
class User(db.Model):  # 表名将会是 user（自动生成，小写）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))
    email = db.Column(db.String(60))
    password = db.Column(db.String(80))


class Admin(db.Model):  # table admin
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(60))
    password = db.Column(db.String(80))


class Asset(db.Model):  # table asset
    AssetID = db.Column(db.String, primary_key=True)
    AssetType = db.Column(db.String)
    Type = db.Column(db.String)
    Status = db.Column(db.String)
    Cost = db.Column(db.Integer)
    Owner = db.Column(db.String)
    ProjectID = db.Column(db.String)
    Project = db.Column(db.String)
    Rack = db.Column(db.String)
    BarCode = db.Column(db.String)
    SN = db.Column(db.String)
    Model = db.Column(db.String)
    BMChostname = db.Column(db.String)
    IP = db.Column(db.String)
    Location = db.Column(db.String)
    User = db.Column(db.String)
    Vendor = db.Column(db.String)
    Comments = db.Column(db.String)
    Quantity = db.Column(db.Integer)
    Bandwidth = db.Column(db.Integer)
    ChangeTime = db.Column(db.String)
    ReleaseTime = db.Column(db.String)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True )
    log = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=func.now())


def user_login(username, password):
    current_user = User.query.filter(and_(User.name == username, User.password == password)).first()
    if current_user:
        return True
    else:
        return False


def admin_login(email, password):
    administrator = Admin.query.filter(and_(Admin.email == email, Admin.password == password)).first()
    if administrator:
        return True
    else:
        return False

# 添加listener,对增删改查的操作监听并写入log表
@event.listens_for(db.session, 'before_flush')
def log_changes(session, flush_context, instances):
    global log_str
    log_str = ""
    for obj in session.new:
        if isinstance(obj, Asset):
            log_str = f"Add asset_id: {obj.AssetID}"
    for obj in session.deleted:
        if isinstance(obj, Asset):
            if log_str:
                log_str = f"Deleted asset_id: {obj.AssetID}"
            else:
                log_str += f",Deleted asset_id: {obj.AssetID}"
    for obj in session.dirty:
        if isinstance(obj, Asset):
            log_str = f"Update asset_id: {obj.AssetID}"
        for attr in db.inspect(obj).attrs:
            if attr.history.has_changes():
                log_str += f" change {attr.key} from {attr.history.deleted[0]} to {attr.value}"


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


# TODO 忘记密码，修改用户密码
@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    return render_template('auth-cover-forgot-password.html')


# 添加新用户
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['Username']
        email = request.form['Email']
        password = request.form['Password']
        # 判断用户是否已经存在
        existing_user = Admin.query.filter_by(email=email).first()
        if existing_user:
            response = {
                "status": "failed",
                "message": "User with this email already exists. Please choose a different email."
            }
            return jsonify(response)
        # 创建向数据库添加的新用户信息
        new_user = Admin()
        new_user.email = email
        new_user.name = username
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        response = {
            "status": "success",
            "message": "Registration successful!"
        }
        return jsonify(response)
    return render_template('auth-cover-register.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    try:
        # 将所有列名存到列表里
        all_columns = [column.key for column in Asset.__table__.columns]
        # 如果前端传输了数据筛选条件
        if request.method == 'POST':
            # 从表单中获取用户输入的筛选条件
            # search_query = request.form['search_query']
            # TODO 逻辑问题
            # filtered_assets = Asset.query.filter(Asset.asset_name.like(f"%{search_query}%")).all()
            all_assets = query_record()
        else:
            # 如果是GET请求或未提供输入，则获取所有资产信息
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


# TODO: try-except
@app.route('/add_record', methods=['POST'])
def add_record():
    try:
        data = request.json        # 从request中获取数据
        new_asset = Asset()
        new_asset.AssetID = data.get('AssetID')
        new_asset.BarCode = data.get('BarCode', '')
        new_asset.Bandwidth = data.get('Bandwidth', 0)
        new_asset.BMChostname = data.get('BMChostname', '')
        new_asset.Cost = data.get('Cost', 0)
        new_asset.Comments = data.get('Comments', '')
        new_asset.IP = data.get('IP', '')
        new_asset.Owner = data.get('Owner', '(admin)')
        new_asset.Project = data.get('Project', '')
        new_asset.SN = data.get('SN', '')
        new_asset.Type = data.get('Type', '')
        new_asset.User = data.get('User', '')
        new_asset.AssetType = data.get('AssetType', '')
        new_asset.Status = data.get('Status', '')
        new_asset.Location = data.get('Location', '')
        new_asset.Model = data.get('Model', '')
        new_asset.Rack = data.get('Rack', '')
        new_asset.Quantity = data.get('Quantity', 0)
        new_asset.Vendor = data.get('Vendor', '')
        new_asset.ReleaseTime = data.get('ReleaseTime', '')
        new_asset.ProjectID = data.get('ProjectID', '')
        change_time = get_formated_time()
        new_asset.ChangeTime = change_time
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
    type_ = data.get('Type', '')
    status_ = data.get('Status', '')
    owner_ = data.get('Owner', '')
    project_ = data.get('Project', '')
    sn_ = data.get('SN', '')
    barcode_ = data.get('BarCode', '')

# 复选条件，如果输入了该条件，将属性加入选择条件的列表
    conditions = []
    if type_:
        conditions.append(Asset.Type == type_)
    if status_:
        conditions.append(Asset.Status == status_)
    if owner_:
        conditions.append(Asset.Owner == owner_)
    if project_:
        conditions.append(Asset.Project == project_)
    if sn_:
        conditions.append(Asset.SN == sn_)
    if barcode_:
        conditions.append(Asset.BarCode == barcode_)

    # 查询列表包含的条件的记录
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
            'Rack': asset_.Rack,
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
        records = Asset.query.filter(Asset.AssetID.in_(assetid_list)).all()
        for record in records:
            db.session.delete(record)
        db.session.commit()

        # TODO: add into log table
        userID = data.get('userID')
        change_time = get_formated_time()
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


if __name__ == '__main__':
    app.run(debug=True)
