from flask import render_template,redirect,flash,session,request,url_for,jsonify
import os,random,string,json,requests,re
from werkzeug.security import generate_password_hash,check_password_hash
#to #initialize the app to load __iniit__
from projects import app,db
#import from local file
from projects.models import Users,Orders,Images,Products,Measurements,Categories,Cart,States,Order_details,Payment

#for profilepicture
def generate_name():
    filename = random.sample(string.ascii_lowercase,10)
    return ''.join(filename)



#signuppage
@app.route('/user/signup/',methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('user/signup.html')
    else:
        #retrieve data from the form
        data = request.form
        fname = data.get('fname')
        lname = data.get('sname')
        email = data.get('email')
        pwd = data.get('pwd')
        cpwd = data.get('cpwd')
        phone = data.get('phone')
        if fname!="" and lname !="" and email != "" and pwd != "" and cpwd !="" and phone !="" :
            if pwd == cpwd:
                if (len(pwd)>=5) and re.search("[a-z]",pwd) and re.search("[A-Z]",pwd) and re.search("[0-9]",pwd) and re.search("[_,@,#,$]",pwd):
                    hashed_pwd = generate_password_hash(pwd)
                    #storing into database
                    query = Users(user_fname=fname,user_lname=lname,user_email=email,user_password=hashed_pwd,user_phone=phone)
                    db.session.add(query)
                    db.session.commit()
                    return redirect(url_for('login'))
                else:
                    flash("Your password must contain Upper Case,lower case,number and any of the listed special charater(_,@,#,$) and should be more that 5")
                    return redirect(url_for('signup'))
            else:
                flash("Password doesnt match with confirm password",category="error")
                return redirect(url_for('signup'))
        else:
            flash("You must complete all the fields to signup",category="error")
            return redirect(url_for('signup'))


#loginpage
@app.route('/user/login/',methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('user/login.html')
    else:
        #retrieve from the form
        data = request.form
        email = data.get('email')
        pwd = data.get('pwd')
            #check if the email exist
        query = Users.query.filter(Users.user_email == email).first()
        if query != None:
            pwd_indb = query.user_password
                #compare password in the database and the submitted one
            chk = check_password_hash(pwd_indb,pwd)
            if chk:
                #create session
                id = query.user_id
                session['user'] = id
                return redirect(url_for('home'))
            else:
                flash("Invalid Credentials",category='error')
                return redirect(url_for('login'))
        else:
            flash("Invalid Credentials",category='error')
            return redirect(url_for('login'))
        
#logout
@app.route('/user/logout')
def logout():
    if session.get('user') != None:
        session.pop('user',None)
        return redirect(url_for('home'))

#forget password
@app.route('/user/forget_password/',methods=['POST','GET'])
def forget():
    if request.method == 'GET':
        return render_template('user/forget_pwd.html')
    else:
        #retrieve data from form
        email = request.form.get('email')
        newpass = request.form.get('newpassword')
        renewpass = request.form.get('renewpassword')
            #check if the email exist
        query = Users.query.filter(Users.user_email == email).first()
        if email !="" and newpass !="" and renewpass !="":
            if query != None:
                if newpass == renewpass:
                    if (len(newpass)>=5) and re.search("[a-z]",newpass) and re.search("[A-Z]",newpass) and re.search("[0-9]",newpass) and re.search("[_,@,#,$]",newpass):
                        '''Convert the plain password to hashed value and insert into db'''
                        hashed_pwd = generate_password_hash(newpass)
                        query.user_password = hashed_pwd
                        db.session.commit()
                        return redirect('/user/login/')
                    else:
                        flash("Your password must contain Upper Case,lower case,number and any of the listed special charater(_,@,#,$) and should be more that 5")
                        return redirect('/user/forget_password/')
                else:
                    flash('Password does not match')
                    return redirect('/user/forget_password/')

            else:
                flash("Invalid Email",category='error')
                return redirect('/user/forget_password/')
        else:
            flash("All fields must be filled",category="error")
            return redirect('/user/forget_password/')


#homepage  
@app.route('/')
@app.route('/myapparel/home/')
def home():
    id = session.get('user')
    if id != None:
        deets = Users.query.get(id)
        mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
        return render_template('user/index.html',deets=deets,mycart=mycart)
    else:
        return render_template('user/index.html')

#gallery
@app.route('/myapparel/gallery/')
def gallery():
    id = session.get('user')
    if id != None:
        deets = Users.query.get(id)
        mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
        return render_template('user/gallery.html',deets=deets,mycart=mycart)
    else:
        return render_template('user/gallery.html')

#shop       
@app.route('/myapparel/shop/')
def shop():
    if session.get('user') != None:
        mycart = Cart.query.filter(Cart.cart_userid==session.get('user')).all()
        deets = Users.query.get(session.get('user'))
        caty = Categories.query.all()
        prop = Products.query.all()
        product_deets = []
        for x in prop:
            img=db.session.query(Images.image_name,Images.image_productid).filter(Images.image_productid==x.product_id).first()
            product_deets.append(img)
        return render_template('user/shop.html',caty=caty,prop=prop,product_deets=product_deets,mycart=mycart,deets=deets)
    else:
        return redirect(url_for('login'))

#ajaximage modal pic on shop
@app.route('/image',methods=['POST','GET'])
def pic():
    product_id = request.args.get('prop')
    img = img=db.session.query(Images.image_name,Images.image_productid).filter(Images.image_productid==product_id).all()
    pix = []
    for i in img:
        pix.append(i.image_name)
    data2send = "<div class='row'>"
    for s in pix:
        a = url_for('static',filename='/uploads/'+ s)
        data2send = data2send + "<div class='col-lg-3 mb-3'>" + f"<img src='{a}' class='d-block w-100 img-thumbnail' alt='pic' style='height: 200px;width: 200px;'>" + "</div>"
    data2send = data2send + "</div>"
    return data2send


#newprofile
@app.route('/user/profile/',methods=['POST','GET'])
def profile():
    id = session.get('user')
    if id == None:
        return redirect(url_for('login')) 
    else:  
        if request.method == 'GET':
            deets = Users.query.get(session.get('user'))
            mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
            return render_template('user/profile.html',deets=deets,mycart=mycart)
        else:
            #retrieve data submitted
            data = request.form
            fname = data.get('fname')
            lname = data.get('lname')
            phone = data.get('phone')
            image = request.files['pic']
            if fname !="" and lname !=""and phone !="" and image !="":
                userobj = Users.query.get(id)
                userobj.user_fname = fname
                userobj.user_lname = lname
                userobj.user_phone = phone
                filename = image.filename
                allowed = ['.jpg','jpeg','.png']
                name,ext = os.path.splitext(filename)
                if ext.lower() in allowed:
                    picture = generate_name()+ ext
                    image.save("projects/static/uploads/"+picture)
                    userobj.user_pix = picture
                else:
                    flash("file extension not allowed",category="error")
                    return redirect('/user/profile/')
                db.session.commit()
                flash("profile updated",category="success")
                return redirect("/user/profile/")
            else:
                flash("All fields must be completed",category="error")
                return redirect("/user/profile/")     


#password change
@app.route('/password/reset/',methods=['POST','GET'])
def password():
    #retrieve from form
    oldpass = request.form.get('password')
    newpass = request.form.get('newpassword')
    renewpass = request.form.get('renewpassword')
    #query to fetch the user info
    user = Users.query.get(session.get('user'))
    pwd_indb = user.user_password
    if oldpass !="" and newpass !="" and renewpass !="":
        #compare the password coming from the form with the hasded password in the db
        chk = check_password_hash(pwd_indb,oldpass)
        if chk:
            if newpass == renewpass:
                if (len(newpass)>=5) and re.search("[a-z]",newpass) and re.search("[A-Z]",newpass) and re.search("[0-9]",newpass) and re.search("[_,@,#,$]",newpass):
                    '''Convert the plain password to hashed value and insert into db'''
                    hashed_pwd = generate_password_hash(newpass)
                    #update the oldpassword to the newpassword
                    user.user_password = hashed_pwd
                    db.session.commit()
                    flash('password changed successfully',category='success')
                    return redirect('/user/profile')
                else:
                    flash("Your password must contain Upper Case,lower case,number and any of the listed special charater(_,@,#,$) and should be more that 5")
                    return redirect('/user/profile/')
            else:
                flash('password does not match',category='error')
                return redirect('/user/profile/')
        else:
            flash('incorrect password',category='error')
            return redirect('/user/profile/')
    else:
        flash('All field must be filled',category='error')
        return redirect('/user/profile/')


#contactus
@app.route('/myapparel/contact/')
def contact():
    id = session.get('user')
    if id != None:
        deets = Users.query.get(id)
        mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
        return render_template('user/contact.html',deets=deets,mycart=mycart)
    else:
        return render_template('user/contact.html')

#orderhistory
@app.route('/myapparel/order-history/')
def order():
    if session.get('user') != None:
        #fetch from db
        deets = Users.query.get(session.get('user'))
        mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
        order = Orders.query.join(Payment).add_columns(Payment).filter(Orders.order_id==Payment.pay_orderid,Orders.order_userid==session.get('user')).all() 
        return render_template('user/order_history.html',deets=deets,order=order,mycart=mycart)
    else:
        return redirect(url_for('login'))


#orderdetailshistoryajax modal
@app.route('/history',methods=['POST','GET'])
def history():
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
    
#fitting
@app.route('/myapparel/fitting',methods=['POST','GET'])
def fitting():
    if session.get('user') !=None:
        if request.method == 'GET':
            deets = Users.query.get(session.get('user'))
            mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
            measure = Measurements.query.filter(Measurements.measure_userid==session.get('user')).first()
            return render_template('user/fitting.html',deets=deets,measure=measure,mycart=mycart)
        else:
            
            #retrieve for form
            bust = request.form.get('bust')
            off = request.form.get('off')
            shoubust = request.form.get('shoubust')
            under = request.form.get('under')
            shounip = request.form.get('shounip')
            nipple = request.form.get('nipple')
            back = request.form.get('back')
            toplen = request.form.get('toplen')
            tophalf = request.form.get('tophalf')
            topw = request.form.get('topw')
            sleeve = request.form.get('sleeve')
            hole = request.form.get('hole')
            hip = request.form.get('hip')
            skirtlen = request.form.get('skirtlen')
            skirtw = request.form.get('skirtw')
            trouserlen = request.form.get('trouserlen')
            dresslen = request.form.get('dresslen')
            measure_deets = Measurements.query.filter(Measurements.measure_userid==session.get('user')).first()
            if measure_deets:
                measure_deets.bust =bust
                measure_deets.off_shoulderdim=off
                measure_deets.shoulder_underbust=shoubust
                measure_deets.underbust_circum=under
                measure_deets.shoulder_nipple=shounip
                measure_deets.nipple_nipple=nipple
                measure_deets.back=back
                measure_deets.top_length=toplen
                measure_deets.top_halflength=tophalf
                measure_deets.top_waist=topw
                measure_deets.sleeve_length=sleeve
                measure_deets.sleeve_hole=hole
                measure_deets.hips=hip
                measure_deets.skirt_length=skirtlen
                measure_deets.skirt_waist=skirtw
                measure_deets.trouser_length=trouserlen
                measure_deets.dress_length=dresslen
                db.session.commit()
            else:
                data = Measurements(measure_userid=session.get('user'),bust=bust,off_shoulderdim=off,shoulder_underbust=shoubust,underbust_circum=under,shoulder_nipple=shounip,nipple_nipple=nipple,back=back,top_length=toplen,top_halflength=tophalf,top_waist=topw,sleeve_length=sleeve,sleeve_hole=hole,hips=hip,skirt_length=skirtlen,skirt_waist=skirtw,trouser_length=trouserlen,dress_length=dresslen)
                db.session.add(data)
                db.session.commit()
            flash("Measurement taken",category="success")
            return redirect(url_for('fitting'))
    else:
        return redirect(url_for('login'))


#ajaximagecar modal pic
'''@app.route('/image/data',methods=['POST','GET'])
def picmore():
    product_id = request.args.get('prop')
    images = db.session.query.filter(Images.image_productid==product_id).all()
    image_data = [{'filename': image.image_name} for image in images]
    return jsonify(image_data)'''



#category
@app.route('/myapparel/product/category/<id>')
def category_page(id):
    deets = Users.query.get(session.get('user'))
    mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
    caty = Categories.query.all()
    category_deets = Products.query.filter(Products.product_categoryid==id).all()
    product = []
    for k in category_deets:
        img=db.session.query(Images.image_name,Images.image_productid).filter(Images.image_productid==k.product_id).first()
        product.append(img)
    return render_template('user/product_category.html',category_deets=category_deets,product=product,caty=caty,deets=deets,mycart=mycart)

@app.route("/add-to-cart",methods=['POST','GET'])
def add_to_cart():
    #retrieve from ajax
    quantity = request.args.get('qty')
    product_id = request.args.get('productid')
    product = Products.query.get(product_id)
    totalamt = (quantity) * (product.product_price)
    #insert in database cart table
    data = Cart(cart_price=product.product_price,cart_total=totalamt,cart_qty=quantity,cart_productid=product_id)
    chk_cart = Cart.query.filter(Cart.cart_productid==product_id).first()
    if chk_cart:
        newqty = request.args.get('qty')
        chk_cart.cart_total=totalamt
        chk_cart.cart_qty=newqty
        db.session.commit()
    else:
        db.session.add(data)
        db.session.commit()
    data2send="<div class='alert alert-warning'>Added<div>"
    return "done" 

#adding the product to cart and also updating the qantity from shop and cart.html
@app.route("/addtocart/", methods=['POST','GET'])
def add_cart():
    #retrieve  data 
    quantity = request.args.get('quantity')
    productid = request.args.get('productid')
    pro = Products.query.get(productid)
    pic_deets = pro.the_image[0].image_name
    price = pro.product_price
    totalamt = int(quantity) * int(price)
    #insert in database table cart
    data = Cart(cart_price=price,cart_qty=quantity,cart_total=totalamt,cart_productid=productid,cart_pix=pic_deets,cart_userid=session.get('user'))
    chk_cart = Cart.query.filter(Cart.cart_productid==productid,Cart.cart_userid==session.get('user')).first()
    if chk_cart:
        newqty = request.args.get('quantity')
        chk_cart.cart_qty=newqty
        newtotal = int(newqty) * int(price)
        chk_cart.cart_total= newtotal
        db.session.commit()
    else:
        db.session.add(data)
        db.session.commit()
    data2send="<div class='alert alert-warning'>Added<div>"
    return data2send

#ajax to updatecart qty frim cart.html
@app.route('/addtocartqty/')
def add_qty():
    #retrieve data
    newqty = request.args.get('quantity')
    cartid = request.args.get('cartid')
    chkcart =  Cart.query.get(cartid)
    price = chkcart.cart_price
    chkcart.cart_qty = newqty
    newtotal = int(price) * int(newqty)
    chkcart.cart_total = newtotal
    db.sesson.commit()
    return "done" 



#ajaxsubtotal inlayout
@app.route("/subtotal")
def subtotal():
    #collect cart info from database
    data = Cart.query.filter(Cart.cart_userid==session.get('user')).all()
    total_price = sum(x.cart_total for x in data)
    return jsonify({'total': total_price})

#cart html
@app.route('/myapparel/cart/')
def cart():
    if session.get('user') != None:
        deets = Users.query.get(session.get('user'))
        mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
        return render_template('user/cart.html',mycart=mycart,deets=deets)
    else:
        return redirect(url_for('login'))

#deletecart
@app.route('/cart/delete/<id>')
def delete_cart(id):
    #retrieve the topic as an object
    the_cart = Cart.query.get_or_404(id)
    db.session.delete(the_cart)
    db.session.commit()
    return redirect(url_for('cart'))


#checkout
@app.route('/myapparel/checkout/',methods=['POST','GET'])
def checkout():
    if session.get('user') != None:
        if request.method == 'GET':
            deets = Users.query.get(session.get('user'))
            mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
            subtotal = sum(x.cart_total for x in mycart)
            shipping = 2000
            grandtotal = int(subtotal)+ int(shipping)
            state = States.query.all()
            return render_template('user/checkout.html',mycart=mycart,subtotal=subtotal,shipping=shipping,grandtotal=grandtotal,state=state,deets=deets)
        else:
            deets = Users.query.get(session.get('user'))
            #retrieve data from the form
            data = request.form
            name = data.get('rname')
            email = deets.user_email
            address = data.get('address')
            state = data.get('state')
            city = data.get('city')
            phone = data.get('phone')
            total = data.get('grandtotal')
                #generate the ref no and keep in session
            refno = int(random.random() * 100000000)
            session['reference'] = refno
            if name !="" and email !="" and address !="" and state !="" and city !="" and phone !="":
                query = Orders(order_userid=session.get('user'),order_name=name,order_amt=total,order_email=email,order_phone=phone,order_shipaddress=address,order_shipcity=city,order_stateid=state,order_refno=session.get('reference'))
                db.session.add(query)
                db.session.commit()
                #store the order id in session
                session['order_id'] = query.order_id
                #generate the ref no and keep in session
                refno = int(random.random() * 100000000)
                session['reference'] = refno
                cart_item=Cart.query.filter(Cart.cart_userid==session.get('user'))
                for i in cart_item:
                    detail = Order_details(detail_orderid=session.get('order_id'),detail_productid=i.cart_productid,detail_price=i.cart_price,detail_quantity=i.cart_qty)
                    db.session.add(detail)
                    db.session.commit()
                return redirect('/confirm/checkout/')
            else:
                flash('All fields required',category='error')
                return redirect('/myapparel/checkout/')
    else:
        return redirect(url_for('login'))        

        
#confirm checkout
@app.route('/confirm/checkout/',methods=['POST','GET'])
def confirm():
    if session.get('order_id') != None:
        if request.method == 'GET':
            deets = Users.query.get(session.get('user'))
            mycart = Cart.query.filter(Cart.cart_userid==deets.user_id).all()
            refno = session.get('reference')
            myorder = Orders.query.get(session.get('order_id'))
            return render_template('user/confirm.html',myorder=myorder,refno=refno,deets=deets,mycart=mycart)
        else:
            pay = Payment(pay_orderid=session.get('order_id'),pay_ref=session.get('reference'))
            mypayment = Payment.query.filter(Payment.pay_orderid==session.get('order_id')).first()
            if mypayment:
                mypayment.pay_ref=session.get('reference')
                db.session.commit()
            else:
                db.session.add(pay)
                db.session.commit()
            #api paystack
            order = Orders.query.get(session.get('order_id'))
            email = order.order_email
            amount = order.order_amt * 100#as to be in kobo 
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_5683a00b6ab49ce8f5a52b8ca956507b1d1b6021"}
            data={"amount":amount,"reference":session['reference'],"email":email}
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            rspjson= json.loads(response.text)
            if rspjson['status'] == True:
                url = rspjson['data']['authorization_url']
                return redirect(url)
            else:
                mypayment.pay_status="failed"
                db.session.commit()
                flash('payment not successful',category='failed')
                return redirect('/confirm/checkout/')
    else:
        return redirect('/myapparel/checkout/')

#payment route
@app.route('/payment/')
def payment():
    refid = session.get('reference')
    if refid ==None:
        return redirect('/')
    else:
        #connect to paystack verify
        headers={"Content-Type": "application/json","Authorization":"Bearer sk_test_5683a00b6ab49ce8f5a52b8ca956507b1d1b6021"}
        verifyurl= "https://api.paystack.co/transaction/verify/"+str(refid)
        response= requests.get(verifyurl, headers=headers)
        rspjson = json.loads(response.text)
        pay = Payment.query.filter(Payment.pay_ref==refid).first()
        if rspjson['status']== True:
            #by returning the rsjon we can see all the data received from paystack return rspjon
            #initiciate the order table to update
            pay.pay_amount=rspjson['data']['amount']
            pay.pay_status='paid'
            db.session.commit()
            #payment was successful
            return redirect('/confirmed_order')
        else:
            pay.pay_status='failed'
            db.session.commit()
            flash('payment failed try again in 5 minutes',category='error')
            return redirect('/confirm/checkout/')
        

#payment confirmation page(landing page)
@app.route('/confirmed_order/')
def confirmed_order():
    deets = Users.query.get(session.get('user'))
    order_deets= Orders.query.get(session.get('order_id'))
    date = order_deets.order_date
    formatdate= date.strftime('%A, %d %B %Y')
    #clear cart
    Cart.query.filter(Cart.cart_userid==session.get('user')).delete()
    db.session.commit()
    return render_template('user/confirm_order.html',deets=deets,order_deets=order_deets,formatdate=formatdate)


#error pages
@app.errorhandler(404)
def error404(error):
    return render_template('user/error404.html',error=error),404

@app.errorhandler(500)
def error500(error):
    return render_template('user/error500.html',error=error),500

