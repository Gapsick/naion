<template>
  <div class="chat-container">
    <header class="chat-header">
      <div class="header-top">
        <h1 class="logo">内音</h1>
        <div class="header-actions">
          <button class="icon-btn" @click="showRecords = true">기록</button>
          <button class="icon-btn dev" @click="devSkipToSummary" title="테스트">🧪</button>
          <button class="icon-btn" @click="showSettings = true">⚙</button>
        </div>
      </div>
      <div class="step-indicator">
        <div :class="['step-item', { active: indicatorStep === 1, done: indicatorStep > 1 }]">
          <span class="step-num">1</span>
          <span class="step-label">ためる</span>
        </div>
        <div class="step-line" :class="{ done: indicatorStep > 1 }" />
        <div :class="['step-item', { active: indicatorStep === 2, done: indicatorStep > 2 }]">
          <span class="step-num">2</span>
          <span class="step-label">きく</span>
        </div>
        <div class="step-line" :class="{ done: indicatorStep > 2 }" />
        <div :class="['step-item', { active: indicatorStep === 3 }]">
          <span class="step-num">3</span>
          <span class="step-label">まとめる</span>
        </div>
      </div>
    </header>

    <!-- 설정 패널 -->
    <Transition name="settings-slide">
      <div v-if="showSettings" class="settings-overlay" @click.self="showSettings = false">
        <div class="settings-drawer">
          <div class="settings-greeting">
            <div class="settings-avatar">{{ currentUser?.nickname?.[0] ?? '나' }}</div>
            <div>
              <div class="settings-name">{{ currentUser?.nickname }}님</div>
              <div class="settings-welcome">환영합니다</div>
            </div>
          </div>

          <div class="settings-menu">
            <button class="settings-menu-item" @click="startEditNickname">
              <span>정보 수정</span>
              <span class="menu-arrow">›</span>
            </button>
            <div v-if="editingNickname" class="nickname-edit-area">
              <input
                v-model="newNickname"
                class="nickname-input"
                placeholder="새 닉네임"
                @keydown.enter="saveNickname"
                @keydown.escape="editingNickname = false"
                autofocus
              />
              <div class="edit-actions">
                <button class="text-btn" @click="saveNickname" :disabled="nicknameLoading">저장</button>
                <button class="text-btn cancel" @click="editingNickname = false">취소</button>
              </div>
              <p v-if="nicknameError" class="settings-error">{{ nicknameError }}</p>
            </div>
            <button class="settings-menu-item">
              <span>문의사항</span>
              <span class="menu-arrow">›</span>
            </button>
            <button class="settings-menu-item logout" @click="logout">
              <span>로그아웃</span>
              <span class="menu-arrow">›</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="records-slide">
      <RecordsView v-if="showRecords" @close="showRecords = false" />
    </Transition>

    <ConfirmModal
      :show="modal.show"
      :message="modal.message"
      :confirm-text="modal.confirmText"
      @confirm="modal.onConfirm()"
      @cancel="closeModal"
    />

    <div class="page-wrapper">
      <Transition :name="transitionName">

        <!-- PAGE 1: 자유롭게 쏟아내기 -->
        <div v-if="page === 'input'" key="input" class="page step1">
          <p class="step1-desc">오늘 있었던 일과 느낀 감정을 자유롭게 적어보세요.<br>잘 쓰지 않아도 돼요. 생각나는 그대로.</p>
          <textarea
            v-model="freeInput"
            placeholder="오늘 발표가 있었는데 엄청 떨렸어. 준비는 했는데 왜인지 자신이 없었고..."
            rows="8"
          />
          <button class="start-btn" :disabled="!freeInput.trim()" @click="goToPersona">다음</button>
        </div>

        <!-- PAGE 1.5: 페르소나 선택 -->
        <div v-else-if="page === 'persona'" key="persona" class="page step-persona">
          <div class="persona-page-inner">
            <p class="persona-page-title">어떤 방식으로 이야기할까요?</p>
            <p class="persona-page-sub">코치 스타일을 선택하면 바로 시작해요.</p>
            <div class="persona-cards-full">
              <button
                v-for="p in personaOptions"
                :key="p.id"
                :class="['persona-card-full', { selected: selectedPersona === p.id }]"
                @click="selectedPersona = p.id"
              >
                <span class="persona-icon">{{ p.icon }}</span>
                <div class="persona-text">
                  <span class="persona-name">{{ p.name }}</span>
                  <span class="persona-desc">{{ p.description }}</span>
                  <span class="persona-example">{{ p.example }}</span>
                </div>
              </button>
            </div>
            <div class="persona-actions">
              <button class="back-btn" @click="goBack">돌아가기</button>
              <button class="start-btn" @click="startChat">질문 시작하기</button>
            </div>
          </div>
        </div>

        <!-- PAGE 2: AI 대화 -->
        <div v-else-if="page === 'chat'" key="chat" class="page chat-page">
          <div class="messages" ref="messagesEl">
            <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
              <div
                class="bubble"
                v-html="msg.role === 'assistant' ? renderMarkdown(msg.content) : msg.content"
              />
            </div>
            <div v-if="isLoading" class="message assistant">
              <div class="bubble loading">...</div>
            </div>
          </div>

          <div class="bottom-bar">
            <div class="reason-dots">
              <span v-for="n in Math.max(5, reasonCount)" :key="n" :class="['dot', { filled: n <= reasonCount }]" />
              <span class="dot-label">이유 {{ reasonCount }}개</span>
            </div>
            <div class="bottom-actions">
              <button class="reset-btn" @click="resetChat" title="대화 초기화">↺</button>
              <button
                class="summary-btn"
                :disabled="reasonCount === 0 || isSummarizing"
                @click="handleSummary"
              >{{ isSummarizing ? "분석 중..." : "요약하기" }}</button>
            </div>
          </div>

          <div class="input-area">
            <textarea
              v-model="input"
              placeholder="생각나는 대로 말해보세요"
              rows="1"
              ref="inputEl"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.shift.enter.prevent="input += '\n'"
              :disabled="isLoading"
            />
            <button @click="sendMessage" :disabled="isLoading || !input.trim()">전송</button>
          </div>
        </div>

        <!-- PAGE ERROR -->
        <div v-else-if="page === 'error'" key="error" class="page error-page">
          <div class="error-card">
            <p class="error-title">문제가 발생했어요</p>
            <p class="error-message">{{ errorMessage }}</p>
            <button class="start-btn" @click="restart">처음으로 돌아가기</button>
          </div>
        </div>

        <!-- PAGE 3: まとめる -->
        <div v-else-if="page === 'summary'" key="summary" class="page step3">
          <div class="note-card">
            <div class="note-date">{{ today }}</div>
            <p class="note-context-text">{{ context }}</p>
            <div class="note-reasons-list">
              <div
                v-for="(r, i) in (reasonsHighlighted.length ? reasonsHighlighted : reasons)"
                :key="i"
                class="note-reason-row"
              >
                <span class="note-star">*</span>
                <span v-html="r" />
              </div>
            </div>
            <div class="note-divider" />
            <p class="note-conclusion">{{ conclusion }}</p>
            <div class="note-footer">内音</div>
          </div>
          <div class="step3-actions">
            <button class="back-btn" @click="goBack">대화로 돌아가기</button>
            <button class="restart-btn" @click="restart">새로 시작하기</button>
          </div>
        </div>

      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from "vue"
import { marked } from "marked"
import { useRouter } from "vue-router"
import { streamChat, fetchSummary, seedTestSession } from "../api/chat"
import { getStoredUser, clearAuth } from "../api/auth"
import RecordsView from "./RecordsView.vue"
import ConfirmModal from "../components/ConfirmModal.vue"

const router = useRouter()
const currentUser = getStoredUser()
if (!currentUser) router.push("/login")

const USER_ID = currentUser?.id ?? "demo-user"

function logout() {
  showConfirm("로그아웃 할까요?", "로그아웃", () => {
    closeModal()
    clearAuth()
    router.push("/login")
  })
}

function startEditNickname() {
  newNickname.value = currentUser?.nickname ?? ""
  nicknameError.value = ""
  editingNickname.value = true
}

async function saveNickname() {
  if (!newNickname.value.trim()) return
  nicknameLoading.value = true
  nicknameError.value = ""
  try {
    const { getAccessToken } = await import("../api/auth")
    const token = getAccessToken()
    const res = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/auth/nickname`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ nickname: newNickname.value.trim() }),
    })
    if (!res.ok) { const d = await res.json(); throw new Error(d.detail) }
    const data = await res.json()
    const stored = JSON.parse(localStorage.getItem("naion_user") || "{}")
    stored.nickname = data.user.nickname
    localStorage.setItem("naion_user", JSON.stringify(stored))
    if (currentUser) currentUser.nickname = data.user.nickname
    editingNickname.value = false
  } catch (e: any) {
    nicknameError.value = e.message
  } finally {
    nicknameLoading.value = false
  }
}

const personaOptions = [
  { id: "warm",    icon: "🌿", name: "따뜻한 코치",     description: "공감하며 부드럽게 이끌어요",       example: "\"많이 힘드셨겠어요. 왜 그런지 말해줄 수 있어요?\"" },
  { id: "factual", icon: "🔍", name: "분석적 코치",     description: "사실과 원인 중심으로 파고들어요",   example: "\"어떤 상황에서 그렇게 느꼈나요?\"" },
  { id: "coach",   icon: "💬", name: "소크라테스 코치", description: "질문으로만 스스로 답을 찾게 해요", example: "\"그 순간 무엇을 원하고 있었나요?\"" },
]

type Page = 'input' | 'persona' | 'chat' | 'summary' | 'error'
const pageOrder: Page[] = ['input', 'persona', 'chat', 'summary']

const page           = ref<Page>('input')
const direction      = ref<'forward' | 'backward'>('forward')
const transitionName = computed(() => `slide-${direction.value}`)
const indicatorStep  = computed(() => {
  if (page.value === 'input' || page.value === 'persona') return 1
  if (page.value === 'chat' || page.value === 'error') return 2
  return 3
})

const errorMessage       = ref("")

const freeInput          = ref("")
const input              = ref("")
const selectedPersona    = ref("warm")
const isLoading          = ref(false)
const isSummarizing      = ref(false)
const reasonCount        = ref(0)
const reasons            = ref<string[]>([])
const conclusion         = ref("")
const reasonsHighlighted = ref<string[]>([])
const messagesEl         = ref<HTMLElement>()
const inputEl            = ref<HTMLTextAreaElement>()
const context            = ref("")
const showRecords        = ref(false)
const showSettings       = ref(false)
const modal = ref({ show: false, message: "", confirmText: "확인", onConfirm: () => {} })

function showConfirm(message: string, confirmText: string, onConfirm: () => void) {
  modal.value = { show: true, message, confirmText, onConfirm }
}
function closeModal() { modal.value.show = false }
const editingNickname    = ref(false)
const newNickname        = ref("")
const nicknameLoading    = ref(false)
const nicknameError      = ref("")
const messages           = ref<{ role: "user" | "assistant"; content: string }[]>([])

function navigate(to: Page) {
  direction.value = pageOrder.indexOf(to) >= pageOrder.indexOf(page.value) ? 'forward' : 'backward'
  page.value = to
}
function goBack() {
  if (page.value === 'persona') navigate('input')
  else if (page.value === 'summary') navigate('chat')
}
function goToPersona() {
  if (!freeInput.value.trim()) return
  context.value = freeInput.value.trim()
  navigate('persona')
}
function renderMarkdown(text: string) { return marked.parse(text) as string }

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')}`
})

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}

async function startChat() {
  navigate('chat')
  isLoading.value = true
  messages.value.push({ role: "assistant" as const, content: "" })
  await scrollToBottom()
  const idx = messages.value.length - 1
  try {
    for await (const chunk of streamChat(
      "방금 적은 내용을 바탕으로 질문해줘",
      USER_ID,
      (count) => { reasonCount.value = count },
      context.value, selectedPersona.value,
      (reason) => { reasons.value.push(reason) },
      (msg) => { errorMessage.value = msg; page.value = 'error' },
      () => { messages.value[idx].content = "" }
    )) { messages.value[idx].content += chunk; await scrollToBottom() }
  } finally { isLoading.value = false }
}

async function sendMessage() {
  if (!input.value.trim() || isLoading.value) return
  const userMsg = input.value.trim()
  input.value = ""
  messages.value.push({ role: "user", content: userMsg })
  isLoading.value = true
  messages.value.push({ role: "assistant" as const, content: "" })
  await scrollToBottom()
  const idx = messages.value.length - 1
  try {
    for await (const chunk of streamChat(
      userMsg, USER_ID,
      (count) => { reasonCount.value = count },
      undefined, selectedPersona.value,
      (reason) => { reasons.value.push(reason) },
      (msg) => { errorMessage.value = msg; page.value = 'error' },
      () => { messages.value[idx].content = "" }
    )) { messages.value[idx].content += chunk; await scrollToBottom() }
  } finally {
    isLoading.value = false
    await nextTick()
    inputEl.value?.focus()
  }
}

async function handleSummary() {
  isSummarizing.value = true
  conclusion.value = ""
  reasonsHighlighted.value = []
  try {
    const result = await fetchSummary(USER_ID)
    conclusion.value = result.conclusion
    reasonsHighlighted.value = result.reasons_highlighted
    navigate('summary')
  } finally { isSummarizing.value = false }
}

async function devSkipToSummary() {
  const data = await seedTestSession(USER_ID)
  reasonCount.value = data.reasons_count
  reasons.value = ["발표 준비가 부족했다", "자신감이 없었다", "잠을 못 잤다", "피드백이 두려웠다", "실패가 무서웠다"]
  context.value = "오늘 발표가 있었는데 엄청 떨렸어. 준비는 했는데 왜인지 자신이 없었고..."
  messages.value = [
    { role: "user",      content: "오늘 발표가 있었는데 엄청 떨렸어." },
    { role: "assistant", content: "많이 떨리셨군요. 왜 그렇게 떨렸던 것 같아요?" },
    { role: "user",      content: "모르겠어. 그냥 자신이 없었나봐." },
    { role: "assistant", content: "이유들이 쌓였어요. 요약하기 버튼을 눌러보세요." },
  ]
  navigate('chat')
}

function resetChat() {
  showConfirm("대화를 초기화할까요?\n저장된 이유도 모두 사라져요.", "초기화", async () => {
    closeModal()
    const token = (await import("../api/auth")).getAccessToken()
    await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/chat`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    })
    messages.value = []
    reasonCount.value = 0
    reasons.value = []
    freeInput.value = ""
    context.value = ""
    navigate('input')
  })
}

function restart() {
  freeInput.value = ""; input.value = ""; messages.value = []
  reasonCount.value = 0; reasons.value = []; conclusion.value = ""; reasonsHighlighted.value = []
  context.value = ""; selectedPersona.value = "warm"
  navigate('input')
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px;
  background: #f7f3ee;
  font-size: 15px;
  position: relative;
}

/* ── 헤더 ── */
.chat-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 0 10px;
  border-bottom: 1px solid #e8e0d8;
  flex-shrink: 0;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 18px; font-weight: 600; color: #2c1f14;
  font-family: 'Hiragino Mincho ProN', 'Yu Mincho', 'MS Mincho', serif;
  letter-spacing: 0.08em;
}

.header-actions { display: flex; align-items: center; gap: 6px; }

.icon-btn {
  background: none; border: 1px solid #e0d6cc; border-radius: 6px;
  padding: 4px 10px; font-size: 12px; color: #a89080; cursor: pointer; transition: all 0.2s;
}
.icon-btn:hover { background: #f0e8e0; color: #6b4c2a; }
.icon-btn.dev { border-style: dashed; opacity: 0.5; }
.icon-btn.dev:hover { opacity: 1; }

/* ── 설정 드로어 ── */
.settings-overlay {
  position: absolute; inset: 0;
  background: rgba(44, 31, 20, 0.3);
  z-index: 100;
  backdrop-filter: blur(2px);
}

.settings-drawer {
  position: absolute; top: 0; right: 0; bottom: 0;
  width: 78%;
  background: #f7f3ee;
  display: flex; flex-direction: column;
  box-shadow: -4px 0 20px rgba(44,31,20,0.15);
}

.settings-greeting {
  display: flex; align-items: center; gap: 14px;
  padding: 36px 24px 24px;
  border-bottom: 1px solid #e8e0d8;
  background: #fffdf9;
}

.settings-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: #6b4c2a; color: #fffdf9;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 600; flex-shrink: 0;
}

.settings-name { font-size: 16px; font-weight: 600; color: #2c1f14; }
.settings-welcome { font-size: 12px; color: #a89080; margin-top: 2px; }

.settings-menu {
  display: flex; flex-direction: column;
  padding: 12px 0; flex: 1;
}

.settings-menu-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px; background: none; border: none;
  font-size: 14px; color: #2c1f14; cursor: pointer;
  border-bottom: 1px solid #f0ebe4; text-align: left;
  transition: background 0.15s;
}
.settings-menu-item:hover { background: #f0ebe4; }
.settings-menu-item.logout { color: #c07060; margin-top: auto; }

.menu-arrow { font-size: 18px; color: #c8b8a8; }

.nickname-edit-area {
  padding: 12px 24px 16px;
  display: flex; flex-direction: column; gap: 8px;
  background: #fdf8f3; border-bottom: 1px solid #f0ebe4;
}

.nickname-input {
  width: 100%; padding: 8px 12px; border: 1px solid #a07850;
  border-radius: 8px; font-size: 14px; outline: none;
  background: #fffdf9; color: #2c1f14;
}

.text-btn {
  background: none; border: none; font-size: 12px;
  color: #a07850; cursor: pointer; padding: 4px 0; white-space: nowrap;
}
.text-btn.cancel { color: #b0a090; }
.edit-actions { display: flex; gap: 10px; }
.settings-error { font-size: 11px; color: #c07060; }

/* ── 설정 슬라이드 애니메이션 ── */
.settings-slide-enter-active { transition: opacity 0.25s ease; }
.settings-slide-leave-active { transition: opacity 0.2s ease; }
.settings-slide-enter-from   { opacity: 0; }
.settings-slide-leave-to     { opacity: 0; }

.settings-slide-enter-active .settings-drawer { transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.settings-slide-leave-active .settings-drawer { transition: transform 0.25s cubic-bezier(0.32, 0.72, 0, 1); }
.settings-slide-enter-from .settings-drawer   { transform: translateX(100%); }
.settings-slide-leave-to .settings-drawer     { transform: translateX(100%); }

/* 스텝 인디케이터 */
.step-indicator { display: flex; align-items: center; }

.step-item { display: flex; align-items: center; gap: 6px; }

.step-num {
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600;
  background: #ede8e2; color: #b0a090;
  transition: all 0.3s;
}

.step-label { font-size: 11px; color: #b0a090; letter-spacing: 0.01em; transition: all 0.3s; white-space: nowrap; }

.step-item.active .step-num { background: #6b4c2a; color: #fffdf9; }
.step-item.active .step-label { color: #6b4c2a; font-weight: 600; }
.step-item.done .step-num { background: #c8a878; color: #fffdf9; }
.step-item.done .step-label { color: #a89080; }

.step-line {
  flex: 1; height: 1px; background: #e0d6cc;
  margin: 0 10px; min-width: 32px; transition: background 0.3s;
}
.step-line.done { background: #c8a878; }

/* ── 페이지 전환 ── */
.page-wrapper { flex: 1; position: relative; overflow: hidden; }
.page { position: absolute; inset: 0; display: flex; flex-direction: column; }

.slide-forward-enter-active, .slide-forward-leave-active,
.slide-backward-enter-active, .slide-backward-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}
.slide-forward-enter-from  { transform: translateX(40px); opacity: 0; }
.slide-forward-leave-to    { transform: translateX(-40px); opacity: 0; }
.slide-backward-enter-from { transform: translateX(-40px); opacity: 0; }
.slide-backward-leave-to   { transform: translateX(40px); opacity: 0; }

/* ── STEP 1 ── */
.step1 { justify-content: center; gap: 16px; padding: 24px 12px 20px; }

.step1-desc { font-size: 14px; color: #7a6555; line-height: 1.8; }

.step1 textarea {
  width: 100%; padding: 16px; border: 1px solid #e0d6cc; border-radius: 12px;
  font-size: 15px; line-height: 1.75; resize: none; outline: none;
  background: #fffdf9; color: #2c1f14; font-family: inherit;
  box-shadow: 0 1px 4px rgba(107,76,42,0.06);
}
.step1 textarea:focus { border-color: #a07850; box-shadow: 0 0 0 3px rgba(160,120,80,0.08); }

/* ── STEP 1.5 ── */
.step-persona { justify-content: center; overflow-y: auto; }
.persona-page-inner { display: flex; flex-direction: column; gap: 14px; padding: 16px 0 24px; }
.persona-page-title { font-size: 16px; font-weight: 600; color: #2c1f14; }
.persona-page-sub { font-size: 12px; color: #a89080; margin-top: -8px; }
.persona-cards-full { display: flex; flex-direction: column; gap: 8px; }

.persona-card-full {
  display: flex; align-items: flex-start; gap: 12px; padding: 14px 16px;
  border: 1.5px solid #e0d6cc; border-radius: 12px; background: #fffdf9;
  cursor: pointer; text-align: left; transition: all 0.18s;
}
.persona-card-full:hover { border-color: #a07850; background: #fdf8f3; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(107,76,42,0.08); }
.persona-card-full.selected { border-color: #6b4c2a; background: #f5ede4; }

.persona-icon { font-size: 22px; flex-shrink: 0; margin-top: 2px; }
.persona-text { display: flex; flex-direction: column; gap: 3px; }
.persona-name { font-size: 13px; font-weight: 600; color: #2c1f14; }
.persona-desc { font-size: 12px; color: #7a6555; }
.persona-example { font-size: 11px; color: #b0a090; font-style: italic; margin-top: 2px; }
.persona-actions { display: flex; justify-content: space-between; align-items: center; }

/* ── STEP 2: 채팅 ── */
.chat-page { gap: 0; }

.messages {
  flex: 1; min-height: 0; overflow-y: auto;
  display: flex; flex-direction: column; gap: 14px; padding: 20px 0;
}

.message { display: flex; justify-content: flex-start; }
.message.user { justify-content: flex-end; }

.bubble { max-width: 82%; padding: 12px 16px; font-size: 15px; line-height: 1.7; text-align: left; }
.bubble :deep(p) { margin: 0 0 6px 0; }
.bubble :deep(p:last-child) { margin-bottom: 0; }

.message.assistant .bubble {
  background: #fffdf9; border: 1px solid #e8e0d8; color: #2c1f14;
  border-radius: 4px 16px 16px 16px; box-shadow: 0 1px 3px rgba(107,76,42,0.06);
}
.message.user .bubble {
  background: #6b4c2a; color: #fffdf9;
  border-radius: 16px 16px 4px 16px; white-space: pre-wrap;
}

.loading { color: #c8b8a8; animation: pulse 1.2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.bottom-bar {
  flex-shrink: 0; display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0; border-top: 1px solid #e8e0d8;
}

.reason-dots { display: flex; align-items: center; gap: 5px; }
.dot { width: 7px; height: 7px; border-radius: 50%; background: #ddd4cc; transition: background 0.3s; }
.dot.filled { background: #6b4c2a; }
.dot-label { font-size: 12px; color: #a89080; margin-left: 4px; }

.bottom-actions { display: flex; align-items: center; gap: 8px; }

.reset-btn {
  background: none; border: 1px solid #e0d6cc; border-radius: 8px;
  padding: 6px 10px; font-size: 15px; color: #a89080; cursor: pointer; transition: all 0.2s;
}
.reset-btn:hover { background: #f0e8e0; color: #6b4c2a; }

.summary-btn {
  padding: 6px 16px; background: transparent; color: #a89080;
  border: 1px solid #e0d6cc; border-radius: 8px; font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.summary-btn:hover:not(:disabled) { background: #f0e8e0; color: #6b4c2a; }
.summary-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.input-area { display: flex; gap: 8px; padding: 8px 0 20px; flex-shrink: 0; }
.input-area textarea {
  flex: 1; padding: 12px 16px; border: 1px solid #e0d6cc; border-radius: 12px;
  font-size: 15px; outline: none; background: #fffdf9; color: #2c1f14;
  font-family: inherit; resize: none; line-height: 1.6;
}
.input-area textarea:focus { border-color: #a07850; box-shadow: 0 0 0 3px rgba(160,120,80,0.08); }
.input-area button {
  padding: 12px 20px; background: #6b4c2a; color: #fffdf9; border: none;
  border-radius: 12px; font-size: 15px; cursor: pointer; align-self: flex-end; transition: background 0.2s;
}
.input-area button:hover { background: #5a3e22; }
.input-area button:disabled { opacity: 0.3; cursor: not-allowed; }

/* ── STEP 3: まとめる ── */
.step3 {
  overflow-y: auto; padding: 24px 0 40px;
  gap: 20px; align-items: center; justify-content: center;
}

.note-card {
  width: 100%; max-width: 600px; background: #fffef5; border-radius: 4px;
  padding: 24px 24px 32px 24px;
  box-shadow: 0 2px 8px rgba(107,76,42,0.08), 0 12px 32px rgba(107,76,42,0.10);
  border-left: 3px solid #d4a97a;
}

.note-date { font-size: 11px; color: #b0a090; letter-spacing: 0.08em; margin-bottom: 20px; font-family: 'Courier New', monospace; }

.note-context-text { font-size: 15px; color: #2c1f14; line-height: 1.8; margin: 0 0 16px; word-break: keep-all; text-align: left; }

.note-reasons-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px; }

.note-reason-row { display: flex; gap: 8px; font-size: 14px; color: #5a4030; line-height: 1.6; }
.note-star { color: #c8a878; flex-shrink: 0; }

.note-reason-row :deep(mark) {
  background: none; font-weight: 700; color: #6b4c2a; border-bottom: 2px solid #c8a878;
}

.note-divider { height: 1px; background: linear-gradient(to right, #d4a97a, transparent); margin: 4px 0 20px; }

.note-conclusion { font-size: 15px; color: #2c1f14; line-height: 1.8; margin: 0; word-break: keep-all; }

.note-footer { margin-top: 28px; font-size: 11px; color: #c8b8a8; text-align: right; letter-spacing: 0.1em; }

.step3-actions { display: flex; gap: 10px; flex-shrink: 0; }

/* ── 기록 패널 slide-up ── */
.records-slide-enter-active { transition: opacity 0.25s ease, transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
.records-slide-leave-active { transition: opacity 0.2s ease, transform 0.25s cubic-bezier(0.32, 0.72, 0, 1); }
.records-slide-enter-from   { opacity: 0; transform: translateY(100%); }
.records-slide-leave-to     { opacity: 0; transform: translateY(100%); }

/* ── ERROR PAGE ── */
.error-page { justify-content: center; align-items: center; }
.error-card { display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; }
.error-title { font-size: 18px; font-weight: 600; color: #2c1f14; }
.error-message { font-size: 13px; color: #a89080; }

/* ── 공통 버튼 ── */
.start-btn {
  padding: 10px 22px; background: #6b4c2a; color: #fffdf9; border: none;
  border-radius: 10px; font-size: 13px; cursor: pointer; transition: background 0.2s; align-self: flex-end;
}
.start-btn:hover { background: #5a3e22; }
.start-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.back-btn {
  padding: 10px 22px; background: transparent; color: #a89080;
  border: 1px solid #e0d6cc; border-radius: 8px; font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.back-btn:hover { background: #f0e8e0; color: #6b4c2a; }

.restart-btn {
  padding: 10px 22px; background: transparent; color: #a89080;
  border: 1px solid #e0d6cc; border-radius: 8px; font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.restart-btn:hover { background: #f0e8e0; color: #6b4c2a; }
</style>
