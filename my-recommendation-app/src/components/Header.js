// src/components/Header.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import SearchBar from './SearchBar';

const Header = ({ userId }) => {
  const navigate = useNavigate();

  const handleSearch = (query) => {
    if (query) {
      navigate(`/search?query=${encodeURIComponent(query)}`);
    }
  };
  const handleExploreClick = () => {
    navigate(`/user/${userId}/explore`, { replace: true });
  };

  return (
    <header>
      <h1>Book Finder</h1>
      <nav>
        <Link to={`/user/${userId}/home`}>Home</Link>
        <Link to={`/user/${userId}/explore`} onClick={handleExploreClick}>Explore</Link>
      </nav>
      <SearchBar onSearch={handleSearch} />
    </header>
  );
};

export default Header;
