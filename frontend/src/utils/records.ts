export interface NaionRecord {
  id: string
  date: string       // "2026.03.28"
  conclusion: string // 결론 문장
}

const KEY = "naion_records"

export function saveRecord(conclusion: string): NaionRecord {
  const records = getRecords()
  const d = new Date()
  const record: NaionRecord = {
    id: Date.now().toString(),
    date: `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')}`,
    conclusion,
  }
  records.unshift(record) // 최신이 앞에
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
