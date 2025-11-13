import React from 'react'

function SignInPage({ onSignIn }) {
  return (
    <div className="signin-page">
      <div className="signin-container">
        <div className="signin-content">
          {/* EPAR Logo/Branding */}
          <div className="signin-branding">
            <div className="epar-logo">
              <div className="logo-circle">EPAR</div>
            </div>
            <h1 className="signin-title">EPAR Data Portal</h1>
            <p className="signin-subtitle">
              Evans School Policy Analysis & Research
            </p>
            <p className="signin-tagline">
              Access research reports, data analysis, and policy resources
            </p>
          </div>

          {/* Sign-In Button */}
          <div className="signin-action">
            <button className="microsoft-signin-btn" onClick={onSignIn}>
              <svg className="microsoft-icon" viewBox="0 0 23 23" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="11" height="11" fill="#F25022"/>
                <rect x="12" width="11" height="11" fill="#7FBA00"/>
                <rect y="12" width="11" height="11" fill="#00A4EF"/>
                <rect x="12" y="12" width="11" height="11" fill="#FFB900"/>
              </svg>
              Sign in with Microsoft
            </button>
            <p className="signin-note">
              University of Washington credentials required
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="signin-footer">
          <a href="https://epar.evans.uw.edu" target="_blank" rel="noopener noreferrer" className="signin-link">
            About EPAR
          </a>
          <span className="signin-separator">•</span>
          <a href="#" className="signin-link">Contact</a>
          <span className="signin-separator">•</span>
          <a href="#" className="signin-link">Help</a>
        </div>
      </div>
    </div>
  )
}

export default SignInPage

