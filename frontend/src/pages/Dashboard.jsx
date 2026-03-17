import { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { getDashboardStats } from '../services/api'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboardStats()
      .then(res => setStats(res.data))
      .catch(() => setStats(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading dashboard...</div>
  }

  if (!stats || stats.total_reports === 0) {
    return (
      <div>
        <div className="page-header">
          <h1>Dashboard</h1>
          <p>Overview of food waste across your district</p>
        </div>
        <div className="card">
          <p>No data yet. <a href="/upload">Upload a report</a> or run the seed script to get started.</p>
        </div>
      </div>
    )
  }

  const wasteClass = stats.avg_waste_percentage < 10 ? 'low'
    : stats.avg_waste_percentage < 20 ? 'medium' : 'high'

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of food waste across your district</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="label">Schools</div>
          <div className="value">{stats.total_schools}</div>
        </div>
        <div className="stat-card">
          <div className="label">Total Reports</div>
          <div className="value">{stats.total_reports}</div>
        </div>
        <div className="stat-card">
          <div className="label">Avg Waste %</div>
          <div className={`value ${wasteClass}`}>{stats.avg_waste_percentage}%</div>
        </div>
        <div className="stat-card">
          <div className="label">Total Waste (lbs)</div>
          <div className="value">{stats.total_waste_lbs.toLocaleString()}</div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="card">
          <h2>Waste Trend Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis unit="%" />
              <Tooltip formatter={(v) => `${v}%`} />
              <Line
                type="monotone"
                dataKey="waste_percentage"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                name="Waste %"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>School Comparison</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.school_comparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="school" tick={{ fontSize: 11 }} />
              <YAxis unit="%" />
              <Tooltip formatter={(v) => `${v}%`} />
              <Bar dataKey="avg_waste_percentage" fill="#2563eb" radius={[4, 4, 0, 0]} name="Avg Waste %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
