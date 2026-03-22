import { useState } from 'react'
import { familiesAPI, type FamilyMember } from '../../api/families'

interface Props {
  familyId: string
  members: FamilyMember[]
  onMemberAdded: (member: FamilyMember) => void
}

export default function ManageMembersPanel({ familyId, members, onMemberAdded }: Props) {
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [adding, setAdding] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!displayName.trim()) return
    setAdding(true)
    setError('')
    setSuccess('')
    try {
      const member = await familiesAPI.addMember(familyId, {
        display_name: displayName.trim(),
        email: email.trim() || undefined,
      })
      onMemberAdded(member)
      setDisplayName('')
      setEmail('')
      setSuccess(`${member.display_name} added.`)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(detail || 'Failed to add member')
    } finally {
      setAdding(false)
    }
  }

  const roleColor = (role: string) => role === 'admin' ? '#93c5fd' : '#9ca3af'

  return (
    <div style={{ backgroundColor: '#111827', borderRadius: '0.75rem', border: '1px solid #1f2937', padding: '1.5rem' }}>
      <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#ffffff', marginBottom: '1rem' }}>
        Manage Members
      </h2>

      {/* Current members */}
      <div style={{ marginBottom: '1.25rem' }}>
        {members.map((m) => (
          <div key={m.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0', borderBottom: '1px solid #1f2937' }}>
            <span style={{ color: '#d1d5db', fontSize: '0.875rem' }}>{m.display_name}</span>
            <span style={{ color: roleColor(m.role), fontSize: '0.75rem', textTransform: 'capitalize' }}>{m.role}</span>
          </div>
        ))}
      </div>

      {/* Add member form */}
      <form onSubmit={handleAdd} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: '#9ca3af', marginBottom: '0.25rem' }}>
            Display Name <span style={{ color: '#ef4444' }}>*</span>
          </label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="e.g. Jane"
            required
            style={{ width: '100%', padding: '0.5rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.875rem', boxSizing: 'border-box' as const }}
          />
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: '#9ca3af', marginBottom: '0.25rem' }}>
            Email <span style={{ color: '#6b7280' }}>(links to their account)</span>
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="their registered email"
            style={{ width: '100%', padding: '0.5rem 0.75rem', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.875rem', boxSizing: 'border-box' as const }}
          />
        </div>

        {error && <p style={{ color: '#fca5a5', fontSize: '0.875rem', margin: 0 }}>{error}</p>}
        {success && <p style={{ color: '#86efac', fontSize: '0.875rem', margin: 0 }}>{success}</p>}

        <button
          type="submit"
          disabled={adding || !displayName.trim()}
          style={{ padding: '0.5rem 1rem', backgroundColor: adding || !displayName.trim() ? '#374151' : '#2563eb', color: '#ffffff', borderRadius: '0.375rem', border: 'none', cursor: adding || !displayName.trim() ? 'not-allowed' : 'pointer', fontSize: '0.875rem', fontWeight: 500 }}
        >
          {adding ? 'Adding...' : 'Add Member'}
        </button>
      </form>
    </div>
  )
}
