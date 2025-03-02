from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect, url_for
import sqlite3  # Using SQLite for simplicity
import numpy as np
import pickle

# Load trained model 
with open('Breast_cancer_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

app = Flask(__name__, static_url_path='/static')

@app.route("/")
def home():
    return jsonify({"message": "Flask App on Vercel!"})

# Export the app for Vercel
def handler(event, context):
    return app(event, context)

# Create Feedback Table (Run this once in Python shell)
def init_db():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        navigation INTEGER,
                        design TEXT,
                        design_suggestions TEXT,
                        useful TEXT,
                        accuracy INTEGER,
                        trust TEXT,
                        features TEXT,
                        chatbot TEXT,
                        general_feedback TEXT
                    )''')
    conn.commit()
    conn.close()

# Call init_db() when the app starts
init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/prevention')
def prevention():
    return render_template('prevention.html')

@app.route('/precautions')
def precautions():
    return render_template('precautions.html')

@app.route('/check_risk')
def check_risk():
    return render_template("check_risk.html")

@app.route('/contact')
def contact():
    return render_template('contact.html')

# @app.route('/feedback')
# def feedback():
#     return render_template('feedback.html')

# Home Route for Feedback Page
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Get Form Data
        navigation = request.form.get('navigation')
        design = request.form.get('design')
        design_suggestions = request.form.get('design_suggestions')
        useful = request.form.get('useful')
        accuracy = request.form.get('accuracy')
        trust = request.form.get('trust')
        features = request.form.get('features')
        chatbot = request.form.get('chatbot')
        general_feedback = request.form.get('general_feedback')

        # Store in Database
        conn = sqlite3.connect("feedback.db")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO feedback (navigation, design, design_suggestions, useful, 
                        accuracy, trust, features, chatbot, general_feedback)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (navigation, design, design_suggestions, useful, accuracy, trust, features, chatbot, general_feedback))
        conn.commit()
        conn.close()

        return redirect(url_for('thank_you'))  # Redirect to Thank You Page

    return render_template('feedback.html')

# Thank You Page
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')


# ✅ Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # List of all 30 features expected by the model
        feature_names = [
            'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean', 
            'compactness_mean', 'concavity_mean', 'concave_points_mean', 'symmetry_mean', 'fractal_dimension_mean',
            'radius_se', 'texture_se', 'perimeter_se', 'area_se', 'smoothness_se', 
            'compactness_se', 'concavity_se', 'concave_points_se', 'symmetry_se', 'fractal_dimension_se',
            'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst', 'smoothness_worst', 
            'compactness_worst', 'concavity_worst', 'concave_points_worst', 'symmetry_worst', 'fractal_dimension_worst'
        ]

        # Extract and validate user input
        input_features = []
        for feature in feature_names:
            value = request.form.get(feature, "").strip()  # Get input and remove extra spaces
            if value == " ":  
                return render_template('check_risk.html', prediction_text="⚠️ Error: All fields are required.")
            
            input_features.append(float(value))  # Convert to float
            
        # Convert input to numpy array and reshape
        input_array = np.array(input_features).reshape(1, -1)

        # Make predictions
        prediction = model.predict(input_array)
        
        # Map prediction result
        result = "Malignant (Cancerous)" if prediction[0] == 1 else "Benign (Non-Cancerous)"

        # Return only the result on a blank screen
        return f"<h2>The tumor is: {result}</h2>"
    
    except ValueError:
        return render_template('check_risk.html', prediction_text="⚠️ Error: Please enter valid numbers in all fields.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

