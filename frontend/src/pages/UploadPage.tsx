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

  // Family/member selection
  const [families, setFamilies] = useState<Family[]>([])
  const [selectedFamilyId, setSelectedFamilyId] = useState('')
  const [members, setMembers] = useState<FamilyMember[]>([])
  const [selectedMemberId, setSelectedMemberId] = useState('')
  const [loadingFamilies, setLoadingFamilies] = useState(true)
  const [familiesError, setFamiliesError] = useState('')

  // Create-family inline form
  const [showCreateFamily, setShowCreateFamily] = useState(false)
  const [newFamilyName, setNewFamilyName] = useState('')
  const [creatingFamily, setCreatingFamily] = useState(false)

  useEffect(() => {
    familiesAPI.listFamilies().then(
      (data) => {
        console.log('Families loaded:', data)
        setFamilies(data)
        if (data.length > 0) setSelectedFamilyId(data[0].id)
      }
    ).catch(
      (err) => {
        const msg = err?.response?.data?.detail || err?.message || 'Unknown error'
        console.error('Failed to load families:', msg)
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

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Upload Lab Report</h1>
          <button onClick={() => navigate('/dashboard')} className="text-blue-600 hover:underline">
            Back to Dashboard
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <form onSubmit={handleSubmit} className="space-y-6">

            {/* Family selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Family</label>
              {familiesError && (
                <div className="mb-3 p-3 bg-red-100 text-red-700 text-sm rounded">
                  Error loading families: {familiesError}
                </div>
              )}
              {loadingFamilies ? (
                <p className="text-sm text-gray-500">Loading families...</p>
              ) : families.length === 0 ? (
                <p className="text-sm text-gray-500">No families yet.</p>
              ) : (
                <select
                  value={selectedFamilyId}
                  onChange={(e) => setSelectedFamilyId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
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
                  className="mt-2 text-sm text-blue-600 hover:underline"
                >
                  + Create new family
                </button>
              ) : (
                <div className="mt-2 flex gap-2">
                  <input
                    type="text"
                    value={newFamilyName}
                    onChange={(e) => setNewFamilyName(e.target.value)}
                    placeholder="Family name"
                    className="flex-1 px-3 py-1 border border-gray-300 rounded-md text-sm"
                  />
                  <button
                    type="button"
                    onClick={handleCreateFamily}
                    disabled={creatingFamily}
                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {creatingFamily ? 'Creating...' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateFamily(false)}
                    className="px-3 py-1 text-sm text-gray-600 hover:underline"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>

            {/* Member selector */}
            {selectedFamilyId && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">For</label>
                {members.length === 0 ? (
                  <p className="text-sm text-gray-500">No members in this family.</p>
                ) : (
                  <select
                    value={selectedMemberId}
                    onChange={(e) => setSelectedMemberId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
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
              <label className="block text-sm font-medium text-gray-700 mb-2">PDF File</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              {file && <p className="mt-2 text-sm text-gray-600">Selected: {file.name}</p>}
            </div>

            {error && <div className="p-4 bg-red-100 text-red-700 rounded">{error}</div>}

            <button
              type="submit"
              disabled={!file || uploading || !selectedMemberId}
              className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            >
              {uploading ? 'Uploading...' : 'Upload PDF'}
            </button>
          </form>

          {uploadStatus === 'success' && (
            <div className="mt-8 p-4 bg-green-100 text-green-700 rounded">
              <h3 className="font-bold mb-2">Upload Successful!</h3>
              <p>Your lab report has been uploaded and queued for extraction.</p>
              <button
                onClick={() => navigate('/dashboard')}
                className="mt-4 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                Return to Dashboard
              </button>
            </div>
          )}
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-bold text-blue-900 mb-2">Supported Formats</h3>
          <p className="text-blue-800">
            Currently, we support PDF lab reports from various sources. The system will automatically
            extract test results and map them to standard categories.
          </p>
        </div>
      </main>
    </div>
  )
}
