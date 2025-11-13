import React, { useEffect } from 'react'

function HelpModal({ isOpen, onClose }) {
  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>About EPAR Data Portal</h2>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close help">
            ✕
          </button>
        </div>

        <div className="modal-body">
          <section className="help-section">
            <h3>What is this portal?</h3>
            <p>
              The EPAR Data Portal provides access to research reports, data analysis, policy briefs, 
              and technical resources produced by the Evans School Policy Analysis & Research (EPAR) 
              group at the University of Washington for the Bill & Melinda Gates Foundation.
            </p>
          </section>

          <section className="help-section">
            <h3>How to use the portal</h3>
            <ol className="help-list">
              <li>
                <strong>Search:</strong> Use the search bar to find projects by project code, title, 
                research area, geography, or contact person.
              </li>
              <li>
                <strong>Filter:</strong> Use the filter dropdowns to narrow results by:
                <ul>
                  <li>Research Areas (Agricultural Economics, Food Security, etc.)</li>
                  <li>Geographies (Kenya, Tanzania, Uganda, etc.)</li>
                  <li>Output Type (Final Report, Policy Brief, etc.)</li>
                  <li>PO Contact (Project Officer)</li>
                </ul>
              </li>
              <li>
                <strong>Multi-select:</strong> You can select multiple options in each filter. 
                Click the same option again to deselect it.
              </li>
              <li>
                <strong>Download:</strong> Click the download button next to any file to download it.
              </li>
              <li>
                <strong>Clear filters:</strong> Click "Clear all filters" to reset your search.
              </li>
            </ol>
          </section>

          <section className="help-section">
            <h3>Available Resources</h3>
            <p>The portal contains:</p>
            <ul className="help-list">
              <li>Final research reports (PDF)</li>
              <li>Data analysis files (Excel)</li>
              <li>Policy briefs and technical notes (PDF, Word)</li>
              <li>Survey results and field data</li>
              <li>Methodology documentation</li>
            </ul>
          </section>

          <section className="help-section">
            <h3>Need Help?</h3>
            <p>
              For questions or technical support, please contact:<br />
              <strong>EPAR Team</strong><br />
              Email: <a href="mailto:epar@uw.edu" className="help-link">epar@uw.edu</a><br />
              Website: <a href="https://epar.evans.uw.edu" target="_blank" rel="noopener noreferrer" className="help-link">
                epar.evans.uw.edu
              </a>
            </p>
          </section>
        </div>

        <div className="modal-footer">
          <button className="modal-btn-primary" onClick={onClose}>
            Got it
          </button>
        </div>
      </div>
    </div>
  )
}

export default HelpModal

