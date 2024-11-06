from flask import Flask, request, jsonify
from flask_cors import CORS  # To handle cross-origin requests
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load the dataset and prepare the model components
def load_data():
    df = pd.read_csv('data/google_hotel_data_clean_v2.csv')
    # Create binary columns for each feature
    selected_features = ['Free breakfast', 'Free Wi-Fi', 'Air conditioning', 'Restaurant', 
                        'Free parking', 'Room service', 'Pool', 'Full-service laundry', 
                        'Fitness center', 'Kitchen', 'Airport shuttle', 'Spa']
    
    # Initialize feature columns with zeros
    for feature in selected_features:
        df[feature] = 0
    
    # Fill in the binary values by checking Feature_1 through Feature_9
    feature_cols = ['Feature_1', 'Feature_2', 'Feature_3', 'Feature_4', 'Feature_5', 
                   'Feature_6', 'Feature_7', 'Feature_8', 'Feature_9']
    
    for feature in selected_features:
        for col in feature_cols:
            df.loc[df[col] == feature, feature] = 1
            
    return df, selected_features

# Implementation of the similarity function from your recommender model
def similarity_features_only(df, user_features, selected_features):
    similarity_scores = cosine_similarity([user_features], df[selected_features])
    df['Similarity'] = similarity_scores[0]
    return df.sort_values(by='Similarity', ascending=False)

# Load data at startup
df, selected_features = load_data()

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        city = data.get('city')
        user_features = data.get('features')
        
        # Filter by city if provided
        city_df = df[df['City'].str.lower() == city.lower()] if city else df
        
        if city_df.empty:
            return jsonify({'error': 'No hotels found in the specified city'}), 404
            
        # Get recommendations
        recommendations = similarity_features_only(city_df, user_features, selected_features)
        
        # Return top 10 recommendations with relevant information
        top_recommendations = recommendations.head(10)[['Hotel_Name', 'City', 'Hotel_Rating', 
                                                      'Hotel_Price', 'Similarity'] + selected_features]
        
        return jsonify(top_recommendations.to_dict('records'))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
