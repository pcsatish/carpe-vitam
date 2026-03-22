import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { familiesAPI, type Family, type FamilyMember } from '../api/families'
import { resultsAPI, type TimeSeriesSeries } from '../api/results'
import AnalyteCard from '../components/dashboard/AnalyteCard'
import AnalyteDetailModal from '../components/dashboard/AnalyteDetailModal'
import ManageMembersPanel from '../components/dashboard/ManageMembersPanel'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const [families, setFamilies] = useState<Family[]>([])
  const [selectedFamilyId, setSelectedFamilyId] = useState('')
  const [members, setMembers] = useState<FamilyMember[]>([])
  const [selectedMemberId, setSelectedMemberId] = useState('')

  const [allSeries, setAllSeries] = useState<TimeSeriesSeries[]>([])
  const [loadingChart, setLoadingChart] = useState(false)
  const [selectedSeries, setSelectedSeries] = useState<TimeSeriesSeries | null>(null)

  const currentUserIsAdmin = members.some(
    (m) => m.user_id === user?.id && m.role === 'admin'
  )

  const grouped = allSeries.reduce<Record<string, TimeSeriesSeries[]>>((acc, s) => {
    const cat = s.category ?? 'Other'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(s)
    return acc
  }, {})

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  useEffect(() => {
    familiesAPI.listFamilies().then((data) => {
      setFamilies(data)
      if (data.length > 0) setSelectedFamilyId(data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!selectedFamilyId) {
      setMembers([])
      setSelectedMemberId('')
      setAllSeries([])
      return
    }
    familiesAPI.listMembers(selectedFamilyId).then((data) => {
      setMembers(data)
      if (data.length > 0) setSelectedMemberId(data[0].id)
      else setSelectedMemberId('')
    })
  }, [selectedFamilyId])

  useEffect(() => {
    if (!selectedMemberId) {
      setAllSeries([])
      return
    }
    setLoadingChart(true)
    resultsAPI.getTimeSeries(selectedMemberId)
      .then((data) => setAllSeries(data.series))
      .catch(() => setAllSeries([]))
      .finally(() => setLoadingChart(false))
  }, [selectedMemberId])

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#030712' }}>
      <header style={{ backgroundColor: '#111827', borderBottom: '1px solid #1f2937' }}>
        <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '1.5rem 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, color: '#ffffff' }}>Carpe Vitam</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ color: '#d1d5db' }}>Welcome, {user?.display_name || user?.email}</span>
            <button
              onClick={handleLogout}
              style={{ backgroundColor: '#dc2626', color: '#ffffff', padding: '0.5rem 1rem', borderRadius: '0.375rem', border: 'none', cursor: 'pointer' }}
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main style={{ maxWidth: '80rem', margin: '0 auto', padding: '2rem 1rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Actions row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
          <div style={{ backgroundColor: '#111827', borderRadius: '0.75rem', padding: '1.5rem', border: '1px solid #1f2937' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: '#ffffff' }}>Upload Lab Report</h2>
            <p style={{ color: '#9ca3af', marginBottom: '1rem' }}>
              Upload a PDF lab report to extract and visualize test results.
            </p>
            <button
              onClick={() => navigate('/upload')}
              style={{ backgroundColor: '#2563eb', color: '#ffffff', padding: '0.5rem 1rem', borderRadius: '0.375rem', border: 'none', cursor: 'pointer' }}
            >
              Go to Upload
            </button>
          </div>

          {/* Family/member selector */}
          <div style={{ backgroundColor: '#111827', borderRadius: '0.75rem', padding: '1.5rem', border: '1px solid #1f2937' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: '#ffffff' }}>View Results For</h2>
            {families.length === 0 ? (
              <div style={{ fontSize: '0.875rem', color: '#6b7280', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                <p style={{ margin: 0 }}>You're not part of any family yet.</p>
                <p style={{ margin: 0 }}>Create one below, or ask your family admin to add you by email.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#9ca3af', marginBottom: '0.25rem' }}>Family</label>
                  <select
                    value={selectedFamilyId}
                    onChange={(e) => setSelectedFamilyId(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', fontSize: '0.875rem', color: '#ffffff' }}
                  >
                    {families.map((f) => (
                      <option key={f.id} value={f.id}>{f.name}</option>
                    ))}
                  </select>
                </div>
                {members.length > 0 && (
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#9ca3af', marginBottom: '0.25rem' }}>Member</label>
                    <select
                      value={selectedMemberId}
                      onChange={(e) => setSelectedMemberId(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', fontSize: '0.875rem', color: '#ffffff' }}
                    >
                      {members.map((m) => (
                        <option key={m.id} value={m.id}>{m.display_name}</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Manage members (admin only) */}
        {currentUserIsAdmin && selectedFamilyId && (
          <ManageMembersPanel
            familyId={selectedFamilyId}
            members={members}
            onMemberAdded={(newMember) => setMembers((prev) => [...prev, newMember])}
          />
        )}

        {/* Results */}
        {loadingChart && (
          <div style={{ backgroundColor: '#111827', borderRadius: '0.75rem', padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
            Loading results...
          </div>
        )}
        {!loadingChart && allSeries.length === 0 && selectedMemberId && (
          <div style={{ backgroundColor: '#111827', borderRadius: '0.75rem', padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
            No results found for this member.
          </div>
        )}
        {!loadingChart && Object.entries(grouped).map(([category, series]) => (
          <div key={category}>
            <h3 style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#9ca3af', marginBottom: '0.75rem' }}>
              {category}
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem' }}>
              {series.map((s) => <AnalyteCard key={s.analyte_id} series={s} onClick={() => setSelectedSeries(s)} />)}
            </div>
          </div>
        ))}
      </main>

      {selectedSeries && (
        <AnalyteDetailModal series={selectedSeries} onClose={() => setSelectedSeries(null)} />
      )}
    </div>
  )
}
