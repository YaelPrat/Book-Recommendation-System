// src/utils/getImageSrc.js
const getImageSrc = (bookImage) => {
  if (bookImage === '/static/default_book_cover.jpg') {
    return '/default_book_cover.jpg';
  }
  return bookImage;
};

export default getImageSrc;
