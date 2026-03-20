import apiClient from './client'

export interface TimeSeriesDatapoint {
  date: string
  value: number | null
  ref_low: number | null
  ref_high: number | null
}

export interface TimeSeriesSeries {
  analyte_id: string
  analyte_name: string
  unit: string
  datapoints: TimeSeriesDatapoint[]
}

export interface TimeSeriesResponse {
  series: TimeSeriesSeries[]
}

export const resultsAPI = {
  getTimeSeries: async (
    familyMemberId: string,
    analyteIds?: string[],
    dateFrom?: string,
    dateTo?: string
  ): Promise<TimeSeriesResponse> => {
    const params = new URLSearchParams()
    params.append('family_member_id', familyMemberId)
    if (analyteIds?.length) {
      analyteIds.forEach((id) => params.append('analyte_id', id))
    }
    if (dateFrom) params.append('date_from', dateFrom)
    if (dateTo) params.append('date_to', dateTo)

    const response = await apiClient.get(`/results/timeseries?${params.toString()}`)
    return response.data
  },
}
