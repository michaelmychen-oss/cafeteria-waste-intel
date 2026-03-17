import { useState, useEffect } from 'react'
import { getSchools, createSchool, getSchoolTrend } from '../services/api'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'

function Schools() {
  const [schools, setSchools] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ name: '', district: '', address: '', student_count: '' })
  const [trendSchoolId, setTrendSchoolId] = useState(null)
  const [trendData, setTrendData] = useState([])

  const loadSchools = () => {
    getSchools()
      .then(res => setSchools(res.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadSchools() }, [])

  useEffect(() => {
    if (trendSchoolId) {
      getSchoolTrend(trendSchoolId).then(res => setTrendData(res.data))
    }
  }, [trendSchoolId])

  const handleAdd = async (e) => {
    e.preventDefault()
    await createSchool({
      ...form,
      student_count: form.student_count ? parseInt(form.student_count) : null,
    })
    setForm({ name: '', district: '', address: '', student_count: '' })
    setShowAdd(false)
    loadSchools()
  }

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading schools...</div>
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Schools</h1>
          <p>Manage schools in your district</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? 'Cancel' : '+ Add School'}
        </button>
      </div>

      {showAdd && (
        <div className="card">
          <h2>Add New School</h2>
          <form onSubmit={handleAdd} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label>School Name *</label>
              <input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} style={{ width: '100%' }} />
            </div>
            <div>
              <label>District</label>
              <input value={form.district} onChange={e => setForm({ ...form, district: e.target.value })} style={{ width: '100%' }} />
            </div>
            <div>
              <label>Address</label>
              <input value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} style={{ width: '100%' }} />
            </div>
            <div>
              <label>Student Count</label>
              <input type="number" value={form.student_count} onChange={e => setForm({ ...form, student_count: e.target.value })} style={{ width: '100%' }} />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <button className="btn btn-primary" type="submit">Save School</button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>District</th>
              <th>Students</th>
              <th>Address</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            {schools.map(s => (
              <tr key={s.id}>
                <td><strong>{s.name}</strong></td>
                <td>{s.district || '—'}</td>
                <td>{s.student_count?.toLocaleString() || '—'}</td>
                <td>{s.address || '—'}</td>
                <td>
                  <button
                    className="btn"
                    style={{ padding: '4px 12px', fontSize: 12 }}
                    onClick={() => setTrendSchoolId(trendSchoolId === s.id ? null : s.id)}
                  >
                    {trendSchoolId === s.id ? 'Hide' : 'View Trend'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {trendSchoolId && trendData.length > 0 && (
        <div className="card">
          <h2>Waste Trend: {schools.find(s => s.id === trendSchoolId)?.name}</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis unit="%" />
              <Tooltip formatter={(v) => `${v}%`} />
              <Line type="monotone" dataKey="waste_percentage" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} name="Waste %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default Schools
