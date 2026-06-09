import axios from 'axios'

const BASE_URL = 'http://localhost:8000/api/v1'

export const analyzeProspect = async (companyName, linkedinUrl, screenshot) => {
  const formData = new FormData()
  formData.append('company_name', companyName)
  formData.append('linkedin_url', linkedinUrl)
  if (screenshot) {
    formData.append('screenshot', screenshot)
  }
  const response = await axios.post(`${BASE_URL}/analyze`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

export const continueConversation = async (companyName, prospectReply, conversationHistory, closingProbability) => {
  const formData = new FormData()
  formData.append('company_name', companyName)
  formData.append('prospect_reply', prospectReply)
  formData.append('conversation_history', JSON.stringify(conversationHistory))
  formData.append('closing_probability', closingProbability.toString())
  const response = await axios.post(`${BASE_URL}/continue-conversation`, formData)
  return response.data
}

export const checkHealth = async () => {
  const response = await axios.get(`${BASE_URL}/health`)
  return response.data
}