import { NavLink } from 'react-router-dom'
import { Moon, Sun } from 'lucide-react'
import { useEffect, useState } from 'react'
import logo from '../assets/Formula_1_Logo_4.svg'
import './Navbar.css'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/predict', label: 'Predict' },
  { to: '/races', label: 'Race History' },
  { to: '/compare', label: 'Compare' },
]

export default function Navbar() {
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('f1-theme') === 'dark')

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light'
    localStorage.setItem('f1-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-logo">
          <img src={logo} alt="F1 Logo" className="navbar-logo-img" />
          <span className="navbar-logo-text">Predictor</span>
        </NavLink>

        <ul className="navbar-links">
          {links.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  'navbar-link' + (isActive ? ' navbar-link--active' : '')
                }
                end={to === '/'}
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>

        <button
          type="button"
          className="theme-toggle"
          onClick={() => setDarkMode(current => !current)}
          aria-label={darkMode ? 'Switch to light theme' : 'Switch to dark theme'}
          title={darkMode ? 'Switch to light theme' : 'Switch to dark theme'}
        >
          {darkMode ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}
        </button>

      </div>
    </nav>
  )
}
