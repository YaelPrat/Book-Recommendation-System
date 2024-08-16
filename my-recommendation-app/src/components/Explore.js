// src/components/Explore.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useLocation } from 'react-router-dom'; // Make sure Link is imported
import getImageSrc from '../utils/getImageSrc';

const Explore = ({ userId }) => {
  const [books, setBooks] = useState([]);
  const location = useLocation();

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const query = searchParams.get('query');

    // Clear books before fetching new data
    setBooks([]);

    const fetchBooks = async () => {
      try {
        const url = query ? `/search?query=${encodeURIComponent(query)}` : '/explore';
        const response = await axios.get(url);
        setBooks(response.data);  // This will replace the current state with new books
      } catch (error) {
        console.error("There was an error fetching the data!", error);
      }
    };

    fetchBooks();
  }, [location.search]);

  const formatAuthors = (authors) => {
    if (typeof authors === 'string') {
      return authors.replace(/[\[\]'"]+/g, '').trim();
    }
    return 'Unknown';
  };

  return (
    <section>
      <h2>{location.search ? `Search Results` : `Explore More Books`}</h2>
      <div className="book-cards">
        {books.map((book, index) => (
          <div className="book-card" key={book._id ? book._id : index}>
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
