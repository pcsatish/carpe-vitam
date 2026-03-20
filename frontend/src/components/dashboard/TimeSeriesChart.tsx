import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TimeSeriesSeries } from '../../api/results'

interface TimeSeriesChartProps {
  series: TimeSeriesSeries[]
  loading?: boolean
}

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']

export default function TimeSeriesChart({ series, loading = false }: TimeSeriesChartProps) {
  if (loading) {
    return <div className="h-96 flex items-center justify-center">Loading...</div>
  }

  if (!series || series.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-500">No data available</p>
      </div>
    )
  }

  // Merge all datapoints into a single array keyed by date
  const dataMap = new Map<string, any>()
  series.forEach((s, seriesIndex) => {
    s.datapoints.forEach((dp) => {
      if (!dataMap.has(dp.date)) {
        dataMap.set(dp.date, { date: dp.date })
      }
      const entry = dataMap.get(dp.date)
      entry[`${s.analyte_name}_value`] = dp.value
      entry[`${s.analyte_name}_ref_low`] = dp.ref_low
      entry[`${s.analyte_name}_ref_high`] = dp.ref_high
    })
  })

  const chartData = Array.from(dataMap.values()).sort((a, b) => a.date.localeCompare(b.date))

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
            formatter={(value) => value?.toFixed(2) || 'N/A'}
          />
          <Legend />

          {series.map((s, index) => (
            <Line
              key={s.analyte_id}
              type="monotone"
              dataKey={`${s.analyte_name}_value`}
              stroke={COLORS[index % COLORS.length]}
              dot={false}
              name={`${s.analyte_name} (${s.unit})`}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
