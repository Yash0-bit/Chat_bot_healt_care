from flask import Flask, render_template, request, jsonify

app = Flask("Chatbot_K_LLC")

# Add your Healthcare ChatBot model and functions here
import pandas as pd
from fuzzywuzzy import process
from sklearn.tree import DecisionTreeClassifier
import numpy as np

# Load the training data
training = pd.read_csv('C:/Users/Yash/Downloads/healthcare-chatbot-master/Data/Training.csv')
cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']

# Label encode the target variable
from sklearn import preprocessing
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)

# Train the decision tree classifier
clf = DecisionTreeClassifier()
clf.fit(x, y)

# Load symptom data and descriptions
symptom_description = pd.read_csv('C:/Users/Yash/Downloads/healthcare-chatbot-master/MasterData/symptom_Description.csv', index_col=0)
symptom_precautions = pd.read_csv('C:/Users/Yash/Downloads/healthcare-chatbot-master/MasterData/symptom_precaution.csv', index_col=0)

def fuzzy_match_symptom(input_symptom):
    # Use fuzzy matching to find the closest matching symptom
    choices = cols
    best_match, score = process.extractOne(input_symptom, choices)
    if score >= 80:  # You can adjust the matching threshold as needed
        return best_match
    else:
        return None

def chatbot_response(user_message):
    matched_symptom = fuzzy_match_symptom(user_message)

    if matched_symptom:
        num_days = 1  # Default value, you can modify this

        input_vector = np.zeros(len(cols))
        input_vector[cols.get_loc(matched_symptom)] = 1
        prediction = clf.predict([input_vector])

        present_disease = le.inverse_transform(prediction)[0]

        symptoms_given = list(symptom_precautions.columns[symptom_precautions.loc[present_disease].notna()])
        symptoms_exp = [symptom for symptom in symptoms_given if user_message.lower() == 'yes']

        second_prediction = le.inverse_transform(clf.predict([input_vector]))[0]
        if present_disease != second_prediction:
            return f"You may also have {second_prediction}\n{symptom_description.loc[second_prediction]}"
        else:
            return f"You may have {present_disease}\n{symptom_description.loc[present_disease]}"
    else:
        return "Enter a valid symptom."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('user_message')
    bot_response = chatbot_response(user_message)
    return jsonify({'bot_response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
