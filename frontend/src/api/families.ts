import apiClient from './client'

export interface Family {
  id: string
  name: string
  created_by: string
  created_at: string
}

export interface FamilyMember {
  id: string
  family_id: string
  user_id: string | null
  display_name: string
  date_of_birth: string | null
  sex: string | null
  role: 'admin' | 'member' | 'viewer'
  joined_at: string
}

export const familiesAPI = {
  listFamilies: async (): Promise<Family[]> => {
    const response = await apiClient.get('/families')
    return response.data
  },

  createFamily: async (name: string): Promise<Family> => {
    const response = await apiClient.post('/families', { name })
    return response.data
  },

  listMembers: async (familyId: string): Promise<FamilyMember[]> => {
    const response = await apiClient.get(`/families/${familyId}/members`)
    return response.data
  },

  addMember: async (
    familyId: string,
    payload: { display_name: string; email?: string; date_of_birth?: string; sex?: string; role?: string }
  ): Promise<FamilyMember> => {
    const response = await apiClient.post(`/families/${familyId}/members`, payload)
    return response.data
  },
}
