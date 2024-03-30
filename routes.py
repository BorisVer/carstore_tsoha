from app import app
from db import db
from flask import render_template, request, redirect, url_for, session
import limiter
import starter
from sqlalchemy.sql import text
import base64
from werkzeug.security import check_password_hash, generate_password_hash



###### TODO 
# Sort by
# Be able to see current user data
# Like listings and remove "sold" cars
# Have a back button on the /listing
# Make everything look better
# Make not read False False when no brand chosen



# Check if the brands are added to the table brands, this is only run the first time the website is opened
brand_checker = db.session.execute(text("SELECT * FROM allbrands")).fetchall()
if len(brand_checker) == 0:
    starter.make_brands_models()

# Get all brands
brands = limiter.get_brands()

# The main page, with the search options, login and links to the other sites
@app.route("/", methods=["POST","GET"])
def index(): 
    if request.method == 'POST':
        # If submitted a brand returns all that brands models
        if "submit_brand" in request.form:
            selected_brand = request.form.get('brand_selector')
            models = limiter.get_models(selected_brand.lower())
            return render_template("index.html", brands=brands, models=models, selected_brand=selected_brand)
        # Gets all the info inputed and moves to the search part
        elif "submit_all" in request.form:
            selected_model = request.form.get("model_selector")
            if selected_model == "All Models":
                selected_model = False
            selected_brand = request.form.get("selected_brand")
            if not selected_brand:
                selected_brand = False
            minprice = request.form.get("minprice")
            maxprice = request.form.get("maxprice")
            minyear = request.form.get("minyear")
            maxyear = request.form.get("maxyear")
            minmileage = request.form.get("minmileage")
            maxmileage = request.form.get("maxmileage")
            gas = request.form.get("gas_selector")
            drive = request.form.get("drive_selector")
            transmition = request.form.get("transmition_selector")
            allinfo = [minprice, maxprice, minyear, maxyear, minmileage,maxmileage,gas,drive,transmition]
            sortby = "pricedescending"
            return redirect(url_for("search", selected_brand=selected_brand, selected_model=selected_model, allinfo=allinfo, sortby=sortby))
    return render_template("index.html", brands=brands)

# Logic for loging in, hash_value to hide passwords in the data
@app.route("/login",methods=["GET","POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT user_id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if not user:
        error = "Username or password incorrect"
        return render_template("index.html", brands=brands, error=error)
    else:
        hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
    return redirect("/")

# Removes the session login
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

# Bring to loginwebsite, checks that username is not taken an passwords are the same
@app.route("/makeuser", methods=["GET","POST"])
def makeuser():
    error = 0
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        passwordcheck = request.form["passwordcheck"]
        if len(db.session.execute(text("SELECT username FROM users WHERE username = :username"), {"username":username}).fetchall()) > 0:
            error = 1
            return render_template("makeuser.html", error=error)
        if password != passwordcheck:
            error = 2
            return render_template("makeuser.html", error=error)
        
        hash_value = generate_password_hash(password)
        sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
        return redirect("/")
    return render_template("makeuser.html", error=error)

# Brings to the add info page, where users can add contact info
# TODO check all info and make user after creating user automatically move to this place, also show current info
@app.route("/addinfo", methods=["GET","POST"])
def addinfo():
    done = False
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        username = session["username"]
        sql = text("UPDATE users SET email = :email, first_name = :first, last_name = :last, phone_number = :phone WHERE username = username")
        db.session.execute(sql, {"email":email, "first":first_name, "last":last_name, "phone":phone, "username":username})
        db.session.commit()
        done = True
    return render_template("addinfo.html", done=done)


# Runs the search with brand, model and all the rest as link info
@app.route("/search/<selected_brand>/<selected_model>/<allinfo>/<sortby>", methods=["POST", "GET"])
def search(selected_brand, selected_model, allinfo, sortby):
    if request.method == "GET":
        brand,model,amount_of_listings,modified_listings = limiter.run_search(selected_brand, selected_model, allinfo, sortby)

    if request.method == "POST":
        sortby = request.form.get("sortby")
        return redirect(url_for("search", selected_brand=selected_brand, selected_model=selected_model, allinfo=allinfo, sortby=sortby))

    return render_template("search.html", brand=brand, model=model, amount_of_listings=amount_of_listings, all_listings=modified_listings)
    
# Add car page and gets all inputed info and runs a check that they are valid
@app.route("/addcars", methods=["GET","POST"])
def add_car_for_sale():
    if request.method == "POST":
        brand = request.form.get("brand").lower()
        model = request.form.get("model").lower()
        year = request.form.get("year")
        mileage = request.form.get("mileage")
        price = request.form.get("price")
        horsepower = request.form.get("horsepower")
        torque = request.form.get("torque")
        engine = request.form.get("engine")
        register = request.form.get("register")
        weight = request.form.get("weight")
        seating = request.form.get("seating")
        door = request.form.get("door")
        drive_train = request.form.get("drive")
        gas_type = request.form.get("gas")
        transmition = request.form.get("transmition")
        condition = request.form.get("condition")
        description = request.form.get("description")
        file_list = request.files.getlist("files")
        username = session["username"]
        result = limiter.check_model(brand, model)
        if result == 0:
            result = limiter.check_data(year, mileage, price, horsepower, torque, register, weight, seating, door, engine)
            if result != 0:
                return redirect(url_for("listing_status_bad",result=result))
            status, result = limiter.add_car(brand, model, year, mileage, price, horsepower, torque, engine, register, weight, seating, door, drive_train, gas_type, transmition, condition, description, file_list, username)
            if status:
                return redirect("listingstatusgood")
            return redirect(url_for("listing_status_bad",result=result))
        else:
            return redirect(url_for("listing_status_bad",result=result))
        
    return render_template("addListing.html")

# A page to show that making the listing has been a sucsses
@app.route("/listingstatusgood")
def listing_status_good():
    return render_template("listingcompleted.html")

# A page to show that making the listing has failed, also shows why
# TODO add more error texts, move the error handler to limiter.py to make more clear
@app.route("/listingstatusfail/<result>")
def listing_status_bad(result):
    result = int(result)
    if result == 1:
        failure = "Your listing was not completed because your given brand does not exist. Check try again or fill in 'unknown' into both fields."
    if result == 2:
        failure = "Your listing was not completed because your given model does not exist. Check try again or fill in 'unknown' into both fields." 
    elif result == 3:
        failure = "Your image filename was incorrect."
    elif result == 4:
        failure = "Your image file was too large."
    else:
        failure = "Something else"
    return render_template("listingfailed.html", failure=failure)

# Reroutes to the listing website and gets the listings info to the html
@app.route("/listing/<listing_id>")
def listing(listing_id):
    user_id,brand, model,year,mileage,price,drive,horsepower,torque, engine,gas,transmition,register, weight, seating, door,description,is_new,all_data = limiter.get_listing_info(listing_id)
    first, last, email, phone = limiter.get_user_info(user_id)
    images = []
    for data in all_data:
        images.append(base64.b64encode(data[0]).decode('ascii'))
        #file_name = data[1]
    if is_new:
        condition = "New"
    else:
        condition = "Used"
    return render_template("listing.html" , user_id=user_id,brand=brand.title(), model=model.title(),year=year,mileage=mileage,price=price,drive=drive,horsepower=horsepower,torque=torque,engine=engine,gas=gas,transmition=transmition,register=register,weight=weight,seating=seating,door=door,description=description, condition=condition, images=images, first=first, last=last, email=email, phone=phone)
