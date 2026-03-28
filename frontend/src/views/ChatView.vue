<template>
  <div class="chat-container">
    <header class="chat-header">
      <h1>内音</h1>
      <div class="step-indicator">
        <span :class="['step', { active: step === 1, done: step > 1 }]">1 ためる</span>
        <span class="divider">›</span>
        <span :class="['step', { active: step === 2, done: step > 2 }]">2 きく</span>
        <span class="divider">›</span>
        <span :class="['step', { active: step === 3 }]">3 まとめる</span>
      </div>
      <div class="header-actions">
        <button class="records-open-btn" @click="showRecords = true">기록</button>
        <button class="dev-btn" @click="devSkipToSummary" title="테스트: 이유 6개 주입 후 요약">🧪</button>
      </div>
    </header>

    <RecordsView v-if="showRecords" @close="showRecords = false" />

    <!-- STEP 1: 자유롭게 쏟아내기 -->
    <div v-if="step === 1" class="step1">
      <p class="step1-desc">오늘 있었던 일과 느낀 감정을 자유롭게 적어보세요.<br>잘 쓰지 않아도 돼요. 생각나는 그대로.</p>
      <textarea
        v-model="freeInput"
        placeholder="오늘 발표가 있었는데 엄청 떨렸어. 준비는 했는데 왜인지 자신이 없었고..."
        rows="8"
      />
      <button class="start-btn" :disabled="!freeInput.trim()" @click="startChat">
        질문 시작하기 →
      </button>
    </div>

    <!-- STEP 2: AI 대화 -->
    <template v-if="step === 2">
      <div class="messages" ref="messagesEl">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="['message', msg.role]"
        >
          <div
            class="bubble"
            v-html="msg.role === 'assistant' ? renderMarkdown(msg.content) : msg.content"
          />
        </div>
        <div v-if="isLoading" class="message assistant">
          <div class="bubble loading">...</div>
        </div>
      </div>

      <div class="reason-counter">
        <div class="dots">
          <span
            v-for="n in Math.max(5, reasonCount)"
            :key="n"
            :class="['dot', { filled: n <= reasonCount }]"
          />
        </div>
        <span class="count-label">
          이유 {{ reasonCount }}개 {{ reasonCount >= 5 ? '✓' : `(${5 - reasonCount}개 더)` }}
        </span>
        <button
          class="summary-btn"
          :disabled="reasonCount < 5 || isSummarizing"
          @click="handleSummary"
        >
          {{ isSummarizing ? "분석 중..." : "요약하기" }}
        </button>
      </div>

      <div class="input-area">
        <textarea
          v-model="input"
          placeholder="생각나는 대로 말해보세요  (Shift+Enter 줄바꿈)"
          rows="1"
          ref="inputEl"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.shift.enter.prevent="input += '\n'"
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading || !input.trim()">전송</button>
      </div>
    </template>

    <!-- STEP 3: 결론 -->
    <div v-if="step === 3" class="step3">
      <div class="note-card">
        <div class="note-date">{{ today }}</div>
        <div class="note-lines">
          <div
            v-for="(line, i) in conclusionLines"
            :key="i"
            class="note-line"
          >{{ line }}</div>
        </div>
        <div class="note-footer">内音</div>
      </div>
      <div class="step3-actions">
        <button class="back-btn" @click="step = 2">← 대화로 돌아가기</button>
        <button class="restart-btn" @click="restart">새로 시작하기</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from "vue"
import { marked } from "marked"
import { streamChat, streamSummary, seedTestSession } from "../api/chat"
import { saveRecord } from "../utils/records"
import RecordsView from "./RecordsView.vue"

const SESSION_ID = "session-" + Date.now()
const USER_ID = "demo-user"

const step = ref<1 | 2 | 3>(1)
const freeInput = ref("")
const input = ref("")
const isLoading = ref(false)
const isSummarizing = ref(false)
const reasonCount = ref(0)
const conclusion = ref("")
const messagesEl = ref<HTMLElement>()
const inputEl = ref<HTMLTextAreaElement>()
const context = ref("")
const showRecords = ref(false)

const messages = ref<{ role: "user" | "assistant"; content: string }[]>([])

function renderMarkdown(text: string): string {
  return marked.parse(text) as string
}

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')}`
})

const conclusionLines = computed(() =>
  conclusion.value
    .split('\n')
    .map(l => l.replace(/^#+\s*/, '').trim())
    .filter(l => l.length > 0)
)

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

async function startChat() {
  if (!freeInput.value.trim()) return
  context.value = freeInput.value.trim()
  step.value = 2

  // STEP 1 내용을 컨텍스트로 넘기며 첫 메시지 전송
  const firstMessage = "방금 적은 내용을 바탕으로 질문해줘"
  isLoading.value = true
  const assistantMsg = { role: "assistant" as const, content: "" }
  messages.value.push(assistantMsg)
  await scrollToBottom()

  try {
    for await (const chunk of streamChat(
      firstMessage,
      SESSION_ID,
      USER_ID,
      (count) => { reasonCount.value = count },
      context.value
    )) {
      assistantMsg.content += chunk
      await scrollToBottom()
    }
  } finally {
    isLoading.value = false
  }
}

async function sendMessage() {
  if (!input.value.trim() || isLoading.value) return

  const userMsg = input.value.trim()
  input.value = ""
  messages.value.push({ role: "user", content: userMsg })
  isLoading.value = true

  const assistantMsg = { role: "assistant" as const, content: "" }
  messages.value.push(assistantMsg)
  await scrollToBottom()

  try {
    for await (const chunk of streamChat(
      userMsg,
      SESSION_ID,
      USER_ID,
      (count) => { reasonCount.value = count }
    )) {
      assistantMsg.content += chunk
      await scrollToBottom()
    }
  } finally {
    isLoading.value = false
    await nextTick()
    inputEl.value?.focus()
  }
}

async function handleSummary() {
  isSummarizing.value = true
  conclusion.value = ""

  try {
    for await (const chunk of streamSummary(SESSION_ID, USER_ID)) {
      conclusion.value += chunk
    }
    saveRecord(conclusion.value)
    step.value = 3
  } finally {
    isSummarizing.value = false
  }
}

async function devSkipToSummary() {
  const data = await seedTestSession(SESSION_ID)
  reasonCount.value = data.reasons_count
  messages.value = [
    { role: "user", content: "오늘 발표가 있었는데 엄청 떨렸어." },
    { role: "assistant", content: "많이 떨리셨군요. 왜 그렇게 떨렸던 것 같아요?" },
    { role: "user", content: "모르겠어. 그냥 자신이 없었나봐." },
    { role: "assistant", content: `이유 ${data.reasons_count}개가 쌓였어요. 요약하기 버튼을 눌러보세요.` },
  ]
  step.value = 2
}

function restart() {
  step.value = 1
  freeInput.value = ""
  input.value = ""
  messages.value = []
  reasonCount.value = 0
  conclusion.value = ""
  context.value = ""
}
</script>

<style scoped>
/* ── 카페 감성 토큰 ── */
/* bg: 따뜻한 크림, accent: 연한 모카 브라운 */

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 680px;
  margin: 0 auto;
  padding: 0 24px;
  background: #f7f3ee;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0;
  border-bottom: 1px solid #e8e0d8;
}

.chat-header h1 {
  font-size: 19px;
  font-weight: 600;
  color: #2c1f14;
  letter-spacing: 0.02em;
}

.step-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  letter-spacing: 0.03em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.records-open-btn {
  background: none;
  border: 1px solid #e0d6cc;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  color: #a89080;
  cursor: pointer;
  transition: all 0.2s;
}

.records-open-btn:hover {
  background: #f0e8e0;
  color: #6b4c2a;
}

.dev-btn {
  background: none;
  border: 1px dashed #ddd4cc;
  border-radius: 6px;
  padding: 3px 7px;
  font-size: 14px;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.dev-btn:hover { opacity: 1; }

.step { color: #c8bdb5; }
.step.active { color: #6b4c2a; font-weight: 600; }
.step.done { color: #a89080; }
.divider { color: #ddd4cc; }

/* ── STEP 1 ── */
.step1 {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 18px;
  padding: 40px 0;
}

.step1-desc {
  font-size: 15px;
  color: #7a6555;
  line-height: 1.8;
}

.step1 textarea {
  width: 100%;
  padding: 18px;
  border: 1px solid #e0d6cc;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.8;
  resize: none;
  outline: none;
  background: #fffdf9;
  color: #2c1f14;
  font-family: inherit;
  box-shadow: 0 1px 4px rgba(107,76,42,0.06);
}

.step1 textarea:focus {
  border-color: #a07850;
  box-shadow: 0 0 0 3px rgba(160,120,80,0.08);
}

.start-btn {
  align-self: flex-end;
  padding: 12px 26px;
  background: #6b4c2a;
  color: #fffdf9;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.start-btn:hover { background: #5a3e22; }
.start-btn:disabled { opacity: 0.3; cursor: not-allowed; }

/* ── STEP 2 ── */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.message { display: flex; justify-content: flex-start; }
.message.user { justify-content: flex-end; }

.bubble {
  max-width: 72%;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.7;
  text-align: left;
}

.bubble :deep(p) { margin: 0 0 6px 0; }
.bubble :deep(p:last-child) { margin-bottom: 0; }

.message.assistant .bubble {
  background: #fffdf9;
  border: 1px solid #e8e0d8;
  color: #2c1f14;
  border-radius: 4px 16px 16px 16px;
  box-shadow: 0 1px 3px rgba(107,76,42,0.06);
}

.message.user .bubble {
  background: #6b4c2a;
  color: #fffdf9;
  border-radius: 16px 16px 4px 16px;
  white-space: pre-wrap;
}

.loading { color: #c8b8a8; animation: pulse 1.2s infinite; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.reason-counter {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid #e8e0d8;
}

.dots { display: flex; gap: 5px; }

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ddd4cc;
  transition: background 0.3s;
}

.dot.filled { background: #6b4c2a; }

.count-label { font-size: 12px; color: #a89080; flex: 1; }

.summary-btn {
  padding: 8px 16px;
  background: #6b4c2a;
  color: #fffdf9;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.summary-btn:hover { background: #5a3e22; }
.summary-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.input-area {
  display: flex;
  gap: 8px;
  padding: 10px 0 22px;
}

.input-area textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0d6cc;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  background: #fffdf9;
  color: #2c1f14;
  font-family: inherit;
  resize: none;
  line-height: 1.6;
}

.input-area textarea:focus {
  border-color: #a07850;
  box-shadow: 0 0 0 3px rgba(160,120,80,0.08);
}

.input-area button {
  padding: 12px 20px;
  background: #6b4c2a;
  color: #fffdf9;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
  align-self: flex-end;
  transition: background 0.2s;
}

.input-area button:hover { background: #5a3e22; }
.input-area button:disabled { opacity: 0.3; cursor: not-allowed; }

/* ── STEP 3 ── */
.step3 {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 28px;
  padding: 40px 0;
}

.note-card {
  width: 100%;
  max-width: 420px;
  background: #fffef5;
  border-radius: 4px;
  padding: 36px 40px 40px;
  box-shadow:
    0 2px 4px rgba(107,76,42,0.08),
    0 8px 24px rgba(107,76,42,0.10),
    4px 4px 0 #e8ddd0;
  position: relative;
  /* 노트 줄 배경 */
  background-image: repeating-linear-gradient(
    to bottom,
    transparent,
    transparent 31px,
    #ede8e0 31px,
    #ede8e0 32px
  );
  background-position: 0 52px;
}

.note-date {
  font-size: 11px;
  color: #b0a090;
  letter-spacing: 0.08em;
  margin-bottom: 20px;
  font-family: 'Courier New', monospace;
}

.note-lines {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.note-line {
  font-size: 15px;
  color: #2c1f14;
  line-height: 32px;
  min-height: 32px;
  letter-spacing: 0.01em;
}

.note-footer {
  margin-top: 28px;
  font-size: 11px;
  color: #c8b8a8;
  text-align: right;
  letter-spacing: 0.1em;
}

.step3-actions {
  display: flex;
  gap: 10px;
}

.back-btn {
  padding: 10px 22px;
  background: transparent;
  color: #a89080;
  border: 1px solid #e0d6cc;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f0e8e0;
  color: #6b4c2a;
}

.restart-btn {
  padding: 10px 22px;
  background: transparent;
  color: #a89080;
  border: 1px solid #e0d6cc;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.restart-btn:hover {
  background: #f0e8e0;
  color: #6b4c2a;
}
</style>
