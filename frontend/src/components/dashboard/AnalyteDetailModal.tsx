import { useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceArea, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { TimeSeriesSeries } from '../../api/results'

interface Props {
  series: TimeSeriesSeries
  onClose: () => void
}

function getDeviation(value: number, refLow: number | null | undefined, refHigh: number | null | undefined): string | null {
  if (refHigh != null && value > refHigh) {
    const pct = Math.round(((value - refHigh) / refHigh) * 100)
    return `+${pct}%`
  }
  if (refLow != null && refLow > 0 && value < refLow) {
    const pct = Math.round(((refLow - value) / refLow) * 100)
    return `-${pct}%`
  }
  return null
}

function getStatus(value: number | null | undefined, refLow: number | null | undefined, refHigh: number | null | undefined) {
  if (value == null) return null
  if (refLow != null && value < refLow) return 'Low'
  if (refHigh != null && value > refHigh) return 'High'
  if (refLow != null || refHigh != null) return 'Optimal'
  return null
}

const STATUS = {
  Low:     { bg: '#78350f', color: '#fcd34d', line: '#f59e0b' },
  High:    { bg: '#7f1d1d', color: '#fca5a5', line: '#ef4444' },
  Optimal: { bg: '#1e3a8a', color: '#93c5fd', line: '#3b82f6' },
}
const DEFAULT_STATUS = { bg: '#374151', color: '#d1d5db', line: '#6b7280' }

function formatDate(dateStr: string) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatDateShort(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

export default function AnalyteDetailModal({ series, onClose }: Props) {
  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const latest = series.datapoints[series.datapoints.length - 1]
  const status = getStatus(latest?.value, series.ref_low, series.ref_high)
  const style = status ? STATUS[status] : DEFAULT_STATUS

  const chartData = series.datapoints.map((dp) => ({
    date: dp.date,
    value: dp.value,
    label: formatDateShort(dp.date),
    lab_name: dp.lab_name,
  }))

  const values = series.datapoints.map((d) => d.value).filter((v): v is number => v != null)
  const allPoints = [...values, series.ref_low, series.ref_high].filter((v): v is number => v != null)
  const min = allPoints.length ? Math.min(...allPoints) * 0.85 : 0
  const max = allPoints.length ? Math.max(...allPoints) * 1.15 : 100

  // History rows newest-first
  const rows = [...series.datapoints].reverse()

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 50,
        backgroundColor: 'rgba(0,0,0,0.7)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '1rem',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: '#111827', borderRadius: '0.75rem',
          border: '1px solid #1f2937', width: '100%', maxWidth: '720px',
          maxHeight: '90vh', overflowY: 'auto', padding: '1.5rem',
          display: 'flex', flexDirection: 'column', gap: '1.25rem',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ color: '#ffffff', fontWeight: 700, fontSize: '1.25rem', margin: 0 }}>
              {series.analyte_name}
            </h2>
            {series.category && (
              <span style={{ color: '#6b7280', fontSize: '0.75rem' }}>{series.category}</span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {status && (
              <span style={{ backgroundColor: style.bg, color: style.color, fontSize: '0.75rem', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontWeight: 500 }}>
                {latest?.value != null && (status === 'High' || status === 'Low')
                  ? `${getDeviation(latest.value, series.ref_low, series.ref_high)} ${status}`
                  : status}
              </span>
            )}
            <button
              onClick={onClose}
              style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer', fontSize: '1.25rem', lineHeight: 1, padding: '0.25rem' }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Latest value */}
        {latest?.value != null && (
          <div>
            <span style={{ fontSize: '2rem', fontWeight: 700, color: style.line }}>{latest.value}</span>
            <span style={{ color: '#9ca3af', fontSize: '1rem', marginLeft: '0.375rem' }}>{series.unit}</span>
            {latest.date && (
              <span style={{ color: '#6b7280', fontSize: '0.875rem', marginLeft: '0.75rem' }}>
                as of {formatDate(latest.date)}
              </span>
            )}
          </div>
        )}

        {(series.ref_low != null || series.ref_high != null) && (
          <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Optimal range: {series.ref_low ?? '—'} – {series.ref_high ?? '—'} {series.unit}
          </div>
        )}

        {/* Large chart */}
        <div style={{ height: 220 }}>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="label"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                axisLine={{ stroke: '#374151' }}
                tickLine={false}
              />
              <YAxis
                domain={[min, max]}
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={48}
                tickFormatter={(v: number) => String(v)}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#ffffff' }}
                labelStyle={{ color: '#9ca3af', marginBottom: '0.25rem' }}
                formatter={(value: number, _key: string, props: { payload?: { lab_name?: string | null } }) => {
                  const lab = props.payload?.lab_name
                  return [`${value} ${series.unit}${lab ? ` · ${lab}` : ''}`, series.analyte_name]
                }}
              />
              {series.ref_low != null && series.ref_high != null && (
                <ReferenceArea y1={series.ref_low} y2={series.ref_high} fill="#166534" fillOpacity={0.25} />
              )}
              {series.ref_low != null && (
                <ReferenceLine y={series.ref_low} stroke="#166534" strokeDasharray="3 3" strokeWidth={1} />
              )}
              {series.ref_high != null && (
                <ReferenceLine y={series.ref_high} stroke="#166534" strokeDasharray="3 3" strokeWidth={1} />
              )}
              <Line
                type="monotone"
                dataKey="value"
                stroke={style.line}
                strokeWidth={2}
                dot={{ r: 4, fill: style.line, strokeWidth: 0 }}
                activeDot={{ r: 6 }}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* History table */}
        <div>
          <h3 style={{ color: '#9ca3af', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
            History
          </h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1f2937' }}>
                <th style={{ textAlign: 'left', padding: '0.5rem 0.75rem', color: '#6b7280', fontWeight: 500 }}>Date</th>
                <th style={{ textAlign: 'right', padding: '0.5rem 0.75rem', color: '#6b7280', fontWeight: 500 }}>Value</th>
                <th style={{ textAlign: 'left', padding: '0.5rem 0.75rem', color: '#6b7280', fontWeight: 500 }}>Unit</th>
                <th style={{ textAlign: 'center', padding: '0.5rem 0.75rem', color: '#6b7280', fontWeight: 500 }}>Status</th>
                <th style={{ textAlign: 'left', padding: '0.5rem 0.75rem', color: '#6b7280', fontWeight: 500 }}>Lab</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((dp, i) => {
                const rowStatus = getStatus(dp.value, series.ref_low, series.ref_high)
                const rowStyle = rowStatus ? STATUS[rowStatus] : DEFAULT_STATUS
                return (
                  <tr key={i} style={{ borderBottom: '1px solid #1f2937' }}>
                    <td style={{ padding: '0.625rem 0.75rem', color: '#d1d5db' }}>{formatDate(dp.date)}</td>
                    <td style={{ padding: '0.625rem 0.75rem', color: rowStyle.line, fontWeight: 600, textAlign: 'right' }}>
                      {dp.value ?? '—'}
                    </td>
                    <td style={{ padding: '0.625rem 0.75rem', color: '#9ca3af' }}>{series.unit}</td>
                    <td style={{ padding: '0.625rem 0.75rem', textAlign: 'center' }}>
                      {rowStatus ? (
                        <span style={{ backgroundColor: rowStyle.bg, color: rowStyle.color, fontSize: '0.7rem', padding: '0.125rem 0.5rem', borderRadius: '9999px', fontWeight: 500 }}>
                          {dp.value != null && (rowStatus === 'High' || rowStatus === 'Low')
                            ? `${getDeviation(dp.value, series.ref_low, series.ref_high)} ${rowStatus}`
                            : rowStatus}
                        </span>
                      ) : '—'}
                    </td>
                    <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>
                      {dp.lab_name ?? '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
