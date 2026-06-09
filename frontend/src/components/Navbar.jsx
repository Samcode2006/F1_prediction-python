import { NavLink } from 'react-router-dom'
import logo from '../assets/Formula_1_Logo_4.svg'
import './Navbar.css'

const links = [
  { to: '/',        label: 'Dashboard' },
  { to: '/predict', label: 'Predict' },
  { to: '/races',   label: 'Race History' },
  { to: '/compare', label: 'Compare' },
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
          {links.map(l => (
            <li key={l.to}>
              <NavLink
                to={l.to}
                className={({ isActive }) =>
                  'navbar-link' + (isActive ? ' navbar-link--active' : '')
                }
                end={l.to === '/'}
              >
                {l.label}
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="navbar-badge">
          <span className="pulse" />
          Live Data
        </div>
      </div>
    </nav>
  )
}
