// src/components/Home.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Home = ({ userId }) => {
  const [userRatedBooks, setUserRatedBooks] = useState([]);
  const [recommendedBooks, setRecommendedBooks] = useState([]);
  const [displayedRecommendations, setDisplayedRecommendations] = useState([]);

  useEffect(() => {
    axios.get(`/user/${userId}/home`)
      .then(response => {
//        console.log('Response data:', response.data);
        setUserRatedBooks(response.data.rated_books || []);
        setRecommendedBooks(response.data.recommended_books || []);
        setDisplayedRecommendations(response.data.recommended_books.slice(0, 4) || []);

      })
      .catch(error => {
        console.error("There was an error fetching the data!", error);
      });
  }, [userId]);
 const formatAuthors = (authors) => {
  if (typeof authors === 'string') {
    return authors.replace(/[\[\]'"]+/g, '').trim();
  }
  return 'Unknown';
};
  return (
    <section className="card-container">
      <div className="card">
        <h2>Your Rated Books</h2>
        <div className="books-container">
          <ul>
            {userRatedBooks.length > 0 ? userRatedBooks.map((book, index) => (
              <li key={index}>{book.title} by {book.author} - Rating: {book.rating}</li>
            )) : <li>No rated books available.</li>}
          </ul>
        </div>
      </div>
      <div className="card">
        <h2>Recommended for You</h2>
        <div className="book-cards">
          {displayedRecommendations.length > 0 ? displayedRecommendations.map((book, index) => (
            <div className="book-card" key={index}>
              <h3>{book.Title}</h3>
              <p>{formatAuthors(book.authors)}</p>
              <img src={book.image} alt={book.Title} />
              <p  className="book-description">{book.description}</p>
              <a href={book.infoLink} target="_blank" rel="noopener noreferrer">More Info</a>
              <a href={book.previewLink} target="_blank" rel="noopener noreferrer">Preview</a>
            <Link to={`/user/${userId}/book/${book.Title}`}>Rate this book</Link>
            </div>
          )) : <div>No recommendations available.</div>}
        </div>
      </div>
    </section>
  );
};

export default Home;
