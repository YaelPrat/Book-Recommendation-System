// src/components/SearchResult.js
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

const SearchResult = () => {
  const location = useLocation();
  const [books, setBooks] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const queryParam = searchParams.get('query');
    setQuery(queryParam);

    const fetchBooks = async () => {
      if (queryParam) {
        try {
          const response = await fetch(`http://localhost:5001/search?query=${encodeURIComponent(queryParam)}`);
          const data = await response.json();
          setBooks(data);
        } catch (error) {
          console.error('Error fetching search results:', error);
        }
      }
    };

    fetchBooks();
  }, [location.search]);

  return (
    <div>
      <h2>Search Results for "{query}"</h2>
    </div>
  );
};

export default SearchResult;
