import React, { useState } from 'react'

function SearchBar({ searchQuery, onSearch }) {
  const [localQuery, setLocalQuery] = useState(searchQuery)

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch(localQuery)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="search-box">
      <input
        type="text"
        className="search-input"
        placeholder="Search by project code, title, research area, geography, or contact..."
        value={localQuery}
        onChange={(e) => setLocalQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        aria-label="Search projects"
      />
      <button type="submit" className="search-btn">
        Search
      </button>
    </form>
  )
}

export default SearchBar

