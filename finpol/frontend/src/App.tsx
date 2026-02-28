import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import ComplianceView from './pages/ComplianceView'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/compliance" element={<ComplianceView />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
