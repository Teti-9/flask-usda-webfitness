from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from googletrans import Translator
from dotenv import load_dotenv

load_dotenv()

translator = Translator()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('secret_key')

def get_food_info(query):
    api_key = os.environ.get('API_KEY')
    base_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={query}&dataType=SR%20Legacy&pageSize=21&api_key={api_key}"
    return requests.get(base_url).json()

@app.route("/", methods=["POST", "GET"])
def main():
    food = get_food_info(request.args.get("query"))
    if request.method == "POST":
        query = request.form.get("query")
        if query is None:
            return redirect(location="/")
        else:
            trans_query = translator.translate(query, dest='en')
            if trans_query.text == 'minced meat':
                query = 'ground beef'
            else:
                query = trans_query.text
            return redirect(url_for("main", query=query))
    else:
        query = request.args.get("query")
        if query:
            if food is not None:
                foods_list = []
                if 'foods' in food:
                    for food_item in food['foods']:
                        name = translator.translate(food_item['description'], dest='pt')
                        foods = {'name': name.text,
                                'carbs': next((nutrient['value'] for nutrient in food_item['foodNutrients'] if nutrient['nutrientName'] == 'Carbohydrate, by difference'), 'N/A'),
                                'protein': next((nutrient['value'] for nutrient in food_item['foodNutrients'] if nutrient['nutrientName'] == 'Protein'), 'N/A'),
                                'fat': next((nutrient['value'] for nutrient in food_item['foodNutrients'] if nutrient['nutrientName'] == 'Total lipid (fat)'), 'N/A'),
                                'fibers': next((nutrient['value'] for nutrient in food_item['foodNutrients'] if nutrient['nutrientName'] == 'Fiber, total dietary'), 'N/A')}
                        foods_list.append(foods)
                return render_template("d.html", foods_list=foods_list, food=food)
            else:
                return render_template("d.html", food=food)
        else:
            return render_template("d.html", food=food)

if __name__ == '__main__':
    app.run(debug=True)