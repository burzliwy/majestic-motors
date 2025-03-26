import json

def load_cars():
    """Load cars data from the JSON file."""
    with open('data/cars.json', 'r') as file:
        return json.load(file)['cars']
        
def save_cars(cars):
    """Save cars data to the JSON file."""
    with open('data/cars.json', 'w') as file:
        json.dump({"cars": cars}, file, indent=4)

def parser_car():
    car_classes = {
        "economy": load_cars()[0]['vehicles'],
        "standard": load_cars()[1]['vehicles'],
        "luxury": load_cars()[2]['vehicles']
    }

    # Example usage: Print car classes
    for key, cars in car_classes.items():
        print(f"{key.capitalize()} Cars:")
        for car in cars:
            print(f"  - {car['make_model']} ({car['year']})")
    return car_classes

# Allow this script to be imported or run directly
if __name__ == "__main__":
    parser_car()

