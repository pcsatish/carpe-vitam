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


  // Use index-based keys to avoid spaces in dataKey
  const dataMap = new Map<string, any>()
  series.forEach((s, index) => {
    s.datapoints.forEach((dp) => {
      if (!dataMap.has(dp.date)) {
        dataMap.set(dp.date, { date: dp.date })
      }
      const entry = dataMap.get(dp.date)
      entry[`v${index}`] = dp.value
    })
  })

  const chartData = Array.from(dataMap.values()).sort((a, b) => a.date.localeCompare(b.date))

  return (
    <div className="w-full" style={{ height: 384 }}>
      <ResponsiveContainer width="100%" height={384}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" angle={-45} textAnchor="end" height={60} />
          <YAxis />
          <Tooltip formatter={(value: number) => value?.toFixed(2) ?? 'N/A'} />
          <Legend />
          {series.map((s, index) => (
            <Line
              key={s.analyte_id}
              type="monotone"
              dataKey={`v${index}`}
              stroke={COLORS[index % COLORS.length]}
              dot={(props: any) => {
                const { cx, cy } = props
                if (cx == null || cy == null) return <g key="empty" />
                return <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r={5} fill={COLORS[index % COLORS.length]} stroke="#fff" strokeWidth={1} />
              }}
              activeDot={{ r: 7 }}
              name={`${s.analyte_name} (${s.unit})`}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
