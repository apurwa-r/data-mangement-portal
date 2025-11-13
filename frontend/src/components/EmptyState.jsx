import React from 'react'

function EmptyState({ hasFilters }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">🔍</div>
      <h3 className="empty-state-title">
        {hasFilters ? 'No projects found' : 'Start searching'}
      </h3>
      <p className="empty-state-message">
        {hasFilters 
          ? 'Try adjusting your search or filters to find what you\'re looking for.'
          : 'Use the search bar and filters above to find EPAR projects and resources.'
        }
      </p>
    </div>
  )
}

export default EmptyState

