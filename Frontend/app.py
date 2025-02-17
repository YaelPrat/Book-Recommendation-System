from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)

API_URL = 'http://localhost:5001'


@app.route('/')
def home():
    user_id = 'a1n1yemti9dj86'  # Example user_id;
    response = requests.get(f'{API_URL}/user/{user_id}/home')
    if response.status_code == 200:
        data = response.json()
        user_rated_books = data['rated_books']
        recommended_books = data['recommended_books']
        recommended_books = recommended_books[:4]

        print(recommended_books)
        return render_template('home.html', user_rated_books=user_rated_books, recommended_books=recommended_books)
    else:
        return "Failed to load data", response.status_code


# TODO : Search? display by ganere? display by recommended to the user?
# TODO :  How many to load each time? and how to handle it


@app.route('/explore')
def explore():
    response = requests.get(f'{API_URL}/explore')
    if response.status_code == 200:
        books = response.json()
        return render_template('explore.html', books=books)
    else:
        return "Failed to load explore data", response.status_code


@app.route('/book/<title>', methods=['GET', 'POST'])
def book(title):
    if request.method == 'POST':
        user_id = 'a1n1yemti9dj86'
        rating = request.form.get('rating')
        response = requests.post(f'{API_URL}/user/{user_id}/rate', json={'title': title, 'rating': rating})
        if response.status_code == 200:
            return redirect(url_for('home'))
        else:
            return "Failed to save rating", response.status_code

    response = requests.get(f'{API_URL}/book/{title}')
    if response.status_code == 200:
        book = response.json()
        return render_template('book.html', book=book)
    else:
        return "Failed to load data", response.status_code


if __name__ == '__main__':
    app.run(debug=True)
