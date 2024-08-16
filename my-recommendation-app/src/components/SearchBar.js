// src/components/SearchBar.js
import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSearch = (event) => {
    event.preventDefault();
    onSearch(query);
    setQuery('');
  };

  return (
    <form onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center' }}>
      <input
        type="text"
        placeholder="Search book by title or author"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{ padding: '5px', width: '200px' }}
      />
      <button type="submit" style={{ padding: '5px 10px', marginLeft: '5px' }}>Search</button>
    </form>
  );
};

export default SearchBar;
