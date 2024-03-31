from db import db
import json
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash


# Inserts all brands and their coresponding models found in the allcarlist.json into the tables
def make_brands_models():

    db.session.execute(text("CREATE TABLE allBrands (brand_id SERIAL PRIMARY KEY, brand_name TEXT )"))
    
    db.session.execute(text("CREATE TABLE allModels (model_id SERIAL PRIMARY KEY, model_name TEXT, brand_id INTEGER REFERENCES allBrands(brand_id) )"))

    db.session.execute(text("CREATE TYPE drive_train_options AS ENUM ('Rear Wheel Drive', 'Front Wheel Drive', 'All Wheel Drive')"))
    db.session.execute(text("CREATE TYPE gas_type_options AS ENUM ('Gasoline', 'Diesel', 'Hybrid', 'Electric')"))
    db.session.execute(text("CREATE TYPE transmition_options AS ENUM ('Manual', 'Automatic')"))

    db.session.commit()
    
    with open("allcarlist.json", "r") as f:
        data = json.load(f)

        found_brands = []

        counter = 0

        for car in data:
            # Using .lower() so there are less typo related problems later
            brand = car["Make"].lower()
            model = car["Model"].lower()

            print(brand)

            if brand not in found_brands:
                found_brands.append(brand)
                brand_id = len(found_brands)
                sql_brand = text("INSERT INTO allbrands (brand_name) VALUES (:brand)")
                db.session.execute(sql_brand, {"brand": brand})
                counter += 1
                print(counter)
        
            sql_model = text("INSERT INTO allmodels (model_name, brand_id) VALUES (:model, :brand_id)")
            db.session.execute(sql_model, {"model": model, "brand_id": brand_id})

        db.session.commit()

    

def make_basics_database():

    db.session.execute(text("""CREATE TABLE users (
user_id SERIAL PRIMARY KEY,
username TEXT,
password TEXT,
email TEXT,
first_name TEXT,
last_name TEXT,
phone_number TEXT)"""))
    db.session.execute(text("""CREATE TABLE cars (
car_id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(user_id),
brand TEXT,
model TEXT,
year INTEGER,
mileage INTEGER,
price INTEGER,
drive_train drive_train_options,
horsepower INTEGER,
torque INTEGER,
engine FLOAT,
gas_type gas_type_options,
transmition transmition_options,
register TEXT,
weight INTEGER,
seating_capacity INTEGER,
door_count INTEGER,
description TEXT,
is_new BOOLEAN)"""))
    db.session.execute(text("""CREATE TABLE car_pictures (
car_picture_id SERIAL PRIMARY KEY,
car_id INTEGER REFERENCES cars(car_id),
picture_data BYTEA,
file_name TEXT) """))
    db.session.commit()
    # Add the users, made with a random name generator into file

    with open("starterusers.json") as f:
        data = json.load(f)
        for user in data:
            hash_value = generate_password_hash(user["password"])
            sql = text("INSERT INTO users (username, password, email, first_name, last_name, phone_number) VALUES (:username, :password, :email, :first_name, :last_name, :phone_number)")
            db.session.execute(sql, {"username":user["username"], "password":hash_value, "email":user["email"], "first_name":user["first_name"], "last_name":user["last_name"], "phone_number":user["phone_number"]})
            db.session.commit()

    # Add the cars
    with open("startercars.json", "r") as f:
        data = json.load(f)
        for car in data:


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
                "user_id": car["user_id"],
                "brand": car["brand"],
                "model": car["model"],
                "year": car["year"],
                "mileage": car["mileage"],
                "price": car["price"],
                "drive_train": car["drive_train"],
                "horsepower": car["horsepower"],
                "torque": car["torque"],
                "engine": car["engine"],
                "gas_type": car["gas_type"],
                "transmition": car["transmition"],
                "register": car["register"],
                "weight": car["weight"],
                "seating_capacity": car["seating_capacity"],
                "door_count": car["door_count"],
                "description": car["description"],
                "is_new": car["is_new"]
                }).fetchone()[0]
            db.session.commit()


        # For each file they are added to the car_pictures and connected to the cars with the car_id value
    
    with open("starterimages.json") as f:
        data = json.load(f)
        for image in data:
            with open(image["picture_path"], "rb") as image_file:
                image_data = image_file.read()
            print(image)
            sql = text("INSERT INTO car_pictures (car_id, picture_data, file_name) VALUES (:car_id, :picture_data, :file_name)")
            db.session.execute(sql, {"car_id":image["car_id"], "picture_data":image_data, "file_name":image["file_name"]})
            db.session.commit()

