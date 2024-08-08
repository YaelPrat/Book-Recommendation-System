// src/components/Header.js
import React from 'react';
import { Link } from 'react-router-dom';

const Header = ({ userId }) => (
  <header>
    <h1>Book Recommendation App</h1>
    <nav>
      <Link to={`/user/${userId}/home`}>Home</Link>
      <Link to={`/user/${userId}/explore`}>Explore More Books</Link>
    </nav>
  </header>
);

export default Header;
