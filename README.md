# carwebsite_tsoha

A car sale website, where users can
- log in
- make a new user
- add info to the user
- add a car for sale
- look for a car and filter cars by brand, model, year, mileage, gas type, transmition, drive train
- can chose in what order the results are filtered
  
To run
- Clone the repo to your computer and create a .env file into it. insert this into the .env file:
  
  > DATABASE_URL=<local-address-of-the-database>
  > SECRET_KEY=<secret-key>

- Next run these inside the repo clone:

 - python3 -m venv venv
 - source venv/bin/activate
 - pip install -r ./requirements.txt

- Now you can run the code with:

  flask run

Aditional Info
- the starter.py file is called upon first lauch and will create all needed tables and insert needed data into them so website should be usable directly
- there is also a second part run upon first lauch that adds 10 users and 10 cars to the website, this can be disabled by comenting out that part of the code if needed, routes.py : line 20
