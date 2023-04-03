from datetime import datetime
from projects import db


#tables
class Admin(db.Model):
    admin_id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    admin_email = db.Column(db.String(120), nullable=False)
    admin_pwd = db.Column(db.String(120), nullable=False)


class Users(db.Model):
    user_id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    user_fname = db.Column(db.String(50), nullable=False)
    user_lname = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_password = db.Column(db.String(120),nullable=False)
    user_phone = db.Column(db.String(25),nullable=True)
    user_pix = db.Column(db.String(120),nullable=True)
    user_datereg =db.Column(db.DateTime(),default=datetime.utcnow)
    
    #relationship
    myorders = db.relationship('Orders', back_populates='user_deets')
    mymeasurements = db.relationship('Measurements', back_populates ='the_user')
    mycart= db.relationship('Cart', back_populates ='myuser')

class Measurements(db.Model):
    measure_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    #foreign key
    measure_userid = db.Column(db.Integer,db.ForeignKey('users.user_id'))
    bust = db.Column(db.Float(),nullable=True)
    off_shoulderdim = db.Column(db.Float(),nullable=True)
    shoulder_underbust = db.Column(db.Float(),nullable=True)
    underbust_circum = db.Column(db.Float(),nullable=True)
    shoulder_nipple = db.Column(db.Float(),nullable=True)
    nipple_nipple = db.Column(db.Float(),nullable=True)
    back = db.Column(db.Float(),nullable=True)
    top_length = db.Column(db.Float(),nullable=True)
    top_halflength = db.Column(db.Float(),nullable=True)
    top_waist = db.Column(db.Float(),nullable=True)
    sleeve_length = db.Column(db.Float(),nullable=True)
    sleeve_hole = db.Column(db.Float(),nullable=True)
    hips = db.Column(db.Float(),nullable=True)
    skirt_length = db.Column(db.Float(),nullable=True)
    skirt_waist = db.Column(db.Float(),nullable=True)
    trouser_length = db.Column(db.Float(),nullable=True)
    dress_length = db.Column(db.Float(),nullable=True)
    #relationship
    the_user = db.relationship('Users', back_populates='mymeasurements')

class Products(db.Model):
    product_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    product_name = db.Column(db.String(120), nullable=False)
    product_price = db.Column(db.Float(),nullable=False)
    #foreign key
    product_categoryid = db.Column(db.Integer, db.ForeignKey('categories.category_id'))

    #relationship
    mydetails= db.relationship('Order_details', back_populates='myproduct')
    the_image = db.relationship('Images', back_populates='product_deets',cascade="all, delete-orphan")
    mycategory = db.relationship('Categories', back_populates='the_product')
    cart_info = db.relationship("Cart", back_populates="the_product")

class Categories(db.Model):
    category_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    category_name = db.Column(db.String(120), nullable=False, unique =True)

    #relationship
    the_product = db.relationship('Products', back_populates='mycategory')

class Images(db.Model):
    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    image_name = db.Column(db.String(120), nullable=False)
    #foreign key
    image_productid = db.Column(db.Integer, db.ForeignKey('products.product_id'))

    #relationship
    product_deets = db.relationship('Products', back_populates='the_image')
    

class Orders(db.Model):
    order_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
     #foreign key
    order_userid = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    order_name = db.Column(db.String(120), nullable=True)
    order_email = db.Column(db.String(120), nullable=True)
    order_phone = db.Column(db.String(120), nullable=False)
    order_shipaddress = db.Column(db.String(255), nullable=False)
    order_shipcity = db.Column(db.String(120), nullable=False)
        #foreign key
    order_stateid = db.Column(db.Integer, db.ForeignKey('states.state_id'))
    order_amt = db.Column(db.Float(), nullable=False)
    order_status = db.Column(db.Enum('pending','not processed','processing','cancelled','completed'),nullable=False, server_default=('pending'))
    order_refno = db.Column(db.String(100),nullable=True)
    order_date = db.Column(db.DateTime(),default=datetime.utcnow)
    #relationship
    state_deets = db.relationship('States', back_populates='order_deets')
    details_deets = db.relationship('Order_details', back_populates='myorder')
    user_deets = db.relationship('Users', back_populates='myorders')

class Order_details(db.Model):
    detail_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    #foreign key
    detail_productid = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    detail_orderid = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    detail_price = db.Column(db.Float(), nullable=False)
    detail_quantity = db.Column(db.Integer(), nullable=True)
    #relationship
    myorder = db.relationship('Orders', back_populates='details_deets')
    myproduct = db.relationship('Products', back_populates='mydetails')

class States(db.Model):
    state_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    state_name = db.Column(db.String(120), nullable=False)

    #relationship
    order_deets = db.relationship('Orders', back_populates='state_deets')


class Cart(db.Model):
    cart_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    cart_qty = db.Column(db.Integer,nullable=False)
    cart_price = db.Column(db.Float(),nullable=False)
    cart_total = db.Column(db.Float(),nullable=False)
    cart_pix = db.Column(db.String(120), nullable=False)
    cart_date = db.Column(db.DateTime(),default=datetime.utcnow)
    cart_productid = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    cart_userid= db.Column(db.Integer, db.ForeignKey('users.user_id'))
    #relationship
    the_product = db.relationship("Products", back_populates="cart_info")
    myuser = db.relationship("Users", back_populates="mycart")

class Payment(db.Model):
    pay_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    pay_orderid=db.Column(db.Integer,db.ForeignKey("orders.order_id"),nullable=True)
    pay_amount=db.Column(db.Float) 
    pay_date=db.Column(db.DateTime(), default=datetime.utcnow)
    pay_status=db.Column(db.Enum('pending','failed','paid'),nullable=False, server_default=("pending"))  
    pay_ref=db.Column(db.String(100),nullable=True)
    #relationship
    order_deets = db.relationship('Orders',backref='paydeets')


    