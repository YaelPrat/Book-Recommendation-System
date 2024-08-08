// src/components/Book.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const Book = ({ userId }) => {
    const { title } = useParams();
    const [book, setBook] = useState(null);
    const [rating, setRating] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        fetch(`/book/${title}`)
            .then(response => response.json())
            .then(data => setBook(data));
    }, [title]);

    const handleSubmit = (e) => {
        e.preventDefault();
        fetch(`/user/${userId}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, rating }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Rating saved successfully') {
                navigate(`/user/${userId}/home`); // Redirect to home page after successful rating
            } else {
                console.error('Failed to submit rating');
            }
        })
        .catch(error => {
            console.error('Failed to submit rating', error);
        });
    };

    if (!book) {
        return <div>Loading...</div>;
    }

    return (
        <section>
            <h3>{book.Title}</h3>
            <p>Authors: {book.authors || 'Unknown'}</p>
            <p>Categories: {book.categories || 'Uncategorized'}</p>
            <p>Published Date: {book.publishedDate || 'Unknown'}</p>
            <img src={book.image || '/default_book_cover.jpg'} alt={`${book.Title} cover`} />
            <p>Description: {book.description || 'No description available'}</p>
            <p>Publisher: {book.publisher || 'Unknown'}</p>
            <p>Ratings Count: {book.ratingsCount || 'Not rated'}</p>
            <a href={book.infoLink} target="_blank" rel="noopener noreferrer">More Info</a>
            <a href={book.previewLink} target="_blank" rel="noopener noreferrer">Preview</a>
            <form onSubmit={handleSubmit}>
                <label htmlFor="rating">Rate this book:</label>
                <input
                    type="number"
                    id="rating"
                    name="rating"
                    min="1"
                    max="5"
                    value={rating}
                    onChange={(e) => setRating(e.target.value)}
                    required
                />
                <button type="submit">Submit</button>
            </form>
        </section>
    );
};

export default Book;
