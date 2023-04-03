from flask import render_template,redirect,flash,session,request,url_for,jsonify
import os,random,string
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash,check_password_hash
from projects import app,db
from projects.models import Admin,Products,Categories,Measurements,Images,Users,Orders,Order_details,Payment


#for picture
def generate_name():
    filename = random.sample(string.ascii_lowercase,10)
    return ''.join(filename)


#login
@app.route('/admin/login/',methods=['POST','GET'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/adminlogin.html')
    else:
        data = request.form
        email = data.get('email')
        pwd = data.get('pwd')
        #query = Admin.query.filter(Admin.admin_email==email, Admin.admin_pwd==pwd).all()
        query = f"SELECT * FROM admin WHERE admin_email = '{email}' and admin_pwd = '{pwd}'"
        result= db.session.execute(text(query))
        total = result.fetchone()
        if total != None:
            session['loggedin'] = email
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials",category='error')
            return redirect(url_for('admin_login'))

    
#dashboard
@app.route('/admin/dashboard/')
def dashboard():
    if session.get('loggedin') != None:
        allorder = Orders.query.all()
        customer = Users.query.order_by(Users.user_id.desc()).all()
        total = sum(x.order_amt for x in allorder)
        return render_template('admin/dashboard.html',allorder=allorder,customer=customer,total=total)
    else:
        return redirect('/admin/login/')

#logout
@app.route('/admin/logout/')
def admin_logout():
    if session.get("loggedin") != None:
        session.pop("loggedin",None)
    return redirect("/admin/login/")

#orders
@app.route('/admin/orders/')
def order_history():
    if session.get('loggedin') !=None:
        allorder = Orders.query.join(Payment).add_columns(Payment).filter(Orders.order_id==Payment.pay_orderid).all()
        pend_order = Orders.query.join(Payment).add_columns(Payment).filter(Orders.order_id==Payment.pay_orderid,Orders.order_status=='pending').all()
        process_order = Orders.query.join(Payment).add_columns(Payment).filter(Orders.order_id==Payment.pay_orderid,Orders.order_status=='processing').all()
        complete_order = Orders.query.join(Payment).add_columns(Payment).filter(Orders.order_id==Payment.pay_orderid,Orders.order_status=='completed').all()
        cancel_order = Orders.query.join(Payment).add_columns(Payment).filter(Orders.order_id==Payment.pay_orderid,Orders.order_status=='cancelled').all()
        return render_template('admin/orders.html',allorder=allorder,pend_order=pend_order,process_order=process_order,complete_order=complete_order,cancel_order=cancel_order)
    else:
        return redirect('/admin/login')
    

#orderdetailshistoryajax modal
@app.route('/admin/history/',methods=['POST','GET'])
def admin_history():
    #receive thr id from ajax
    orderid= request.args.get('order')
    data = Order_details.query.filter(Order_details.detail_orderid==orderid).all()
    details=[]
    for d in data:
        details.append({
            'name':d.myproduct.product_name,
            'price':d.detail_price,
            'qty':d.detail_quantity,
            'refno':d.myorder.order_refno
        })
       
    return jsonify(details)
 


# order details
@app.route('/admin/order/details/<id>',methods=(['POST','GET']))
def order_details(id):
    if session.get('loggedin') !=None:
        thedetails = Order_details.query.filter(Order_details.detail_orderid==id).all()
        order_deets = Orders.query.get(id)
        return render_template('admin/order_details.html', thedetails=thedetails,order_deets=order_deets)
    else:
       return redirect('/admin/login')  

#edit order
@app.route('/admin/order/edit/<id>',methods=(['POST','GET']))
def edit_order(id):
    if session.get('loggedin') !=None:
        if request.method == 'GET':
            theorder = Orders.query.get(id)
            return render_template('admin/edit_order.html', theorder=theorder)
        else:
            #retrieve from database
            orederid = request.form.get('orderid')
            status = request.form.get('status')
            myorder = Orders.query.get(orederid)
            myorder.order_status = status
            db.session.commit()
            return redirect('/admin/orders/')
    else:
       return redirect('/admin/login') 
    
#customer
@app.route('/admin/users/')
def customer():
    if session.get('loggedin') !=None:
        customers = Users.query.all()
        return render_template('admin/customer.html',customers=customers)
    else:
       return redirect('/admin/login') 

#product
@app.route('/admin/products/')
def admin_product():
    if session.get('loggedin') !=None:
        query = Products.query.all()
        return render_template('admin/products.html',query=query)
    else:
        return redirect('/admin/login')


#add product 
@app.route('/admin/product/add',methods=['POST','GET'])
def add_product():
    if session.get('loggedin') ==  None:
        return redirect('/admin/login')
    else:
        if request.method  == 'GET':
            deets = Categories.query.all()
            return render_template('admin/addproduct.html',deets=deets)
        else:
            #retrieve from the form
            data = request.form
            pname = data.get('name')
            price = data.get('price')
            cat = data.get('cat')
            images = request.files.getlist('img')
            
            if pname!='' and price !='' and cat !='':
                query1 = Products(product_name=pname,product_price=price,product_categoryid=cat)
                db.session.add(query1)
                db.session.commit()
                allowed = [".jpg",".jpeg",".png"]
                for x in images:
                    picture = x.filename
                    if picture !="":
                        name,ext = os.path.splitext(picture)
                        if ext in allowed:
                            newname = generate_name()+ext
                            x.save('projects/static/uploads/'+newname)
                            deets = Images(image_name=newname,image_productid=query1.product_id)
                            db.session.add(deets)
                            db.session.commit()   
                        else:
                            flash(" Image extension not allowed")
                            return redirect(url_for('add_product'))
                    else:
                        flash(" all images must be uploaded")
                        return redirect(url_for('add_product'))
                flash(" Product added successfully",category='success')
                return redirect(url_for('admin_product'))
            else:
                flash(" all felds are quired")
                return  redirect(url_for('add_product'))
                    

    
#deleteproduct
@app.route('/admin/product/delete/<id>')
def delete_product(id):
    prod = Products.query.get_or_404(id)
    img = Images.query.filter(Images.image_productid==id).all()
    db.session.delete(prod)
    db.session.commit()
    flash("successfully deleted",category='error')
    return redirect(url_for('admin_product'))
    

#category
@app.route('/admin/category/')
def admin_category():
    if session.get('loggedin') !=None:
        data = Categories.query.all()
        return render_template('admin/category.html',data=data)
    else:
        return redirect('/admin/login')

#addcategory
@app.route('/admin/category/add',methods=['POST','GET'])
def add_category():
    if session.get('loggedin') ==  None:
        return redirect('/admin/login')
    else:
        if request.method  == 'GET':
            return render_template('admin/addcategory.html')
        else:
            #retrieve from form
            data = request.form
            cat = data.get('cat')
            data = Categories.query.filter(Categories.category_name==cat).first()
            if data:
                flash("category already exist",category="error")
                return redirect(url_for('add_category'))
            else:
                query = Categories(category_name = cat)
                db.session.add(query)
                db.session.commit()
                flash("New category added",category="success")
                return redirect(url_for('admin_category'))
    
#deleteproduct
@app.route('/admin/category/delete/<id>')
def delete_category(id):
    cat = Categories.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash("successfully deleted",category='error')
    return redirect(url_for('admin_category'))

#measurement
@app.route('/admin/measurements/')
def admin_measurement():
    if session.get('loggedin') !=None:
        data = Measurements.query.all()
        return render_template('admin/measurement.html',data=data)
    else:
        return redirect('/admin/login')
    
#delete measurement
@app.route('/admin/measurement/delete/<id>')
def delete_measurement(id):
    mes = Measurements.query.get_or_404(id)
    db.session.delete(mes)
    db.session.commit()
    flash("successfully deleted",category='error')
    return redirect(url_for('admin_measurement'))

#test
@app.route('/admin/test')
def admin_test():
    return render_template('admin/admin_test.html')

@app.route('/my_list', methods=['POST','GET'])
def my_list():
    user = request.args.get('prop')
    measure_deets = Measurements.query.filter(Measurements.measure_userid==user).first()
    data2send = "<table class='table table-bordered'>"
    data2send = data2send + '<thead><tr><th colspan="2">' + measure_deets.the_user.user_fname +' ' + measure_deets.the_user.user_lname + '</th></tr></thead>'
    data2send = data2send + '<tbody><tr><th>Bust</th><td>'+ str(measure_deets.bust)+'</td></tr><tr><th>Off shoulder(des) </th><td>'+str(measure_deets.off_shoulderdim)+'</td></tr><tr><th>shoulder-underbust</th><td>'+str(measure_deets.shoulder_underbust)+'</td></tr><tr><th>Underbust circumference</th><td>'+str(measure_deets.underbust_circum)+'</td></tr><tr><th>Shoulder-nipple</th><td>'+str(measure_deets.shoulder_nipple)+'</td></tr><tr><th>Nipple-nipple</th><td>'+str(measure_deets.nipple_nipple)+'</td></tr><tr><th>Back</th><td>'+str(measure_deets.back)+'</td></tr><tr><th>Top-length</th><td>'+str(measure_deets.top_length)+'</td></tr><tr><th>Top-halflength</th><td>'+str(measure_deets.top_halflength)+'</td></tr><tr><th>Top-waist</th><td>'+str(measure_deets.top_waist)+'</td></tr><tr><th>Sleeve-length</th><td>'+str(measure_deets.sleeve_length)+'</td></tr><tr><th>Sleeve-hole</th><td>'+str(measure_deets.sleeve_hole)+'</td></tr><tr><th>Hips</th><td>'+str(measure_deets.hips)+'</td></tr><tr><th>Skirt-length</th><td>'+str(measure_deets.skirt_length)+'</td></tr><tr><th>Skirt-waist</th><td>'+str(measure_deets.skirt_waist)+'</td></tr><tr><th>Trouser-length</th><td>'+str(measure_deets.trouser_length)+'</td></tr><tr><th>Dress-length</th><td>'+str(measure_deets.dress_length)+'</td></tr>'
    data2send = data2send + '</tbody></table>'
    return data2send
    

#error pages
@app.errorhandler(404)
def error404(error):
    return render_template('admin/error404.html',error=error),404

@app.errorhandler(500)
def error500(error):
    return render_template('admin/error500.html',error=error),500

