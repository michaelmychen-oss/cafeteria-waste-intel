import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Reports from './pages/Reports'
import Schools from './pages/Schools'

function App() {
  return (
    <div className="app-layout">
      <nav className="sidebar">
        <h1>Food Waste Intelligence</h1>
        <p className="sidebar-subtitle">School Cafeteria Analytics</p>
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/upload">Upload Report</NavLink>
        <NavLink to="/reports">Reports</NavLink>
        <NavLink to="/schools">Schools</NavLink>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/schools" element={<Schools />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
