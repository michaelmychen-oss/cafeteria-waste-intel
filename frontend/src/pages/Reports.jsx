import { useState, useEffect } from 'react'
import { getReports, getSchools } from '../services/api'

function Reports() {
  const [reports, setReports] = useState([])
  const [schools, setSchools] = useState([])
  const [schoolFilter, setSchoolFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    Promise.all([
      getReports(schoolFilter || undefined),
      getSchools(),
    ]).then(([reportsRes, schoolsRes]) => {
      setReports(reportsRes.data)
      setSchools(schoolsRes.data)
    }).finally(() => setLoading(false))
  }, [schoolFilter])

  const schoolMap = Object.fromEntries(schools.map(s => [s.id, s.name]))

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading reports...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h1>Reports</h1>
        <p>View all uploaded and processed reports</p>
      </div>

      <div className="card">
        <div style={{ marginBottom: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
          <label>Filter by school:</label>
          <select value={schoolFilter} onChange={(e) => { setSchoolFilter(e.target.value); setLoading(true) }}>
            <option value="">All Schools</option>
            {schools.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>

        {reports.length === 0 ? (
          <p>No reports found. <a href="/upload">Upload one</a> to get started.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>School</th>
                <th>File</th>
                <th>Type</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {reports.map(r => (
                <>
                  <tr key={r.id}>
                    <td>{r.id}</td>
                    <td>{schoolMap[r.school_id] || r.school_id}</td>
                    <td>{r.filename}</td>
                    <td>{r.file_type?.toUpperCase()}</td>
                    <td>
                      <span className={`badge ${r.status === 'completed' ? 'low' : r.status === 'failed' ? 'high' : 'medium'}`}>
                        {r.status}
                      </span>
                    </td>
                    <td>{new Date(r.uploaded_at).toLocaleDateString()}</td>
                    <td>
                      {r.ai_analysis && (
                        <button
                          className="btn"
                          style={{ padding: '4px 12px', fontSize: 12 }}
                          onClick={() => setExpandedId(expandedId === r.id ? null : r.id)}
                        >
                          {expandedId === r.id ? 'Hide' : 'View'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {expandedId === r.id && r.ai_analysis && (
                    <tr key={`${r.id}-detail`}>
                      <td colSpan={7} style={{ background: 'var(--gray-50)' }}>
                        <ReportDetail analysis={JSON.parse(r.ai_analysis)} extracted={r.extracted_data ? JSON.parse(r.extracted_data) : null} />
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

function ReportDetail({ analysis, extracted }) {
  return (
    <div style={{ padding: 12 }}>
      <h3>Waste Level: <span className={`badge ${analysis.waste_level}`}>{analysis.waste_level}</span></h3>
      {analysis.key_findings && (
        <div style={{ marginTop: 12 }}>
          <strong>Key Findings:</strong>
          <ul style={{ marginLeft: 20, marginTop: 4 }}>
            {analysis.key_findings.map((f, i) => <li key={i}>{f}</li>)}
          </ul>
        </div>
      )}
      {analysis.recommendations && (
        <div style={{ marginTop: 12 }}>
          <strong>Recommendations:</strong>
          <ul className="rec-list" style={{ marginTop: 4 }}>
            {analysis.recommendations.map((r, i) => (
              <li key={i}>{typeof r === 'object' ? r.action : r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default Reports
