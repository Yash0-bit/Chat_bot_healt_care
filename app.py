from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import process
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from sklearn import preprocessing

app = Flask(__name__)

# Load the training data
training = pd.read_csv('C:/Users/Yash/OneDrive/Desktop/Study/Chat_bot_kratin_LLC/Data/Training.csv')
cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']

# Label encode the target variable
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)

# Train the decision tree classifier
clf = DecisionTreeClassifier()
clf.fit(x, y)

# Load symptom data and descriptions
symptom_description = pd.read_csv('C:/Users/Yash/OneDrive/Desktop/Study/Chat_bot_kratin_LLC/MasterData/symptom_Description.csv', index_col=0)
symptom_precautions = pd.read_csv('C:/Users/Yash/OneDrive/Desktop/Study/Chat_bot_kratin_LLC/MasterData/symptom_precaution.csv', index_col=0)

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
        input_vector = np.zeros(len(cols))
        input_vector[cols.get_loc(matched_symptom)] = 1
        prediction = clf.predict([input_vector])

        present_disease = le.inverse_transform(prediction)[0]
        response = f"You may have {present_disease}\n{symptom_description.loc[present_disease]}"

        second_prediction = le.inverse_transform(clf.predict([input_vector]))[0]
        if present_disease != second_prediction:
            response += f"\nYou may also have {second_prediction}\n{symptom_description.loc[second_prediction]}"

        precautions = list(symptom_precautions.loc[present_disease].dropna())
        response += "\nTake the following precautions:"
        for i, precaution in enumerate(precautions):
            response += f"\n{i + 1}) {precaution}"

        return response
    else:
        return "Enter a valid symptom."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('user_message')
    bot_response = chatbot_response(user_message)
    return jsonify({'bot_response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
