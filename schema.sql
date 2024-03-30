-- https://www.postgresql.org/docs/current/datatype-enum.html


-- USED COMMANDS AT THE MOMENT --

CREATE TYPE drive_train_options AS ENUM ('Rear Wheel Drive', 'Front Wheel Drive', 'All Wheel Drive')
CREATE TYPE gas_type_options AS ENUM ('Gasoline', 'Diesel', 'Hybrid', 'Electric')
CREATE TYPE transmition_options AS ENUM ('Manual', 'Automatic')

CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username TEXT,
  password TEXT,
  email TEXT,
  first_name TEXT,
  last_name TEXT,
  phone_number TEXT
);

CREATE TABLE cars (
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
  is_new BOOLEAN
);

CREATE TABLE car_pictures (
  car_picture_id SERIAL PRIMARY KEY,
  car_id INTEGER REFERENCES cars(car_id),
  picture_data BYTEA,
  file_name TEXT 
);

-- Brands and their models --

CREATE TABLE allBrands (
  brand_id SERIAL PRIMARY KEY,
  brand_name TEXT
);

CREATE TABLE allModels (
  model_id SERIAL PRIMARY KEY,
  model_name TEXT,
  brand_id INTEGER REFERENCES allBrands(brand_id)
);


-- USED COMMANDS STOP HERE --





-- NOT YET USED COMMANDS --


CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(user_id),
    recipient_id INTEGER REFERENCES users(user_id),
    car_id INTEGER REFERENCES cars(car_id),
    content TEXT,
    sent_time DATETIME

);

CREATE TABLE userSavedSearches (
    saved_search_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    brand TEXT,
    model TEXT,
    min_year INTEGER,
    max_year INTEGER,
    max_milage INTEGER,
    min_price INTEGER,
    max_price INTEGER,
    drive_train TEXT,
    min_horsepower INTEGER,
    gas_type TEXT
);

CREATE TABLE userLikedCars (
    liked_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    car_id INTEGER REFERENCES cars(car_id),
);