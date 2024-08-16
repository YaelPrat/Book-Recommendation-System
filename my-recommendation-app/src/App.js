// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import Home from './components/Home';
import Explore from './components/Explore';
import Book from './components/Book';
import './index.css';

const App = () => {
  const userId = 'a0134066213wyqxltvgyt'; // Hardcoded for now

  return (
    <Router>
      <div>
        <Header userId={userId} />
        <Routes>
          <Route path="/user/:userId/home" element={<Home userId={userId} />} />
          <Route path="/user/:userId/explore" element={<Explore userId={userId} />} />
          <Route path="/user/:userId/book/:title" element={<Book userId={userId} />} />
          {/* Now the Explore component will handle search results as well */}
          <Route path="/search" element={<Explore userId={userId} />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
