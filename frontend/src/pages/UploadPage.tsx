import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'
import { familiesAPI, type Family, type FamilyMember } from '../api/families'

export default function UploadPage() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
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
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
      setUploadStatus('idle')
      setError('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) { setError('Please select a file'); return }
    if (!selectedMemberId) { setError('Please select a family member'); return }

    setUploading(true)
    setUploadStatus('uploading')
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('family_member_id', selectedMemberId)

      await apiClient.post('/uploads', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      setUploadStatus('success')
    } catch (err: unknown) {
      setUploadStatus('error')
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(message || 'Upload failed')
    } finally {
      setUploading(false)
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
              <label style={labelStyle}>PDF File</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                style={{ ...inputStyle, cursor: 'pointer' }}
              />
              {file && <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#9ca3af' }}>Selected: {file.name}</p>}
            </div>

            {error && (
              <div style={{ padding: '1rem', backgroundColor: '#7f1d1d', color: '#fca5a5', borderRadius: '0.375rem' }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={!file || uploading || !selectedMemberId}
              style={{ width: '100%', padding: '0.625rem', backgroundColor: (!file || uploading || !selectedMemberId) ? '#374151' : '#2563eb', color: '#ffffff', borderRadius: '0.375rem', border: 'none', cursor: (!file || uploading || !selectedMemberId) ? 'not-allowed' : 'pointer', fontWeight: 500 }}
            >
              {uploading ? 'Uploading...' : 'Upload PDF'}
            </button>
          </form>

          {uploadStatus === 'success' && (
            <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#14532d', borderRadius: '0.375rem', color: '#86efac' }}>
              <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>Upload Successful!</h3>
              <p>Your lab report has been uploaded and queued for extraction.</p>
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
