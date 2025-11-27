# Calorie Tracker with Gemini Nutrition Insights

A simple web app to **log your meals** and get **daily nutrition summaries** with AI-driven suggestions for a healthier, balanced diet.

---

## Features

- **Autocomplete Dish Search**: Type any Indian dish name and get suggestions from a dataset of 250+ dishes.
- **Log Meals**: Add meals with full nutritional info automatically pulled from the dataset.
- **Daily Nutrition Summary**: View a **table of all logged meals** with total calories, protein, carbs, fats, vitamins, minerals, etc.
- **AI Diet Suggestions**: Ask Gemini AI to suggest improvements for a **balanced diet** based on your logged meals.
- **User-friendly UI**: Modern, clean table layout with total row and colored highlights.

---

## Dataset

The app uses a CSV file `dishes.csv` with columns:

- `Dish_Name`, `Calories`, `Carbohydrates`, `Protein`, `Fats`, `Free_Sugar`, `Fibre`, `Sodium`, `Calcium`, `Iron`, `VitaminC`, `Folate`

_Note_: All nutritional values are per 100g of the dish.

---

## Installation

1. Clone the repo:

```bash
git clone https://github.com/yourusername/calorie-tracker-gemini.git
cd calorie-tracker-gemini
```

### Install dependencies:

```bash
pip install flash
```

Set your Google API key:
```bash
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

or on Windows (PowerShell):
```bash
setx GOOGLE_API_KEY "YOUR_GOOGLE_API_KEY"
```
## Usage

Start the Flask server:
```bash
python app.py
```

1. Open your browser
2. Log meals using dish name autocomplete.
3. View nutrition summary and totals.
4. Click “Get Healthy Diet Suggestions” to ask Gemini AI for balanced diet tips.
