# ========================================================================
#   SALES + MARKETING FORECAST - BACKEND SERVER (app.py)
# ========================================================================
#   A Flask application serving front-end static assets and handling:
#   1. `/api/trends` - Sending current macro-economic indices & platform trend lists.
#   2. `/api/forecast` - Orchestrating the 5-step analysis pipeline via core_pipeline.py.
# ========================================================================

import os
from flask import Flask, render_template

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
