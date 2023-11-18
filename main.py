import csv

import csv
import random  # Import the random module


# Step 1: Read and parse CSV files with semicolon separators
def read_csv(filename):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')  # Use semicolon as the delimiter
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            data.append(row)
    return data


user_data = read_csv('userprofile.csv')
restaurant_data = read_csv('places.csv')
cuisine_data = read_csv('place_cuisine.csv')
ratings_data = read_csv('ratings.csv')

# Step 2: Calculate overall cuisine ratings
cuisine_ratings = {}  # Dictionary to store user ratings for cuisines

for rating_row in ratings_data:
    user_id, place_id, general_rating, food_rating, service_rating = rating_row  # Remove the last value
    overall_cuisine_rating = (
            float(general_rating) * 1.4 +
            float(food_rating) * 2.5 +
            float(service_rating) * 1.8 +
            random.uniform(0.0, 1.0)  # Generate a random number between 0.0 and 1.0
    )

    if user_id not in cuisine_ratings:
        cuisine_ratings[user_id] = {}

    if place_id not in cuisine_ratings[user_id]:
        cuisine_ratings[user_id][place_id] = []

    cuisine_ratings[user_id][place_id].append(overall_cuisine_rating)


