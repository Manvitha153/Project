from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# ✅ Load the trained model
model = joblib.load("risk_model.pkl")  # Ensure this file exists

@app.route('/', methods=["GET", "POST"])  # Single route handles everything
def index():
    if request.method == "POST":
        try:
            form = request.form
            input_data = pd.DataFrame([{
                "avg_speed": float(form.get("avg_speed", 0)),
                "max_speed": float(form.get("max_speed", 0)),
                "braking_events": int(form.get("braking_events", 0)),
                "acceleration_events": int(form.get("acceleration_events", 0)),
                "night_driving": int(form.get("night_driving", 0)),
                "phone_usage": int(form.get("phone_usage", 0)),
                "trip_duration": float(form.get("trip_duration", 0))
            }])

            # Predict risk category
            prediction = model.predict(input_data)[0]
            risk_class = "Risky" if prediction == 1 else "Safe"

            # Risk score formula
            risk_score = (
                (input_data['max_speed'][0] / 180) * 0.4 +
                (input_data['braking_events'][0] / 15) * 0.2 +
                (input_data['acceleration_events'][0] / 15) * 0.1 +
                input_data['night_driving'][0] * 0.15 +
                input_data['phone_usage'][0] * 0.15
            ) * 100

            # Premium calculation
            base_premium = 5000
            premium = round(base_premium * (1 + (risk_score / 100) * 0.5))

            # Recommendations
            recommendations = []
            if input_data['max_speed'][0] > 120:
                recommendations.append("Consider maintaining legal speed limits.")
            if input_data['braking_events'][0] > 4:
                recommendations.append("Smooth braking improves safety and fuel efficiency.")
            if input_data['acceleration_events'][0] > 5:
                recommendations.append("Avoid aggressive acceleration.")
            if input_data['night_driving'][0] == 1:
                recommendations.append("Be cautious while driving at night.")
            if input_data['phone_usage'][0] == 1:
                recommendations.append("Avoid phone usage while driving.")

            if not recommendations:
                recommendations.append("Excellent driving behavior observed. Keep it up!")

            return render_template(
                "index.html",
                prediction=risk_class,
                risk_score=round(risk_score),
                premium=premium,
                recommendations=recommendations
            )

        except Exception as e:
            return f"<h3>Error: {e}</h3>"

    return render_template("index.html")

if __name__ == '__main__':
    print("🚀 Flask server started on http://127.0.0.1:5000")
    app.run(debug=True)
