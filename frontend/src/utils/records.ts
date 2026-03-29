export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface NaionRecord {
  id: string
  date: string
  conclusion: string
  messages: ChatMessage[]
  freeInput: string
}

const KEY = "naion_records"

export function saveRecord(
  conclusion: string,
  messages: ChatMessage[],
  freeInput: string
): NaionRecord {
  const records = getRecords()
  const d = new Date()
  const record: NaionRecord = {
    id: Date.now().toString(),
    date: `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')}`,
    conclusion,
    messages,
    freeInput,
  }
  records.unshift(record)
  localStorage.setItem(KEY, JSON.stringify(records))
  return record
}

export function getRecords(): NaionRecord[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]")
  } catch {
    return []
  }
}
