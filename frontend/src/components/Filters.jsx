import React from 'react'

function Filters({ filters, filterOptions, onFilterChange }) {
  const handleMultiSelectChange = (filterName, value) => {
    const currentValues = filters[filterName]
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value]
    
    onFilterChange({
      ...filters,
      [filterName]: newValues
    })
  }

  return (
    <div className="filters-section">
      <div className="filter-group">
        <label className="filter-label">Research Areas</label>
        <select 
          className="filter-select"
          onChange={(e) => handleMultiSelectChange('researchAreas', e.target.value)}
          value=""
          aria-label="Filter by research area"
        >
          <option value="">Select research area...</option>
          {filterOptions.researchAreas.map((area) => (
            <option key={area} value={area}>
              {area} {filters.researchAreas.includes(area) ? '✓' : ''}
            </option>
          ))}
        </select>
        {filters.researchAreas.length > 0 && (
          <div style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
            Selected: {filters.researchAreas.join(', ')}
          </div>
        )}
      </div>

      <div className="filter-group">
        <label className="filter-label">Geographies</label>
        <select 
          className="filter-select"
          onChange={(e) => handleMultiSelectChange('geographies', e.target.value)}
          value=""
          aria-label="Filter by geography"
        >
          <option value="">Select geography...</option>
          {filterOptions.geographies.map((geo) => (
            <option key={geo} value={geo}>
              {geo} {filters.geographies.includes(geo) ? '✓' : ''}
            </option>
          ))}
        </select>
        {filters.geographies.length > 0 && (
          <div style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
            Selected: {filters.geographies.join(', ')}
          </div>
        )}
      </div>

      <div className="filter-group">
        <label className="filter-label">Output Type</label>
        <select 
          className="filter-select"
          onChange={(e) => handleMultiSelectChange('outputTypes', e.target.value)}
          value=""
          aria-label="Filter by output type"
        >
          <option value="">Select output type...</option>
          {filterOptions.outputTypes.map((type) => (
            <option key={type} value={type}>
              {type} {filters.outputTypes.includes(type) ? '✓' : ''}
            </option>
          ))}
        </select>
        {filters.outputTypes.length > 0 && (
          <div style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
            Selected: {filters.outputTypes.join(', ')}
          </div>
        )}
      </div>

      <div className="filter-group">
        <label className="filter-label">PO Contact</label>
        <select 
          className="filter-select"
          onChange={(e) => handleMultiSelectChange('poContacts', e.target.value)}
          value=""
          aria-label="Filter by PO contact"
        >
          <option value="">Select PO contact...</option>
          {filterOptions.poContacts.map((contact) => (
            <option key={contact} value={contact}>
              {contact} {filters.poContacts.includes(contact) ? '✓' : ''}
            </option>
          ))}
        </select>
        {filters.poContacts.length > 0 && (
          <div style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>
            Selected: {filters.poContacts.join(', ')}
          </div>
        )}
      </div>
    </div>
  )
}

export default Filters

