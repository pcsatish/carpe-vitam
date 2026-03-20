import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'

export default function UploadPage() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [familyMemberId, setFamilyMemberId] = useState('test-member')
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [error, setError] = useState('')
  const [extractedResults, setExtractedResults] = useState<any[]>([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
      setUploadStatus('idle')
      setError('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setUploadStatus('uploading')
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('family_member_id', familyMemberId)

      const response = await apiClient.post('/uploads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadStatus('success')
      setExtractedResults([
        {
          id: response.data.lab_report_id,
          filename: file.name,
          status: response.data.extraction_status,
        },
      ])
    } catch (err: any) {
      setUploadStatus('error')
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Upload Lab Report</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:underline"
          >
            Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PDF File
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              {file && <p className="mt-2 text-sm text-gray-600">Selected: {file.name}</p>}
            </div>

            {/* Family Member (Hardcoded for MVP) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                For: Myself (MVP)
              </label>
              <input
                type="hidden"
                value={familyMemberId}
                onChange={(e) => setFamilyMemberId(e.target.value)}
              />
              <p className="text-sm text-gray-600">
                In future versions, you'll be able to select different family members.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-100 text-red-700 rounded">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            >
              {uploading ? 'Uploading...' : 'Upload PDF'}
            </button>
          </form>

          {/* Upload Status */}
          {uploadStatus === 'success' && (
            <div className="mt-8 p-4 bg-green-100 text-green-700 rounded">
              <h3 className="font-bold mb-2">Upload Successful!</h3>
              <p>Your lab report has been uploaded and queued for extraction.</p>
              <div className="mt-4">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  Return to Dashboard
                </button>
              </div>
            </div>
          )}

          {uploadStatus === 'error' && error && (
            <div className="mt-8 p-4 bg-red-100 text-red-700 rounded">
              <h3 className="font-bold mb-2">Upload Failed</h3>
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Info Box */}
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
