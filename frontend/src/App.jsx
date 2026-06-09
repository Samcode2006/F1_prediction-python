import { Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Predict from './pages/Predict'
import RaceHistory from './pages/RaceHistory'
import RaceDetail from './pages/RaceDetail'
import DriverCompare from './pages/DriverCompare'

export default function App() {
  const location = useLocation()

  return (
    <>
      <Navbar />
      <main key={location.pathname} className="page-enter">
        <Routes>
          <Route path="/"              element={<Dashboard />} />
          <Route path="/predict"       element={<Predict />} />
          <Route path="/races"         element={<RaceHistory />} />
          <Route path="/races/:year/:round" element={<RaceDetail />} />
          <Route path="/compare"       element={<DriverCompare />} />
        </Routes>
      </main>
    </>
  )
}
