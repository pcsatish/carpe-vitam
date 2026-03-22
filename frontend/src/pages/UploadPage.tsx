import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'
import { familiesAPI, type Family, type FamilyMember } from '../api/families'

type FileStatus = 'queued' | 'uploading' | 'done' | 'needs-date' | 'error'
interface FileEntry { file: File; status: FileStatus; labReportId?: string; pendingDate: string; error?: string }

export default function UploadPage() {
  const navigate = useNavigate()
  const [files, setFiles] = useState<FileEntry[]>([])
  const [uploading, setUploading] = useState(false)
  const [allDone, setAllDone] = useState(false)
  const [error, setError] = useState('')

  const [families, setFamilies] = useState<Family[]>([])
  const [selectedFamilyId, setSelectedFamilyId] = useState('')
  const [members, setMembers] = useState<FamilyMember[]>([])
  const [selectedMemberId, setSelectedMemberId] = useState('')
  const [loadingFamilies, setLoadingFamilies] = useState(true)
  const [familiesError, setFamiliesError] = useState('')

  const [showCreateFamily, setShowCreateFamily] = useState(false)
  const [newFamilyName, setNewFamilyName] = useState('')
  const [creatingFamily, setCreatingFamily] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    familiesAPI.listFamilies().then(
      (data) => {
        setFamilies(data)
        if (data.length > 0) setSelectedFamilyId(data[0].id)
      }
    ).catch(
      (err) => {
        const msg = err?.response?.data?.detail || err?.message || 'Unknown error'
        setFamiliesError(msg)
      }
    ).finally(
      () => setLoadingFamilies(false)
    )
  }, [])

  useEffect(() => {
    if (!selectedFamilyId) {
      setMembers([])
      setSelectedMemberId('')
      return
    }
    familiesAPI.listMembers(selectedFamilyId).then((data) => {
      setMembers(data)
      if (data.length > 0) setSelectedMemberId(data[0].id)
      else setSelectedMemberId('')
    })
  }, [selectedFamilyId])

  const handleCreateFamily = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newFamilyName.trim()) return
    setCreatingFamily(true)
    try {
      const family = await familiesAPI.createFamily(newFamilyName.trim())
      const updated = [...families, family]
      setFamilies(updated)
      setSelectedFamilyId(family.id)
      setNewFamilyName('')
      setShowCreateFamily(false)
    } catch {
      setError('Failed to create family')
    } finally {
      setCreatingFamily(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const entries: FileEntry[] = Array.from(e.target.files).map((f) => ({ file: f, status: 'queued', pendingDate: '' }))
      setFiles(entries)
      setAllDone(false)
      setError('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (files.length === 0) { setError('Please select at least one file'); return }
    if (!selectedMemberId) { setError('Please select a family member'); return }

    setUploading(true)
    setError('')

    const updated = [...files]
    for (let i = 0; i < updated.length; i++) {
      updated[i] = { ...updated[i], status: 'uploading' }
      setFiles([...updated])
      try {
        const formData = new FormData()
        formData.append('file', updated[i].file)
        formData.append('family_member_id', selectedMemberId)
        const res = await apiClient.post('/uploads', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        const data = res.data as { lab_report_id: string; report_date: string | null }
        updated[i] = data.report_date
          ? { ...updated[i], status: 'done', labReportId: data.lab_report_id }
          : { ...updated[i], status: 'needs-date', labReportId: data.lab_report_id }
      } catch (err: unknown) {
        const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        updated[i] = { ...updated[i], status: 'error', error: message || 'Upload failed' }
      }
      setFiles([...updated])
    }

    setUploading(false)
    setAllDone(!updated.some(f => f.status === 'needs-date'))
  }

  const handleSetDate = async (i: number) => {
    const entry = files[i]
    if (!entry.labReportId || !entry.pendingDate) return
    try {
      await apiClient.patch(`/uploads/${entry.labReportId}/date`, { report_date: entry.pendingDate })
      const updated = [...files]
      updated[i] = { ...updated[i], status: 'done' }
      setFiles(updated)
      if (!updated.some(f => f.status === 'needs-date')) setAllDone(true)
    } catch {
      const updated = [...files]
      updated[i] = { ...updated[i], error: 'Failed to set date' }
      setFiles(updated)
    }
  }

  const inputStyle = { width: '100%', padding: '0.5rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.875rem', boxSizing: 'border-box' as const }
  const labelStyle = { display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#9ca3af', marginBottom: '0.5rem' }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#030712' }}>
      <header style={{ backgroundColor: '#111827', borderBottom: '1px solid #1f2937' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '1.5rem 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, color: '#ffffff' }}>Upload Lab Report</h1>
          <button
            onClick={() => navigate('/dashboard')}
            style={{ color: '#60a5fa', background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.875rem' }}
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      <main style={{ maxWidth: '42rem', margin: '0 auto', padding: '2rem 1rem' }}>
        <div style={{ backgroundColor: '#111827', borderRadius: '0.75rem', border: '1px solid #1f2937', padding: '2rem' }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

            {/* Family selector */}
            <div>
              <label style={labelStyle}>Family</label>
              {familiesError && (
                <div style={{ marginBottom: '0.75rem', padding: '0.75rem', backgroundColor: '#7f1d1d', color: '#fca5a5', fontSize: '0.875rem', borderRadius: '0.375rem' }}>
                  Error loading families: {familiesError}
                </div>
              )}
              {loadingFamilies ? (
                <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Loading families...</p>
              ) : families.length === 0 ? (
                <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>No families yet.</p>
              ) : (
                <select
                  value={selectedFamilyId}
                  onChange={(e) => setSelectedFamilyId(e.target.value)}
                  style={inputStyle}
                >
                  {families.map((f) => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              )}

              {!showCreateFamily ? (
                <button
                  type="button"
                  onClick={() => setShowCreateFamily(true)}
                  style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#60a5fa', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                >
                  + Create new family
                </button>
              ) : (
                <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                  <input
                    type="text"
                    value={newFamilyName}
                    onChange={(e) => setNewFamilyName(e.target.value)}
                    placeholder="Family name"
                    style={{ flex: 1, padding: '0.25rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.875rem' }}
                  />
                  <button
                    type="button"
                    onClick={handleCreateFamily}
                    disabled={creatingFamily}
                    style={{ padding: '0.25rem 0.75rem', backgroundColor: creatingFamily ? '#374151' : '#2563eb', color: '#ffffff', fontSize: '0.875rem', borderRadius: '0.375rem', border: 'none', cursor: creatingFamily ? 'not-allowed' : 'pointer' }}
                  >
                    {creatingFamily ? 'Creating...' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateFamily(false)}
                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem', color: '#9ca3af', background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>

            {/* Member selector */}
            {selectedFamilyId && (
              <div>
                <label style={labelStyle}>For</label>
                {members.length === 0 ? (
                  <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>No members in this family.</p>
                ) : (
                  <select
                    value={selectedMemberId}
                    onChange={(e) => setSelectedMemberId(e.target.value)}
                    style={inputStyle}
                  >
                    {members.map((m) => (
                      <option key={m.id} value={m.id}>{m.display_name}</option>
                    ))}
                  </select>
                )}
              </div>
            )}

            {/* File input */}
            <div>
              <label style={labelStyle}>PDF Files</label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                multiple
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                style={{ width: '100%', padding: '0.5rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: files.length > 0 ? '#ffffff' : '#6b7280', fontSize: '0.875rem', textAlign: 'left', cursor: 'pointer' }}
              >
                {files.length > 0 ? `${files.length} file${files.length > 1 ? 's' : ''} selected` : 'Choose PDF files...'}
              </button>
              {files.length > 0 && (
                <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
                  {files.map((entry, i) => {
                    const statusColor = entry.status === 'done' ? '#86efac' : entry.status === 'error' ? '#fca5a5' : entry.status === 'uploading' ? '#93c5fd' : entry.status === 'needs-date' ? '#fcd34d' : '#9ca3af'
                    const statusLabel = entry.status === 'done' ? '✓' : entry.status === 'error' ? '✗' : entry.status === 'uploading' ? '⟳' : null
                    return (
                      <div key={i} style={{ backgroundColor: '#1f2937', borderRadius: '0.375rem', padding: '0.5rem 0.75rem', display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.8rem', color: '#d1d5db', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>{entry.file.name}</span>
                          {statusLabel && <span style={{ color: statusColor, marginLeft: '0.75rem', flexShrink: 0, fontSize: '0.8rem' }}>{statusLabel}{entry.error ? ` ${entry.error}` : ''}</span>}
                          {entry.status === 'needs-date' && <span style={{ color: statusColor, marginLeft: '0.75rem', flexShrink: 0, fontSize: '0.75rem' }}>Date not found in PDF</span>}
                        </div>
                        {entry.status === 'needs-date' && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <input
                              type="date"
                              value={entry.pendingDate}
                              onChange={(e) => {
                                const updated = [...files]
                                updated[i] = { ...updated[i], pendingDate: e.target.value }
                                setFiles(updated)
                              }}
                              style={{ flex: 1, padding: '0.25rem 0.5rem', backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '0.25rem', color: '#ffffff', fontSize: '0.75rem', colorScheme: 'dark' }}
                            />
                            <button
                              type="button"
                              onClick={() => handleSetDate(i)}
                              disabled={!entry.pendingDate}
                              style={{ padding: '0.25rem 0.625rem', backgroundColor: entry.pendingDate ? '#2563eb' : '#374151', color: '#ffffff', border: 'none', borderRadius: '0.25rem', fontSize: '0.75rem', cursor: entry.pendingDate ? 'pointer' : 'not-allowed' }}
                            >
                              Set date
                            </button>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            {error && (
              <div style={{ padding: '1rem', backgroundColor: '#7f1d1d', color: '#fca5a5', borderRadius: '0.375rem' }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={files.length === 0 || uploading || !selectedMemberId}
              style={{ width: '100%', padding: '0.625rem', backgroundColor: (files.length === 0 || uploading || !selectedMemberId) ? '#374151' : '#2563eb', color: '#ffffff', borderRadius: '0.375rem', border: 'none', cursor: (files.length === 0 || uploading || !selectedMemberId) ? 'not-allowed' : 'pointer', fontWeight: 500 }}
            >
              {uploading ? 'Uploading...' : `Upload ${files.length > 1 ? `${files.length} PDFs` : 'PDF'}`}
            </button>
          </form>

          {allDone && (
            <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#14532d', borderRadius: '0.375rem', color: '#86efac' }}>
              <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>
                {files.every(f => f.status === 'done') ? 'All uploads successful!' : 'Uploads complete with some errors'}
              </h3>
              <p>{files.filter(f => f.status === 'done').length} of {files.length} file{files.length > 1 ? 's' : ''} uploaded successfully.</p>
              <button
                onClick={() => navigate('/dashboard')}
                style={{ marginTop: '1rem', padding: '0.5rem 1rem', backgroundColor: '#16a34a', color: '#ffffff', borderRadius: '0.375rem', border: 'none', cursor: 'pointer' }}
              >
                Return to Dashboard
              </button>
            </div>
          )}
        </div>

        <div style={{ marginTop: '2rem', backgroundColor: '#111827', border: '1px solid #1e3a5f', borderRadius: '0.75rem', padding: '1.5rem' }}>
          <h3 style={{ fontWeight: 700, color: '#93c5fd', marginBottom: '0.5rem' }}>Supported Formats</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Currently, we support PDF lab reports from various sources. The system will automatically
            extract test results and map them to standard categories.
          </p>
        </div>
      </main>
    </div>
  )
}
