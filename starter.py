from db import db
import json
from sqlalchemy.sql import text

# Inserts all brands and their coresponding models found in the allcarlist.json into the tables
def make_brands_models():
    
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