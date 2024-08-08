// src/components/Explore.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import getImageSrc from '../utils/getImageSrc';

const Explore = ({ userId }) => {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    axios.get('/explore')
      .then(response => {
        setBooks(response.data);
      })
      .catch(error => {
        console.error("There was an error fetching the data!", error);
      });
  }, []);

 const formatAuthors = (authors) => {
  if (typeof authors === 'string') {
    return authors.replace(/[\[\]'"]+/g, '').trim();
  }
  return 'Unknown';
};

  return (
    <section>
      <h2>Explore More Books</h2>
      <div className="book-cards">
        {books.map(book => (
          <div className="book-card" key={book._id}>
            <h3>{book.Title}</h3>
            <p>Authors: {formatAuthors(book.authors) || 'Unknown'}</p>
            <p>Categories: {book.categories || 'Uncategorized'}</p>
            <p>Published Date: {book.publishedDate || 'Unknown'}</p>
            <img
              src={getImageSrc(book.image)}
              alt={`${book.Title} cover`}
            />
            <p>Description</p>
            <p className="book-description">{book.description || 'No description available'}</p>
            <p>Publisher: {book.publisher || 'Unknown'}</p>
            <Link to={`/user/${userId}/book/${book.Title}`}>Rate this book</Link>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Explore;
