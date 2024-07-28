from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# Simulated data
user_rated_books = [
    {"title": "Book 1", "author": "Author 1", "rating": 5},
    {"title": "Book 2", "author": "Author 2", "rating": 4}
]

recommended_books = [
    {"title": "Book 3", "author": "Author 3"},
    {"title": "Book 4", "author": "Author 4"}
]

all_books = [
    {"title": "Book 1", "author": "Author 1"},
    {"title": "Book 2", "author": "Author 2"},
    {"title": "Book 3", "author": "Author 3"},
    {"title": "Book 4", "author": "Author 4"}
]

# TODO : load the data from the DB & predict from the model
@app.route('/')
def home():
    return render_template('home.html', user_rated_books=user_rated_books, recommended_books=recommended_books)

#TODO : Search? dispaly by ganere? display by recommended to the user?
# TODO :  How many to load each time? and how to handle it
# TODO: load the data from the DB
@app.route('/explore')
def explore():
    return render_template('explore.html', books=all_books)

#TODO: Add review field
#TODO : save the data in the backend
@app.route('/book/<title>', methods=['GET', 'POST'])
@app.route('/book/<title>', methods=['GET', 'POST'])
def book(title):
    book = next((book for book in all_books if book["title"] == title), None)
    if request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        # Here, you would save the rating and review to the database
        return redirect(url_for('home'))
    return render_template('book.html', book=book)

if __name__ == '__main__':
    app.run(debug=True)
