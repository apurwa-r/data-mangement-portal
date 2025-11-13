import React, { useState, useEffect } from 'react'
import { filterOptions } from '../mockData'
import ProjectCard from './ProjectCard'
import SearchBar from './SearchBar'
import Filters from './Filters'
import EmptyState from './EmptyState'

const API_BASE_URL = 'http://localhost:7071/api'

function MainPortal({ userName, onSignOut, onOpenHelp, onSwitchToUploader }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    researchAreas: [],
    geographies: [],
    outputTypes: [],
    poContacts: [],
    dateFrom: '',
    dateTo: ''
  })
  const [currentPage, setCurrentPage] = useState(1)
  const [hasSearched, setHasSearched] = useState(false)
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const resultsPerPage = 10

  // Fetch projects from backend API
  useEffect(() => {
    if (!hasSearched) return

    const fetchProjects = async () => {
      setLoading(true)
      setError(null)

      try {
        // Build query parameters
        const params = new URLSearchParams()

        if (searchQuery.trim()) {
          params.append('q', searchQuery.trim())
        }

        if (filters.researchAreas.length > 0) {
          params.append('researchAreas', filters.researchAreas.join(','))
        }

        if (filters.geographies.length > 0) {
          params.append('geographies', filters.geographies.join(','))
        }

        if (filters.outputTypes.length > 0) {
          params.append('outputTypes', filters.outputTypes.join(','))
        }

        if (filters.poContacts.length > 0) {
          params.append('poContacts', filters.poContacts.join(','))
        }

        // Call backend API
        const response = await fetch(`${API_BASE_URL}/search?${params.toString()}`)

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        const data = await response.json()
        setProjects(data.results || [])
      } catch (err) {
        console.error('Error fetching projects:', err)
        setError('Failed to load projects. Please try again.')
        setProjects([])
      } finally {
        setLoading(false)
      }
    }

    fetchProjects()
  }, [searchQuery, filters, hasSearched])

  // Pagination
  const totalPages = Math.ceil(projects.length / resultsPerPage)
  const startIndex = (currentPage - 1) * resultsPerPage
  const endIndex = startIndex + resultsPerPage
  const currentProjects = projects.slice(startIndex, endIndex)

  const handleSearch = (query) => {
    setSearchQuery(query)
    setCurrentPage(1)
    setHasSearched(true)
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
    setCurrentPage(1)
    setHasSearched(true)
  }

  const handleClearFilters = () => {
    setSearchQuery('')
    setFilters({
      researchAreas: [],
      geographies: [],
      outputTypes: [],
      poContacts: [],
      dateFrom: '',
      dateTo: ''
    })
    setCurrentPage(1)
    setHasSearched(false)
    setProjects([])
  }

  const handleDownload = async (fileId, fileName) => {
    try {
      // Call backend download API
      const response = await fetch(`${API_BASE_URL}/download?fileId=${fileId}`)

      if (!response.ok) {
        throw new Error(`Download API error: ${response.status}`)
      }

      const data = await response.json()

      // Check if we're in mock mode
      if (data.mode === 'mock') {
        // Mock mode: Show message instead of downloading
        alert(
          `📁 File: ${fileName}\n\n` +
          `ℹ️ Download feature is in MOCK MODE\n\n` +
          `Azure Storage is not configured. This will work automatically when you:\n` +
          `1. Create Azure Storage account\n` +
          `2. Update BLOB_CONN in .env.dev\n` +
          `3. Restart the backend\n\n` +
          `No code changes needed!`
        )
      } else {
        // Real Azure mode: Open download URL
        window.open(data.download_url, '_blank')
      }
    } catch (err) {
      console.error('Error downloading file:', err)
      alert(`Failed to download ${fileName}. Please try again.`)
    }
  }

  const hasActiveFilters = searchQuery ||
    filters.researchAreas.length > 0 ||
    filters.geographies.length > 0 ||
    filters.outputTypes.length > 0 ||
    filters.poContacts.length > 0

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div>
            <h1>EPAR Data Portal</h1>
            <p className="header-subtitle">
              Evans School Policy Analysis & Research - University of Washington
            </p>
          </div>
          <div className="header-actions">
            <span className="user-welcome">Welcome, {userName}</span>
            <button className="header-btn" onClick={onSwitchToUploader}>
              Upload Portal
            </button>
            <button className="header-btn" onClick={onOpenHelp}>
              Help
            </button>
            <button className="header-btn-secondary" onClick={onSignOut}>
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Search Section */}
        <div className="search-section">
          <SearchBar
            searchQuery={searchQuery}
            onSearch={handleSearch}
          />
          <Filters
            filters={filters}
            filterOptions={filterOptions}
            onFilterChange={handleFilterChange}
          />
        </div>

        {/* Results Section */}
        <div className="results-section">
          {hasSearched ? (
            <>
              {loading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Loading projects...</p>
                </div>
              ) : error ? (
                <div className="error-state">
                  <p className="error-message">{error}</p>
                  <button className="retry-btn" onClick={() => setHasSearched(true)}>
                    Retry
                  </button>
                </div>
              ) : (
                <>
                  <div className="results-header">
                    <div className="results-count">
                      {projects.length} {projects.length === 1 ? 'project' : 'projects'} found
                    </div>
                    {hasActiveFilters && (
                      <button className="clear-filters-btn" onClick={handleClearFilters}>
                        Clear all filters
                      </button>
                    )}
                  </div>

                  {currentProjects.length > 0 ? (
                    <>
                      <div className="projects-list">
                        {currentProjects.map(project => (
                          <ProjectCard
                            key={project.id}
                            project={project}
                            onDownload={handleDownload}
                          />
                        ))}
                      </div>

                      {/* Pagination */}
                      {totalPages > 1 && (
                        <div className="pagination">
                          <button
                            className="pagination-btn"
                            onClick={() => setCurrentPage(p => p - 1)}
                            disabled={currentPage === 1}
                          >
                            Previous
                          </button>
                          <span className="pagination-info">
                            Page {currentPage} of {totalPages}
                          </span>
                          <button
                            className="pagination-btn"
                            onClick={() => setCurrentPage(p => p + 1)}
                            disabled={currentPage === totalPages}
                          >
                            Next
                          </button>
                        </div>
                      )}
                    </>
                  ) : (
                    <EmptyState hasFilters={hasActiveFilters} />
                  )}
                </>
              )}
            </>
          ) : (
            <div className="initial-state">
              <div className="initial-state-icon">🔍</div>
              <h3 className="initial-state-title">Ready to search</h3>
              <p className="initial-state-message">
                Use the search bar and filters above to find EPAR projects and resources.
              </p>
              <div className="initial-state-tips">
                <h4>Quick tips:</h4>
                <ul>
                  <li>Search by project code, title, or keywords</li>
                  <li>Use filters to narrow by research area, geography, or output type</li>
                  <li>Select multiple options in each filter for broader results</li>
                  <li>Click "Help" in the header for detailed instructions</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  )
}

export default MainPortal

