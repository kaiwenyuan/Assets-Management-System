import json
import datetime
from flask import Flask, render_template, request, redirect, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, event
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


# 登录成功，跳转到管理员页面
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    try:
        # 将所有列名存到列表里
        all_columns = [column.key for column in Asset.__table__.columns]
        # 如果前端传输了数据的筛选条件
        if request.method == 'POST':
            # 从表单中获取用户输入
            # search_query = request.form['search_query']
            # TODO 使用筛选条件查询数据库（按照特定列进行筛选，例如“asset_name”）
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
    data = request.json        # 获取json格式的数据
    # TODO: add other attributes
    new_asset = Asset()
    new_asset.AssetID = data.get('AssetID')
    new_asset.Type = data.get('Type', '')
    change_time = get_formated_time()
    new_asset.ChangeTime = change_time
    db.session.add(new_asset)
    db.session.commit()

    # TODO: add into log table
    print(log_str)

    # 整合数据成json格式
    data = {'message': 'Records are added successfully'}
    return Response(json.dumps(data), status=200, mimetype='application/json')

@app.route('/query_asset', methods=['POST'])
# 根据条件筛选查询数据库记录
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
    return Response(jsonify(asset_list), status=200, mimetype='application/json')


@app.route('/update_asset', methods=['POST'])
def update_record():
    try:
        data = request.json
        AssetID = data.get("AssetID")
        record = Asset.query.filter_by(AssetID=AssetID).first()
        # TODO: add more attributes
        comments = data.get("Comments", "")
        if comments:
            record.Comments = comments
        change_time = get_formated_time()
        record.ChangeTime = change_time
        db.session.commit()

        # TODO: add into log table
        userID = data.get('userID')
        print(log_str)

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
            print(log)

        return jsonify({'message': '记录已成功删除'})
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚事务
        return jsonify({'message': '删除失败：数据库错误'}), 500

    except Exception as e:
        return jsonify({'message': '删除失败：' + str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
