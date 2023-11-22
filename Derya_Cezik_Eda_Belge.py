import csv
import random
import recommendations

def read_csv_files(filename):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        next(csv_reader)
        for row in csv_reader:
            data.append(row)
    return data

user_data = read_csv_files('userprofile.csv')
restaurant_data = read_csv_files('places.csv')
cuisine_data = read_csv_files('place_cuisine.csv')
ratings_data = read_csv_files('ratings.csv')

cuisine_ratings = {}
for rating_row in ratings_data:
    user_id, place_id, general_rating, food_rating, service_rating = rating_row
    overall_cuisine_rating = (
        float(general_rating) * 1.4 +
        float(food_rating) * 2.5 +
        float(service_rating) * 1.8 +
        random.uniform(0.0, 1.0)
    )
    if user_id not in cuisine_ratings:
        cuisine_ratings[user_id] = {}
    if place_id not in cuisine_ratings[user_id]:
        cuisine_ratings[user_id][place_id] = []
    cuisine_ratings[user_id][place_id].append(overall_cuisine_rating)

def calculate_cuisine_ranks(cuisine_data):
    cuisine_ranks = {}
    for row in cuisine_data:
        place_id, cuisine = row[0], row[1]
        if place_id not in cuisine_ranks:
            cuisine_ranks[place_id] = []
        cuisine_ranks[place_id].append(cuisine)

    for place_id, cuisines in cuisine_ranks.items():
        total_cuisines = len(cuisines)
        if total_cuisines == 1:
            cuisine_ranks[place_id] = [(cuisines[0], 2.0)]
        else:
            for i, cuisine in enumerate(cuisines):
                rank = 2.0 - (i / (total_cuisines - 1))
                cuisine_ranks[place_id][i] = (cuisine, rank)

    return cuisine_ranks

cuisine_ranks = calculate_cuisine_ranks(cuisine_data)

final_ratings = {}
user_id_to_name = {row[0]: row[1] for row in user_data} 

for user_row in user_data:
    user_id = user_row[0]
    user_name = user_id_to_name.get(user_id, "Unknown User")
    final_ratings[user_name] = {}

    if user_id in cuisine_ratings:
        for place_id, ratings in cuisine_ratings[user_id].items():
            if place_id in cuisine_ranks:
                for i, (cuisine, rank) in enumerate(cuisine_ranks[place_id]):
                    if i < len(ratings):
                        ratings[i] *= rank
                average_rating = sum(ratings) / len(ratings) if ratings else 0
                for cuisine, _ in cuisine_ranks.get(place_id, []):
                    if cuisine not in final_ratings[user_name]:
                        final_ratings[user_name][cuisine] = 0
                    final_ratings[user_name][cuisine] += average_rating

def transform_ratings_to_cuisine(ratings):
    cuisine_based_ratings = {}
    for user, user_ratings in ratings.items():
        for cuisine, rating in user_ratings.items():
            if cuisine not in cuisine_based_ratings:
                cuisine_based_ratings[cuisine] = {}
            cuisine_based_ratings[cuisine][user] = rating
    return cuisine_based_ratings


def calculate_similarity_matrix(ratings, similarity_metric):
    cuisine_based_ratings = transform_ratings_to_cuisine(ratings)
    cuisines = list(cuisine_based_ratings.keys())
    matrix = {}

    for cuisine in cuisines:
        matrix[cuisine] = {}

    for i, cuisine1 in enumerate(cuisines):
        for j, cuisine2 in enumerate(cuisines):
            if i == j:
                matrix[cuisine1][cuisine2] = 1
            elif j > i:
                sim = similarity_metric(cuisine_based_ratings, cuisine1, cuisine2)
                matrix[cuisine1][cuisine2] = sim
                matrix[cuisine2][cuisine1] = sim

    return matrix

def main_menu(final_ratings):
    similarity_metric = None
    recommendation_model = None
    max_recommendations = None

    while True:
        print("\n--- Cuisine Recommendation System Menu ---")
        print("1. Select a similarity metric (Euclidean/Pearson)")
        print("2. Display cuisine similarity matrix")
        print("3. Select a recommendation model (User-based/Item-based)")
        print("4. Set the maximum number of recommendations to be made")
        print("5. List similar persons to a given person")
        print("6. Make a recommendation to a specific user")
        print("7. Exit the program")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            metric_choice = input("Select a similarity metric (Euclidean/Pearson): ").lower()
            if metric_choice in ['euclidean', 'pearson']:
                similarity_metric = recommendations.sim_distance if metric_choice == 'euclidean' else recommendations.sim_pearson
                print(f"Similarity metric set to {metric_choice.title()}.")
            else:
                print("Invalid choice. Please select either 'Euclidean' or 'Pearson'.")

        elif choice == '2':
            if similarity_metric:
                sim_matrix = calculate_similarity_matrix(final_ratings, similarity_metric)
                for cuisine1 in sim_matrix:
                    for cuisine2 in sim_matrix[cuisine1]:
                        print(f"{cuisine1} - {cuisine2}: {sim_matrix[cuisine1][cuisine2]}")
            else:
                print("Please select a similarity metric first (menu item 1).")

        elif choice == '3':
            recommendation_model = input("Select a recommendation model (User-based/Item-based): ").lower()
            if recommendation_model in ['user-based', 'item-based']:
                print(f"Recommendation model set to {recommendation_model.title().replace('-', ' ')}.")
            else:
                print("Invalid choice. Please select either 'User-based' or 'Item-based'.")

        elif choice == '4':
            try:
                max_recommendations = int(input("Enter the maximum number of recommendations: "))
                if max_recommendations <= 0:
                    raise ValueError
                print(f"Maximum number of recommendations set to {max_recommendations}.")
            except ValueError:
                print("Invalid input. Please enter a positive integer.")

        elif choice == '5':
            if similarity_metric and recommendation_model and max_recommendations is not None:
                user_name = input("Enter the name of the person: ")
                if user_name in final_ratings:
                    similar_users = recommendations.topMatches(final_ratings, user_name, n=max_recommendations,
                                                               similarity=similarity_metric)
                    print("Similar users:")
                    for score, user in similar_users:
                        print(f"{user}: {score}")
                else:
                    print("User not found.")
            else:
                print("Ensure you have selected the similarity metric (1), recommendation model (3), and set the maximum recommendations (4).")

        elif choice == '6':
            if similarity_metric and recommendation_model and max_recommendations is not None:
                user_name = input("Enter the name of the person for recommendations: ")
                if user_name in final_ratings:
                    user_recommendations = recommendations.getRecommendations(final_ratings, user_name,
                                                                              similarity=similarity_metric)[:max_recommendations]
                    print("Recommendations:")
                    for score, item in user_recommendations:
                        print(f"{item}: {score}")
                else:
                    print("User not found.")
            else:
                print("Ensure you have selected the similarity metric (1), recommendation model (3), and set the maximum recommendations (4).")

        elif choice == '7':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

main_menu(final_ratings)