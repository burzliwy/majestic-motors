from flask import Flask, render_template, request, redirect, url_for
import json
import re  
from datetime import datetime, timedelta

app = Flask(__name__)

def load_cars():
    with open('data/cars.json', 'r') as file:
        return json.load(file)['cars']


def save_cars(cars):
    with open('data/cars.json', 'w') as file:
        json.dump({"cars": cars}, file, indent=4)

def load_users():
    with open ('data/users.json', 'r') as file:
        return json.load(file)['users']
    
def save_users(users):
    with open ('data/users.json', 'w') as file:
        json.dump({"users": users}, file, indent=4) 

def parser_car():
    car_classes = {
        "economy": load_cars()[0]['vehicles'],
        "standard": load_cars()[1]['vehicles'],
        "luxury": load_cars()[2]['vehicles']
    }; return car_classes

def search_car_by_make_model(make_model):

    for car_class in load_cars():
        for car in car_class['vehicles']:
            
            if car['make_model'] == make_model:
                return {
                    "class": car_class['class'],  
                    "details": car  
                }
    return None  




# Route to index page
@app.route('/')
def index():
    return render_template('hub.html', cars=parser_car())

# Route to book car
@app.route('/book/<make_model>', methods=['POST'])
def book_car(make_model):
    cars = load_cars()
    for category in cars:
        for car in category['vehicles']:
            if car["make_model"] == make_model and not car["rented"]:
                return redirect(url_for('confirmation', make_model=make_model))
    return "Car not available or already rented.", 400

# Route to confirmation page
@app.route('/confirmation/<make_model>')
def confirmation(make_model):
    return render_template('confirmation.html', car_data=search_car_by_make_model(make_model), make_model=make_model)

@app.route('/checkout')
def checkout():
    car_data = {
        "make_model": request.args.get("make_model"),
        "year": request.args.get("year"),
        "mileage": request.args.get("mileage"),
        "rental_duration": request.args.get("duration"),
        "total_price": request.args.get("total_price"),
        "customer_name": request.args.get("customer_name"),
        "customer_email": request.args.get("customer_email"),
        "customer_phone": request.args.get("customer_phone"),
        "start_date": request.args.get("start_date"),
        "pickup_time": request.args.get("pickup_time"),
        "base_price": request.args.get("base_price"),
        "rental_fee": request.args.get("rental_fee"),
        "tax": request.args.get("tax"),
    }

    return render_template('checkout.html', car_data=car_data)

@app.route('/hub')
def hub():
    return render_template('index.html', cars=parser_car())

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/paymentconfirmation')
def paymentconfirmation():
    car_data = {
        "make_model": request.args.get("make_model"),
        "year": request.args.get("year"),
        "mileage": request.args.get("mileage"),
        "rental_duration": request.args.get("duration"),
        "total_price": float(re.sub(r'[^\d.]', '', request.args.get("total_price", "0"))),
        "customer_name": request.args.get("customer_name"),
        "customer_email": request.args.get("customer_email"),
        "customer_phone": request.args.get("customer_phone"),
        "start_date": request.args.get("start_date"),
        "pickup_time": request.args.get("pickup_time"),
    }

    users = load_users()
    user_exists = False
    for user in users:
        if user['email'] == car_data['customer_email']:
            user_exists = True
            if isinstance(user['totalSpent'], str):
                user['totalSpent'] = float(re.sub(r'[^\d.]', '', user['totalSpent']))
            user['totalSpent'] += car_data['total_price']
            user['rentedCars'].append({
                "make_model": car_data['make_model'],
                "start_date": car_data['start_date'],
                "pickup_time": car_data['pickup_time'],
                "duration": car_data['rental_duration'],
                "total_price": car_data['total_price']
            })
            break
    if not user_exists:
        users.append({
            "hasAccount": False,
            "name": car_data['customer_name'],
            "email": car_data['customer_email'],
            "phone": car_data['customer_phone'],
            "totalSpent": car_data['total_price'], 
            "rentedCars": [
                {
                    "make_model": car_data['make_model'],
                    "start_date": car_data['start_date'],
                    "pickup_time": car_data['pickup_time'],
                    "duration": car_data['rental_duration'],
                    "total_price": car_data['total_price']
                }
            ]
        })

    save_users(users)
    
    cars = load_cars()
    for category in cars:
        for car in category['vehicles']:
            if car["make_model"] == car_data['make_model']:
                car["rented"] = True
                break
    save_cars(cars)

    return render_template('paymentconfirmation.html', car_data=car_data)

@app.route('/returncar', methods=['GET', 'POST'])
def returncar():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')

        users = load_users()
        user = next((u for u in users if u['email'] == email and u['phone'] == phone), None)

        if not user:
            return render_template('returncar.html', error="No account found with the provided email and phone number.")

        if not user['rentedCars']:
            return render_template('returncar.html', error="No rented cars found for this account.")

        for car in user['rentedCars']:
            start_date = datetime.strptime(car['start_date'], "%Y-%m-%d")
            duration_days = int(car['duration'].split()[0]) 
            end_date = start_date + timedelta(days=duration_days)
            remaining_time = end_date - datetime.now()

            car['remaining_time'] = str(remaining_time).split(".")[0]  
            car['is_future_rental'] = datetime.now() < start_date 
        return render_template('returncar.html', rented_cars=user['rentedCars'], email=email)

    return render_template('returncar.html')

@app.route('/processreturn', methods=['POST'])
def process_return():
    email = request.form.get('email')
    make_model = request.form.get('make_model')

    # Load users and cars
    users = load_users()
    cars = load_cars()

    # Find the user and remove the rented car
    user = next((u for u in users if u['email'] == email), None)
    if user:
        user['rentedCars'] = [car for car in user['rentedCars'] if car['make_model'] != make_model]
        save_users(users)

    # Mark the car as available
    for category in cars:
        for car in category['vehicles']:
            if car['make_model'] == make_model:
                car['rented'] = False
                break
    save_cars(cars)

    return redirect('/returncar')

@app.route('/condition')
def condition():
    return render_template('condition.html')

    

if __name__ == '__main__':
    app.run(debug=True)


