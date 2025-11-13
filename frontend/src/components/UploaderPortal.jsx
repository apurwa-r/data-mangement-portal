import { useState } from 'react'
import './UploaderPortal.css'

function UploaderPortal({ userName, onSignOut, onSwitchToDownloader }) {
  const [formData, setFormData] = useState({
    projectCode: '',
    title: '',
    researchAreas: [],
    dateInitialRequest: '',
    dateCompletion: '',
    poContact: '',
    otherPos: [],
    agdevPartner: '',
    outputType: '',
    geographies: []
  })
  
  const [files, setFiles] = useState([])
  const [isDragging, setIsDragging] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState(null) // 'success' | 'error' | null

  // Available options for multi-select fields
  const researchAreaOptions = [
    'Agricultural Economics',
    'Market Systems',
    'Food Security',
    'Rural Development',
    'Gender & Agriculture',
    'Climate & Agriculture'
  ]

  const geographyOptions = [
    'Kenya',
    'Tanzania',
    'Uganda',
    'Ethiopia',
    'Rwanda',
    'Malawi',
    'Zambia',
    'Nigeria',
    'Ghana',
    'Multi-Country'
  ]

  const outputTypeOptions = [
    'Report',
    'Dataset',
    'Brief',
    'Presentation',
    'Working Paper'
  ]

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleMultiSelectChange = (field, value) => {
    setFormData(prev => {
      const currentValues = prev[field]
      const newValues = currentValues.includes(value)
        ? currentValues.filter(v => v !== value)
        : [...currentValues, value]
      return {
        ...prev,
        [field]: newValues
      }
    })
  }

  const handleOtherPosChange = (e) => {
    const value = e.target.value
    const posList = value.split(',').map(po => po.trim()).filter(po => po)
    setFormData(prev => ({
      ...prev,
      otherPos: posList
    }))
  }

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles(prev => [...prev, ...selectedFiles])
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFiles = Array.from(e.dataTransfer.files)
    setFiles(prev => [...prev, ...droppedFiles])
  }

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitStatus(null)

    try {
      // Create FormData for file upload
      const uploadData = new FormData()
      
      // Add project metadata
      uploadData.append('projectCode', formData.projectCode)
      uploadData.append('title', formData.title)
      uploadData.append('researchAreas', JSON.stringify(formData.researchAreas))
      uploadData.append('dateInitialRequest', formData.dateInitialRequest)
      uploadData.append('dateCompletion', formData.dateCompletion)
      uploadData.append('poContact', formData.poContact)
      uploadData.append('otherPos', JSON.stringify(formData.otherPos))
      uploadData.append('agdevPartner', formData.agdevPartner)
      uploadData.append('outputType', formData.outputType)
      uploadData.append('geographies', JSON.stringify(formData.geographies))
      
      // Add files
      files.forEach((file, index) => {
        uploadData.append(`file_${index}`, file)
      })

      // Submit to backend
      const response = await fetch('http://localhost:7071/api/upload', {
        method: 'POST',
        body: uploadData
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const result = await response.json()
      console.log('Upload successful:', result)
      
      setSubmitStatus('success')
      
      // Reset form after successful upload
      setTimeout(() => {
        setFormData({
          projectCode: '',
          title: '',
          researchAreas: [],
          dateInitialRequest: '',
          dateCompletion: '',
          poContact: '',
          otherPos: [],
          agdevPartner: '',
          outputType: '',
          geographies: []
        })
        setFiles([])
        setSubmitStatus(null)
      }, 3000)

    } catch (error) {
      console.error('Upload error:', error)
      setSubmitStatus('error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="uploader-portal">
      {/* Header */}
      <header className="portal-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="portal-title">EPAR Data Portal - Upload</h1>
            <p className="portal-subtitle">Upload research outputs and datasets</p>
          </div>
          <div className="header-right">
            <button className="switch-mode-btn" onClick={onSwitchToDownloader}>
              Switch to Download Portal
            </button>
            <span className="user-name">Welcome, {userName}</span>
            <button className="sign-out-btn" onClick={onSignOut}>Sign Out</button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="uploader-main">
        <div className="uploader-container">
          <form onSubmit={handleSubmit} className="upload-form">
            
            {/* Project Information Section */}
            <section className="form-section">
              <h2 className="section-title">Project Information</h2>
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="projectCode" className="form-label">
                    Project Code <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="projectCode"
                    name="projectCode"
                    value={formData.projectCode}
                    onChange={handleInputChange}
                    placeholder="e.g., EPAR-2024-015"
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="outputType" className="form-label">
                    Type of Output <span className="required">*</span>
                  </label>
                  <select
                    id="outputType"
                    name="outputType"
                    value={formData.outputType}
                    onChange={handleInputChange}
                    className="form-select"
                    required
                  >
                    <option value="">Select type...</option>
                    {outputTypeOptions.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="title" className="form-label">
                  Project Title <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Enter project title"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Research Areas <span className="required">*</span>
                </label>
                <div className="checkbox-group">
                  {researchAreaOptions.map(area => (
                    <label key={area} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.researchAreas.includes(area)}
                        onChange={() => handleMultiSelectChange('researchAreas', area)}
                        className="checkbox-input"
                      />
                      <span>{area}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Geographies <span className="required">*</span>
                </label>
                <div className="checkbox-group">
                  {geographyOptions.map(geo => (
                    <label key={geo} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.geographies.includes(geo)}
                        onChange={() => handleMultiSelectChange('geographies', geo)}
                        className="checkbox-input"
                      />
                      <span>{geo}</span>
                    </label>
                  ))}
                </div>
              </div>
            </section>

            {/* Contact & Dates Section */}
            <section className="form-section">
              <h2 className="section-title">Contact & Timeline</h2>
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="poContact" className="form-label">
                    PO Contact <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="poContact"
                    name="poContact"
                    value={formData.poContact}
                    onChange={handleInputChange}
                    placeholder="Primary contact name"
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="agdevPartner" className="form-label">
                    AgDev Partner
                  </label>
                  <input
                    type="text"
                    id="agdevPartner"
                    name="agdevPartner"
                    value={formData.agdevPartner}
                    onChange={handleInputChange}
                    placeholder="Partner organization"
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="otherPos" className="form-label">
                  Other POs (comma-separated)
                </label>
                <input
                  type="text"
                  id="otherPos"
                  name="otherPos"
                  value={formData.otherPos.join(', ')}
                  onChange={handleOtherPosChange}
                  placeholder="e.g., Jane Doe, John Smith"
                  className="form-input"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="dateInitialRequest" className="form-label">
                    Date of Initial Request
                  </label>
                  <input
                    type="month"
                    id="dateInitialRequest"
                    name="dateInitialRequest"
                    value={formData.dateInitialRequest}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="dateCompletion" className="form-label">
                    Date of Completion <span className="required">*</span>
                  </label>
                  <input
                    type="month"
                    id="dateCompletion"
                    name="dateCompletion"
                    value={formData.dateCompletion}
                    onChange={handleInputChange}
                    className="form-input"
                    required
                  />
                </div>
              </div>
            </section>

            {/* File Upload Section */}
            <section className="form-section">
              <h2 className="section-title">Files</h2>

              <div
                className={`file-drop-zone ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="drop-zone-content">
                  <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="drop-zone-text">Drag and drop files here, or</p>
                  <label htmlFor="file-input" className="file-select-btn">
                    Browse Files
                  </label>
                  <input
                    type="file"
                    id="file-input"
                    multiple
                    onChange={handleFileSelect}
                    className="file-input-hidden"
                    accept=".pdf,.txt,.md,.docx,.xlsx"
                  />
                  <p className="drop-zone-hint">Supported: PDF, TXT, MD, DOCX, XLSX</p>
                </div>
              </div>

              {/* File List */}
              {files.length > 0 && (
                <div className="file-list">
                  <h3 className="file-list-title">Selected Files ({files.length})</h3>
                  {files.map((file, index) => (
                    <div key={index} className="file-item">
                      <div className="file-info">
                        <svg className="file-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <div className="file-details">
                          <span className="file-name">{file.name}</span>
                          <span className="file-size">{formatFileSize(file.size)}</span>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveFile(index)}
                        className="file-remove-btn"
                        aria-label="Remove file"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Submit Section */}
            <section className="form-section">
              {submitStatus === 'success' && (
                <div className="alert alert-success">
                  ✓ Project uploaded successfully!
                </div>
              )}

              {submitStatus === 'error' && (
                <div className="alert alert-error">
                  ✗ Upload failed. Please try again.
                </div>
              )}

              <div className="form-actions">
                <button
                  type="submit"
                  disabled={isSubmitting || files.length === 0}
                  className="submit-btn"
                >
                  {isSubmitting ? 'Uploading...' : 'Upload Project'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setFormData({
                      projectCode: '',
                      title: '',
                      researchAreas: [],
                      dateInitialRequest: '',
                      dateCompletion: '',
                      poContact: '',
                      otherPos: [],
                      agdevPartner: '',
                      outputType: '',
                      geographies: []
                    })
                    setFiles([])
                    setSubmitStatus(null)
                  }}
                  className="reset-btn"
                >
                  Reset Form
                </button>
              </div>
            </section>

          </form>
        </div>
      </main>
    </div>
  )
}

export default UploaderPortal

