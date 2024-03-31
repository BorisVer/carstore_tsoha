from sqlalchemy.sql import text
import base64
from db import db

# Here are all the working functions that get used by the routes.py

def get_brands():
    # Gets all brands in alphabetical order
    sql = text("SELECT DISTINCT brand_name FROM allBrands ORDER BY brand_name ASC" )
    brands = [i[0].title() for i in db.session.execute(sql).fetchall()]
    return brands

def get_models(brand):
    # Gets all models for the chosen brand
    sql = text("SELECT m.model_name FROM allModels m JOIN allBrands b ON m.brand_id = b.brand_id WHERE b.brand_name = :brand ORDER BY m.model_name ASC")
    models = [i[0] for i in db.session.execute(sql, {"brand": brand}).fetchall()]
    correct_spelling = []
    for model in models:
        correct_spelling.append(spelling(model))
    return correct_spelling

def spelling(model):
    # Fixes the spelling so model names are correctly caps (V90, Altima, GT-R)
    model = model.split(" ")
    new_model = ""
    for part in model:
        if sum(i.isalpha() for i in part) > 3:
            new_model += part.title()
        else:
            for char in part:
                if char.isalpha():
                    new_model += char.upper()
                else:
                    new_model += char
        new_model += " "
    return new_model[:-1]
            


def check_brand(brand, model):
    # Checks that the given brand exists in the database. If it does goes to check_model(), else return error code 1
    brand = brand.lower()
    model = model.lower()
    sql = text("SELECT brand_name FROM allbrands WHERE brand_name = :brand")
    if len([i[0] for i in db.session.execute(sql, {"brand":brand}).fetchall()]) > 0:
        return check_model(brand, model)
    return 1

def check_model(brand, model):
    # Checks that the models exists in the database and returns error code 0 (correct), else return error code 2
    sql = text("SELECT m.model_name FROM allmodels m JOIN allbrands b ON m.brand_id = b.brand_id WHERE b.brand_name = :brand AND m.model_name = :model")
    if len([i[0] for i in db.session.execute(sql, {"brand":brand, "model":model}).fetchall()]) > 0:
        return 0
    return 2

def check_data(year, mileage, price, horsepower, torque, register, weight, seating, door, engine):
    # Checks that all the inputed data from the add listing are valid
    # Make the register into numbers and letters to check for valid length
    register = register.strip("-")
    register_letters = "".join(i for i in register if i.isalpha())
    register_numbers = "".join(i for i in register if i.isdigit())
    allowed_register_letter = [2,3]
    allowed_register_number = [0,1,2,3]
    # Check each input that they are valid and return the error number back to give feedback what has failed
    if int(year) < 1885 or int(year) > 2026:
        return 4
    elif int(mileage) < 0 or int(mileage) > 999999:
        return 5
    elif int(price) < 0 or int(price) > 9999999:
        return 6
    elif int(horsepower) < 0 or int(horsepower) > 9999:
        return 7
    elif int(torque) < 0 or int(torque) > 9999:
        return 8
    elif len(register_letters) not in allowed_register_letter or len(register_numbers) not in allowed_register_number:
        return 9
    elif int(weight) < 100 or int(weight) > 9999:
        return 10
    elif int(seating) < 0 or int(seating) > 99:
        return 11
    elif int(door) < 0 or int(door) > 5:
        return 12
    elif float(engine) < 0.5 or float(engine) > 15:
        return 13
    else:
        return 0

def add_car(brand, model, year, mileage, price, horsepower, torque, engine, register, weight, seating, door, drive_train, gas_type, transmition, condition, description, file_list, username):
    # Uses all the inputed info to create a "listing" aka car in the cars database and connect it to its images in the car_pictures database
    user_id = db.session.execute(text("SELECT user_id FROM users WHERE username = :username"), {"username":username}).fetchone()[0]
    brand = brand.lower()
    model = model.lower()
    if condition == "new":
        isnew = True
    else:
        isnew = False
    sql = text("""
        INSERT INTO cars (
               user_id,
               brand,
               model,
               year,
               mileage,
               price,
               drive_train,
               horsepower,
               torque,
               engine,
               gas_type,
               transmition,
               register,
               weight,
               seating_capacity,
               door_count,
               description,
               is_new
        ) VALUES (
               :user_id,
               :brand,
               :model,
               :year,
               :mileage,
               :price,
               :drive_train,
               :horsepower,
               :torque,
               :engine,
               :gas_type,
               :transmition,
               :register,
               :weight,
               :seating_capacity,
               :door_count,
               :description,
               :is_new
        )  RETURNING car_id
""")
    # Inputing info and at the same time returning the car_id
    car_id = db.session.execute(sql, {
        "user_id": user_id,
        "brand": brand,
        "model": model,
        "year": year,
        "mileage": mileage,
        "price": price,
        "drive_train": drive_train,
        "horsepower": horsepower,
        "torque":torque,
        "engine":engine,
        "gas_type": gas_type,
        "transmition": transmition,
        "register":register,
        "weight":weight,
        "seating_capacity":seating,
        "door_count":door,
        "description": description,
        "is_new":isnew,
        }).fetchone()[0]
    db.session.commit()
    # For each file they are added to the car_pictures and connected to the cars with the car_id value
    for file in file_list:
        sql_images = text("INSERT INTO car_pictures (car_id,picture_data,file_name) VALUES (:car_id,:picture_data,:file_name)")
        db.session.execute(sql_images, {"car_id":car_id,"picture_data":file.read(),"file_name":file.name})
        db.session.commit()
    return True, ""

def get_listing_info(listing):
    # Gets all the listings info using the given listing id = car_id
    # TODO make this code part better
    sql = text("SELECT user_id,brand, model,year,mileage,price,drive_train,horsepower,torque, engine, gas_type,transmition,register,weight,seating_capacity,door_count,description,is_new,car_id FROM cars WHERE car_id = :listing")
    result = [i for i in db.session.execute(sql, {"listing":listing}).fetchall()]
    user_id = result[0][0]
    brand = result[0][1]
    model = result[0][2]
    year = result[0][3]
    mileage = result[0][4]
    price = result[0][5]
    drive = result[0][6]
    horsepower = result[0][7]
    torque = result[0][8]
    engine = result[0][9]
    gas = result[0][10]
    transmition = result[0][11]
    register = result[0][12]
    weight = result[0][13]
    seating = result[0][14]
    door = result[0][15]
    description = result[0][16]
    is_new = result[0][17]
    car_id = result[0][18]
    # Using the listings car_id get the files connected to it
    sql = text("SELECT picture_data,file_name FROM car_pictures WHERE car_id = :car_id")
    all_data = [i for i in db.session.execute(sql, {"car_id":car_id}).fetchall()]
    model = spelling(model)
    return user_id,brand, model,year,mileage,price,drive,horsepower,torque, engine,gas,transmition,register, weight, seating, door,description,is_new,all_data

def get_user_info(user_id):
    # For the listings the user data is collected
    sql = text("SELECT first_name, last_name, email, phone_number FROM users WHERE user_id = :user_id")
    allcontacts = db.session.execute(sql, {"user_id":user_id}).fetchall()[0]
    first = allcontacts[0]
    last = allcontacts[1]
    email = allcontacts[2]
    phone = allcontacts[3]
    return first, last, email, phone 

def get_sql_and_input(selected_brand, selected_model, allinfo, sortby):
        # Create a sql and the sql input for the selected ristrictions with what the search is going to happen 
        allinfo = eval(allinfo)
        minprice = allinfo[0]
        maxprice = allinfo[1]
        minyear = allinfo[2]
        maxyear = allinfo[3]
        minmileage = allinfo[4]
        maxmileage = allinfo[5]
        gas = allinfo[6]
        drive = allinfo[7]
        transmition = allinfo[8]
        # Craeting the sql by adding all the selected options are WHERE restrictions at the end
        sql_fetch = "SELECT brand,model,year,mileage,price,car_id FROM cars "
        # For each option we make also the input and add that to the input dict
        sql_where = []
        input = {}
        print(selected_model)
        if  selected_brand != "False" and selected_brand != "All Brands":
            sql_where.append("brand = :brand")
            input["brand"] = selected_brand.lower()
        if  selected_model != "False" and selected_model != "All Models":
            sql_where.append("model = :model")
            input["model"] = selected_model.lower()
        if minprice:
            sql_where.append("price >= :minprice")
            input["minprice"] = int(minprice)
        if maxprice:
            sql_where.append("price <= :maxprice")
            input["maxprice"] = int(maxprice)
        if minyear:
            sql_where.append("year >= :minyear")
            input["minyear"] = int(minyear)
        if maxyear:
            sql_where.append("year <= :maxyear")
            input["maxyear"] = int(maxyear)
        if minmileage:
            sql_where.append("mileage >= :minmileage")
            input["minmileage"] = int(minmileage)
        if maxmileage:
            sql_where.append("mileage <= :maxmileage")
            input["maxmileage"] = int(maxmileage)
        if gas:
            sql_where.append("gas_type = :gas")
            input["gas"] = int(gas)
        if drive:
            sql_where.append("drive_train = :drive")
            input["drive"] = int(drive)
        if transmition:
            sql_where.append("transmition = :transmition")
            input["transmition"] = int(transmition)
        # If there is a added search add it to the end of the sql_fetch
        first = True
        for i in sql_where:
            if first:
                sql_fetch += "WHERE " + i
                first = False
            else:
                sql_fetch += " AND " + i
        # Create the sort by
        if sortby == "pricedescending":
            sql_sortby = " ORDER BY price DESC"
        elif sortby == "priceascending":
            sql_sortby = " ORDER BY price ASC"
        elif sortby == "yeardescending":
            sql_sortby = " ORDER BY year DESC"
        elif sortby == "yearascending":
            sql_sortby = " ORDER BY year ASC"
        elif sortby == "mileagedescending":
            sql_sortby = " ORDER BY mileage DESC"
        elif sortby == "mileageascending":
            sql_sortby = " ORDER BY mileage ASC"
        sql_fetch += sql_sortby
        print(sql_fetch)
        return sql_fetch, input


def run_search(selected_brand, selected_model, allinfo, sortby):
        sql_fetch, input = get_sql_and_input(selected_brand, selected_model, allinfo, sortby)
        all_listings = [i for i in db.session.execute(text(sql_fetch), input).fetchall()]
        amount_of_listings = len(all_listings)
        modified_listings = []
        print(all_listings)
        # Decode the image for each search
        for i in all_listings:
            car_id = i[5]
            print(car_id)
            first_pic = db.session.execute(text("SELECT picture_data FROM car_pictures WHERE car_id = :car_id"), {"car_id":car_id}).fetchone()[0]
            first_pic_data = first_pic
            encoded_data = base64.b64encode(first_pic_data).decode("ascii")
            new_item = list(i)
            new_item.append(encoded_data)
            new_item[0] = i[0].title()
            new_item[1] = i[1].title()
            new_item[5] = car_id
            modified_listings.append(new_item)
        brand = selected_brand.title()
        model = spelling(selected_model)
        return brand,model,amount_of_listings,modified_listings