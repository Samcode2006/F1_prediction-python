import { NavLink } from 'react-router-dom'
import logo from '../assets/Formula_1_Logo_4.svg'
import './Navbar.css'
import { BrainCircuit, GitCompare, History, LayoutDashboard } from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/predict', label: 'Predict', icon: BrainCircuit },
  { to: '/races', label: 'Race History', icon: History },
  { to: '/compare', label: 'Compare', icon: GitCompare },
]

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-logo">
          <img src={logo} alt="F1 Logo" className="navbar-logo-img" />
          <span className="navbar-logo-text">Predictor</span>
        </NavLink>

        <ul className="navbar-links">
          {links.map(({ to, label, icon: Icon }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  'navbar-link' + (isActive ? ' navbar-link--active' : '')
                }
                end={to === '/'}
              >
                <Icon size={16} strokeWidth={2} aria-hidden="true" />
                <span>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

      </div>
    </nav>
  )
}
