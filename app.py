# ========================================================================
#   SALES + MARKETING FORECAST - BACKEND SERVER (app.py)
# ========================================================================
#   A Flask application serving front-end static assets and handling:
#   1. `/api/trends` - Sending current macro-economic indices & platform trend lists.
#   2. `/api/forecast` - Orchestrating the 5-step analysis pipeline via core_pipeline.py.
# ========================================================================

from flask import Flask, render_template, request

# Initialize the Flask application
app = Flask(__name__)

# Route 1: The Home Page (GET request)
@app.route('/')
def home():
    # This tells Flask to look inside the templates folder and serve this HTML file
    return render_template('index.html')

# Route 2: The Submission Catcher (POST request)
@app.route('/submit', methods=['POST'])
def submit():
    # Here we extract the data the user typed into the form
    business_field = request.form.get('business_field')
    core_problem = request.form.get('core_problem')
    target_audience = request.form.get('target_audience')

    # For now, we will just print it to the terminal to prove it works!
    print(f"Field: {business_field}")
    print(f"Problem: {core_problem}")
    print(f"Audience: {target_audience}")

    return "Success! Check your terminal to see the captured data. (We will make a real results page later)."

# This line actually runs the server
if __name__ == '__main__':
    app.run(debug=True)