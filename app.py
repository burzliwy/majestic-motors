from flask import Flask, render_template, request, redirect, url_for
import json


app = Flask(__name__)

def load_cars():
    with open('data/cars.json', 'r') as file:
        return json.load(file)['cars']


def save_cars(cars):
    with open('data/cars.json', 'w') as file:
        json.dump({"cars": cars}, file, indent=4)

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

print(search_car_by_make_model('Toyota Corolla')['details']['make_model']) 



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
    }

    return render_template('checkout.html', car_data=car_data)

@app.route('/hub')
def hub():
    return render_template('index.html', cars=parser_car())

@app.route('/auth')
def auth():
    return render_template('auth.html')

if __name__ == '__main__':
    app.run(debug=True)
 

