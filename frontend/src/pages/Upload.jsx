import { useState, useEffect, useRef, useCallback } from 'react'
import { getSchools, uploadReport } from '../services/api'

function Upload() {
  const [schools, setSchools] = useState([])
  const [schoolId, setSchoolId] = useState('')
  const [file, setFile] = useState(null)
  const [dragover, setDragover] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef()

  useEffect(() => {
    getSchools().then(res => {
      setSchools(res.data)
      if (res.data.length > 0) setSchoolId(res.data[0].id)
    })
  }, [])

  const handleFile = (f) => {
    const allowed = ['pdf', 'csv', 'xlsx', 'xls', 'png', 'jpg', 'jpeg']
    const ext = f.name.split('.').pop().toLowerCase()
    if (!allowed.includes(ext)) {
      setError(`File type .${ext} not supported. Use: ${allowed.join(', ')}`)
      return
    }
    setFile(f)
    setError(null)
    setResult(null)
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragover(false)
    if (e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleSubmit = async () => {
    if (!file || !schoolId) return
    setUploading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('school_id', schoolId)

    try {
      const res = await uploadReport(formData)
      setResult(res.data)
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Upload Report</h1>
        <p>Upload a cafeteria report for AI-powered waste analysis</p>
      </div>

      <div className="card">
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="school-select">School</label>
          <select
            id="school-select"
            value={schoolId}
            onChange={(e) => setSchoolId(e.target.value)}
            style={{ width: '100%', marginTop: 4 }}
          >
            {schools.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        <div
          className={`upload-zone ${dragover ? 'dragover' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragover(true) }}
          onDragLeave={() => setDragover(false)}
          onDrop={handleDrop}
        >
          <div className="icon">+</div>
          {file ? (
            <p><strong>{file.name}</strong> ({(file.size / 1024).toFixed(1)} KB)</p>
          ) : (
            <>
              <p><strong>Click or drag a file here</strong></p>
              <p>PDF, CSV, Excel, or Image</p>
            </>
          )}
          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".pdf,.csv,.xlsx,.xls,.png,.jpg,.jpeg"
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
          />
        </div>

        <div style={{ marginTop: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={!file || !schoolId || uploading}
          >
            {uploading ? 'Analyzing...' : 'Upload & Analyze'}
          </button>
          {uploading && <div className="spinner" />}
        </div>

        {error && (
          <div style={{ marginTop: 16, padding: 12, background: '#fee2e2', borderRadius: 8, color: '#991b1b', fontSize: 14 }}>
            {error}
          </div>
        )}
      </div>

      {result && <AnalysisResult result={result} />}
    </div>
  )
}

function AnalysisResult({ result }) {
  return (
    <div>
      <div className="card">
        <h2>Analysis Results</h2>
        <div className="stats-grid" style={{ marginBottom: 0 }}>
          <div className="stat-card">
            <div className="label">Waste Level</div>
            <div className={`value ${result.waste_level}`}>
              {result.waste_level.toUpperCase()}
            </div>
          </div>
          <div className="stat-card">
            <div className="label">Waste Percentage</div>
            <div className={`value ${result.waste_level}`}>
              {result.waste_percentage}%
            </div>
          </div>
        </div>
      </div>

      {result.drivers.length > 0 && (
        <div className="card">
          <h2>Waste Drivers</h2>
          <ul className="rec-list driver-list">
            {result.drivers.map((d, i) => (
              <li key={i}>{typeof d === 'object' ? d.driver : d}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="card">
        <h2>Recommendations</h2>
        <ul className="rec-list">
          {result.recommendations.map((r, i) => (
            <li key={i}>{typeof r === 'object' ? r.action : r}</li>
          ))}
        </ul>
      </div>

      {result.menu_items.length > 0 && (
        <div className="card">
          <h2>Extracted Menu Items</h2>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Category</th>
                  <th>Prepared</th>
                  <th>Served</th>
                  <th>Wasted</th>
                  <th>Waste %</th>
                </tr>
              </thead>
              <tbody>
                {result.menu_items.map((item, i) => {
                  const wastePct = item.servings_prepared > 0
                    ? ((item.servings_wasted / item.servings_prepared) * 100).toFixed(1)
                    : '—'
                  const cls = wastePct > 30 ? 'high' : wastePct > 15 ? 'medium' : 'low'
                  return (
                    <tr key={i}>
                      <td>{item.name}</td>
                      <td>{item.category || '—'}</td>
                      <td>{item.servings_prepared ?? '—'}</td>
                      <td>{item.servings_served ?? '—'}</td>
                      <td>{item.servings_wasted ?? '—'}</td>
                      <td><span className={`badge ${cls}`}>{wastePct}%</span></td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Upload
