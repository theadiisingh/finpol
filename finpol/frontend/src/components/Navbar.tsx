import { Link, useLocation } from 'react-router-dom'
import { Shield, Home, CreditCard, FileCheck } from 'lucide-react'

function Navbar() {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/transactions', label: 'Transactions', icon: CreditCard },
    { path: '/compliance', label: 'Compliance', icon: FileCheck },
  ]

  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">FinPol</span>
          </Link>

          <div className="flex space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium ${
                  location.pathname === item.path
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
