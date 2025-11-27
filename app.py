from flask import Flask, render_template, request, jsonify, flash
import pandas as pd
import json
import re
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from datetime import date

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------- Dataset ----------
df = pd.read_csv("dishes.csv")
df.columns = df.columns.str.strip()  # remove extra spaces

# ---------- Gemini API ----------
os.environ["GOOGLE_API_KEY"] = "AIzaSyCmOim5Aq_b3Mthu99GaCsczoY4DuPjAO0"
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
prompt_template = ChatPromptTemplate.from_template("""
You are a Nutrition Insights AI Assistant.

You analyze meals and their nutritional content. Generate clear, friendly, and actionable insights for a normal user.

Return JSON with:
- "summary": 50-word explanation of the meal's nutrition.
- "key_nutrients": List nutrients that stand out (high/low).
- "tips": Practical guidance to balance this meal.
- "warnings": Optional warnings (high sugar, sodium, fats).

User Input:
{input_text}
""")
chain = prompt_template | llm | StrOutputParser()

# ---------- Log file ----------
DATA_FILE = "calorie_log.json"

# ---------- Helpers ----------
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_dish_suggestions(query):
    query_lower = query.lower()
    matches = df[df["Dish_Name"].str.lower().str.contains(query_lower)]
    return matches.head(5)["Dish_Name"].tolist()

def get_nutrition(dish_name):
    row = df[df["Dish_Name"].str.lower() == dish_name.lower()]
    if row.empty:
        return None
    nutrition = row.iloc[0].to_dict()
    # Fill missing values with 0
    for k, v in nutrition.items():
        if pd.isna(v):
            nutrition[k] = 0
    return nutrition

def extract_information(user_query: str):
    result = chain.invoke({"input_text": user_query})
    return result

def extract_fields(raw_response: str):
    fields = {"summary": "", "key_nutrients": [], "tips": "", "warnings": ""}
    patterns = {
        "summary": r'"summary"\s*:\s*"(.*?)"',
        "key_nutrients": r'"key_nutrients"\s*:\s*\[(.*?)\]',
        "tips": r'"tips"\s*:\s*"(.*?)"',
        "warnings": r'"warnings"\s*:\s*"(.*?)"'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_response, re.DOTALL)
        if match:
            value = match.group(1).strip()
            if key == "key_nutrients":
                # Convert comma-separated string to list
                value = [x.strip().strip('"') for x in value.split(',') if x.strip()]
            fields[key] = value
    return fields

# ---------- Routes ----------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("q", "")
    suggestions = get_dish_suggestions(query)
    return jsonify(suggestions)

@app.route("/log_meal", methods=["POST"])
def log_meal():
    dish_name = request.form.get("dish_name")
    nutrition = get_nutrition(dish_name)
    if not nutrition:
        flash("Dish not found!", "error")
        return render_template("index.html")

    today = str(date.today())
    data = load_data()
    if today not in data:
        data[today] = []
    data[today].append(nutrition)
    save_data(data)
    flash(f"{dish_name} logged successfully!", "success")
    return render_template("index.html")

@app.route("/insights")
def insights():
    data = load_data()
    today = str(date.today())
    if today not in data or len(data[today]) == 0:
        flash("No meals logged today!", "info")
        return render_template("index.html")

    # Normalize keys and compute totals
    required_keys = ["Dish_Name","Calories","Carbohydrates","Protein","Fats",
                     "Free_Sugar","Fibre","Sodium","Calcium","Iron","VitaminC","Folate"]
    meals = []
    totals = {k: 0 for k in required_keys if k != "Dish_Name"}

    for m in data[today]:
        meal = {}
        for k in required_keys:
            meal[k] = m.get(k, 0)
            if k != "Dish_Name":
                try:
                    totals[k] += float(meal[k])
                except:
                    totals[k] += 0
        meals.append(meal)

    return render_template("insights.html", meals=meals, totals=totals)

@app.route("/gemini_advice", methods=["POST"])
def gemini_advice():
    data = load_data()
    today = str(date.today())
    if today not in data or len(data[today]) == 0:
        flash("No meals logged today!", "info")
        return render_template("index.html")

    required_keys = ["Dish_Name","Calories","Carbohydrates","Protein","Fats",
                     "Free_Sugar","Fibre","Sodium","Calcium","Iron","VitaminC","Folate"]
    meals = []
    for m in data[today]:
        meal = {}
        for k in required_keys:
            meal[k] = m.get(k, 0)
        meals.append(meal)

    # Prepare summary for Gemini
    meals_summary = "\n".join([
        f"{m['Dish_Name']}: {m['Calories']} kcal, {m['Protein']}g protein, {m['Fats']}g fat, {m['Carbohydrates']}g carbs"
        for m in meals
    ])

    try:
        raw_response = extract_information(meals_summary)
        try:
            advice_json = json.loads(raw_response)
        except json.JSONDecodeError:
            advice_json = extract_fields(raw_response)
    except Exception:
        advice_json = {
            "summary": "Could not get AI advice.",
            "key_nutrients": [],
            "tips": "",
            "warnings": ""
        }

    # Also pass meals and totals so we can render the table again
    totals = {k: sum(float(m[k]) for m in meals) for k in required_keys if k != "Dish_Name"}
    return render_template("insights.html", meals=meals, totals=totals, gemini_advice=advice_json)


if __name__ == "__main__":
    app.run(debug=True)
