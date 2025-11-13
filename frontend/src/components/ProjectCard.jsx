import React from 'react'

const getFileIcon = (fileType) => {
  switch (fileType) {
    case 'pdf':
      return '📄'
    case 'xlsx':
      return '📊'
    case 'docx':
      return '📝'
    default:
      return '📎'
  }
}

function ProjectCard({ project, onDownload }) {
  return (
    <div className="project-card">
      <div className="project-header">
        <div className="project-code">{project.projectCode}</div>
        <h2 className="project-title">{project.title}</h2>
      </div>

      <div className="project-meta">
        <div className="meta-item">
          <span className="meta-label">PO Contact</span>
          <span className="meta-value">{project.poContact}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Output Type</span>
          <span className="meta-value">{project.outputType}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Completed</span>
          <span className="meta-value">
            {new Date(project.dateCompletion).toLocaleDateString('en-US', { 
              month: 'short', 
              year: 'numeric' 
            })}
          </span>
        </div>
        {project.agdevPartner && (
          <div className="meta-item">
            <span className="meta-label">Partner</span>
            <span className="meta-value">{project.agdevPartner}</span>
          </div>
        )}
      </div>

      <div className="project-tags">
        {project.researchAreas.map((area, index) => (
          <span key={index} className="tag">{area}</span>
        ))}
        {project.geographies.map((geo, index) => (
          <span key={index} className="tag geography">{geo}</span>
        ))}
      </div>

      <div className="files-section">
        <div className="files-header">
          Files ({project.files.length})
        </div>
        <div className="files-list">
          {project.files.map((file) => (
            <div key={file.id} className="file-item">
              <div className="file-info">
                <span className="file-icon">{getFileIcon(file.type)}</span>
                <div className="file-details">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{file.size}</span>
                </div>
              </div>
              <button 
                className="download-btn"
                onClick={() => onDownload(file.id, file.name)}
                aria-label={`Download ${file.name}`}
              >
                Download
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ProjectCard

