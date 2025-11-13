import { useState } from 'react'
import './App.css'
import SignInPage from './components/SignInPage'
import MainPortal from './components/MainPortal'
import UploaderPortal from './components/UploaderPortal'
import HelpModal from './components/HelpModal'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userName, setUserName] = useState('')
  const [isHelpOpen, setIsHelpOpen] = useState(false)
  const [mode, setMode] = useState('downloader') // 'downloader' | 'uploader'

  const handleSignIn = () => {
    // Mock authentication - in real implementation, this will use Microsoft OAuth
    // For now, simulate successful sign-in
    setUserName('John Smith') // Mock user name
    setIsAuthenticated(true)
  }

  const handleSignOut = () => {
    setIsAuthenticated(false)
    setUserName('')
    setMode('downloader') // Reset to downloader mode on sign out
  }

  const handleOpenHelp = () => {
    setIsHelpOpen(true)
  }

  const handleCloseHelp = () => {
    setIsHelpOpen(false)
  }

  const handleSwitchToUploader = () => {
    setMode('uploader')
  }

  const handleSwitchToDownloader = () => {
    setMode('downloader')
  }

  return (
    <div className="app">
      {!isAuthenticated ? (
        // Page 1: Sign-In Page
        <SignInPage onSignIn={handleSignIn} />
      ) : (
        // Page 2: Main Portal (after authentication)
        <>
          {mode === 'downloader' ? (
            <MainPortal
              userName={userName}
              onSignOut={handleSignOut}
              onOpenHelp={handleOpenHelp}
              onSwitchToUploader={handleSwitchToUploader}
            />
          ) : (
            <UploaderPortal
              userName={userName}
              onSignOut={handleSignOut}
              onSwitchToDownloader={handleSwitchToDownloader}
            />
          )}

          {/* Footer - Only show for downloader mode */}
          {mode === 'downloader' && (
            <footer className="footer">
              <div className="footer-content">
                <div className="footer-links">
                  <a href="https://epar.evans.uw.edu" target="_blank" rel="noopener noreferrer" className="footer-link">
                    About EPAR
                  </a>
                  <a href="#" className="footer-link">Contact</a>
                  <a href="#" className="footer-link" onClick={(e) => { e.preventDefault(); handleOpenHelp(); }}>
                    Help
                  </a>
                </div>
                <p>&copy; 2024 Evans School Policy Analysis & Research, University of Washington</p>
              </div>
            </footer>
          )}

          {/* Help Modal */}
          <HelpModal isOpen={isHelpOpen} onClose={handleCloseHelp} />
        </>
      )}
    </div>
  )
}

export default App
