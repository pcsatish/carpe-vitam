import { LineChart, Line, ReferenceLine, ReferenceArea, ResponsiveContainer, YAxis } from 'recharts'
import { TimeSeriesSeries } from '../../api/results'

interface AnalyteCardProps {
  series: TimeSeriesSeries
  onClick: () => void
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

export default function AnalyteCard({ series, onClick }: AnalyteCardProps) {
  const latest = series.datapoints[series.datapoints.length - 1]
  const status = getStatus(latest?.value, series.ref_low, series.ref_high)
  const style = status ? STATUS[status] : DEFAULT_STATUS

  const chartData = series.datapoints.map((dp) => ({ date: dp.date, value: dp.value }))

  const values = series.datapoints.map((d) => d.value).filter((v): v is number => v != null)
  const allPoints = [...values, series.ref_low, series.ref_high].filter((v): v is number => v != null)
  const min = allPoints.length ? Math.min(...allPoints) * 0.85 : 0
  const max = allPoints.length ? Math.max(...allPoints) * 1.15 : 100

  return (
    <div
      onClick={onClick}
      style={{ backgroundColor: '#1f2937', borderRadius: '0.75rem', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', cursor: 'pointer' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{ color: '#ffffff', fontWeight: 600, fontSize: '0.875rem' }}>{series.analyte_name}</span>
        {status && (
          <span style={{ backgroundColor: style.bg, color: style.color, fontSize: '0.75rem', padding: '0.125rem 0.5rem', borderRadius: '9999px', fontWeight: 500 }}>
            {status}
          </span>
        )}
      </div>

      {latest?.value != null && (
        <div>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, color: style.line }}>{latest.value}</span>
          <span style={{ color: '#9ca3af', fontSize: '0.875rem', marginLeft: '0.25rem' }}>{series.unit}</span>
        </div>
      )}

      {(series.ref_low != null || series.ref_high != null) && (
        <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>
          Optimal range: {series.ref_low ?? '—'} – {series.ref_high ?? '—'}
        </div>
      )}

      <div style={{ height: 60 }}>
        <ResponsiveContainer width="100%" height={60}>
          <LineChart data={chartData} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
            <YAxis domain={[min, max]} hide />
            {series.ref_low != null && series.ref_high != null && (
              <ReferenceArea y1={series.ref_low} y2={series.ref_high} fill="#166534" fillOpacity={0.4} />
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
              dot={chartData.length === 1 ? { r: 3, fill: style.line } : false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
