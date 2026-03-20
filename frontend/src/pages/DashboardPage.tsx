import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Carpe Vitam</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">Welcome, {user?.display_name || user?.email}</span>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Upload Lab Report</h2>
            <p className="text-gray-600 mb-4">
              Upload a PDF lab report to extract and visualize test results.
            </p>
            <button
              onClick={() => navigate('/upload')}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Go to Upload
            </button>
          </div>

          {/* Chart Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">View Results</h2>
            <p className="text-gray-600 mb-4">
              View your lab results as interactive time-series charts.
            </p>
            <button
              disabled
              className="bg-gray-400 text-white px-4 py-2 rounded-md cursor-not-allowed"
            >
              View Charts (Coming Soon)
            </button>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-bold text-blue-900 mb-2">MVP Version</h3>
          <p className="text-blue-800">
            This is the MVP version of Carpe Vitam. Currently, you can upload lab PDFs and view extracted results.
            Full family management and advanced charting coming in Phase 2.
          </p>
        </div>
      </main>
    </div>
  )
}
