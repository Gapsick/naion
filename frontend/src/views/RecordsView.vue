<template>
  <div class="records-overlay" @click.self="$emit('close')">
    <div class="records-panel">
      <Transition name="panel" mode="out-in">

        <!-- 상세 보기 -->
        <div v-if="selected" key="detail" class="detail-view">
          <div class="panel-header">
            <button class="back-btn" @click="selected = null">← 뒤로</button>
            <span class="panel-title">{{ selected.date }}</span>
            <button class="close-btn" @click="$emit('close')">✕</button>
          </div>
          <div class="detail-scroll">
            <div v-if="selected.freeInput" class="detail-section">
              <div class="detail-label">처음 적은 글</div>
              <div class="detail-free-text">{{ selected.freeInput }}</div>
            </div>
            <div v-if="selected.messages?.length" class="detail-section">
              <div class="detail-label">대화</div>
              <div class="detail-messages">
                <div
                  v-for="(msg, i) in selected.messages"
                  :key="i"
                  :class="['detail-msg', msg.role]"
                >
                  <div class="detail-bubble">{{ msg.content }}</div>
                </div>
              </div>
            </div>
            <div class="detail-section">
              <div class="detail-label">결론</div>
              <div class="detail-conclusion">{{ selected.conclusion }}</div>
            </div>
          </div>
        </div>

        <!-- 카드 그리드 -->
        <div v-else key="grid" class="grid-view">
          <div class="panel-header">
            <span class="panel-title">기록</span>
            <button class="close-btn" @click="$emit('close')">✕</button>
          </div>

          <div v-if="months.length > 1" class="month-filters">
            <button
              v-for="m in months"
              :key="m"
              :class="['month-btn', { active: selectedMonth === m }]"
              @click="selectedMonth = selectedMonth === m ? null : m"
            >{{ m }}</button>
          </div>

          <div v-if="filtered.length === 0" class="empty">
            <p>{{ records.length === 0 ? '아직 기록이 없어요.' : '기록이 없어요.' }}</p>
            <p class="empty-sub">대화를 마치면 여기에 쌓여요.</p>
          </div>

          <div v-else class="cards">
            <div
              v-for="(rec, i) in filtered"
              :key="rec.id"
              class="memo-card"
              :style="{ '--rotate': rotations[i % rotations.length] }"
              @click="selected = rec"
            >
              <div class="memo-date">{{ rec.date }}</div>
              <div class="memo-text">{{ rec.conclusion }}</div>
              <div class="memo-footer">内音</div>
            </div>
          </div>
        </div>

      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import { getRecords, type NaionRecord } from "../utils/records"

defineEmits(["close"])

const records = getRecords()
const selectedMonth = ref<string | null>(null)
const selected = ref<NaionRecord | null>(null)
const rotations = ["-2deg", "1.5deg", "-1deg", "2.5deg", "-1.5deg", "1deg"]

const months = computed(() => {
  const set = new Set(records.map(r => r.date.slice(0, 7)))
  return [...set].sort().reverse()
})

const filtered = computed(() =>
  records.filter(r => !selectedMonth.value || r.date.startsWith(selectedMonth.value))
)
</script>

<style scoped>
.records-overlay {
  position: fixed;
  inset: 0;
  background: rgba(44, 31, 20, 0.38);
  z-index: 100;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  backdrop-filter: blur(3px);
}

.records-panel {
  width: 100%;
  max-width: 680px;
  max-height: 88vh;
  background: #f7f3ee;
  border-radius: 20px 20px 0 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Panel transition */
.panel-enter-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.panel-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.panel-enter-from   { opacity: 0; transform: translateX(16px); }
.panel-leave-to     { opacity: 0; transform: translateX(-16px); }

.grid-view, .detail-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  max-height: 88vh;
}

/* ── 공통 헤더 ── */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e8e0d8;
  flex-shrink: 0;
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #2c1f14;
}

.back-btn {
  font-size: 13px;
  color: #a89080;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.2s;
}
.back-btn:hover { color: #6b4c2a; }

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #a89080;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
}

/* ── 월별 필터 ── */
.month-filters {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  padding: 14px 24px 8px;
  flex-shrink: 0;
}

.month-btn {
  padding: 4px 12px;
  border: 1px solid #e0d6cc;
  border-radius: 20px;
  font-size: 11px;
  color: #a89080;
  background: none;
  cursor: pointer;
  transition: all 0.2s;
}
.month-btn.active { background: #6b4c2a; color: #fffdf9; border-color: #6b4c2a; }

/* ── 빈 상태 ── */
.empty {
  text-align: center;
  padding: 60px 24px;
  color: #b0a090;
  font-size: 14px;
  line-height: 2;
}
.empty-sub { font-size: 12px; color: #c8b8a8; }

/* ── 폴라로이드 카드 ── */
.cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  padding: 20px 24px 40px;
  overflow-y: auto;
}

.memo-card {
  background: #fffef5;
  border-radius: 4px;
  padding: 20px 18px 16px;
  box-shadow:
    0 2px 4px rgba(107,76,42,0.08),
    0 6px 18px rgba(107,76,42,0.10),
    3px 3px 0 #e0d4c4;
  transform: rotate(var(--rotate));
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  background-image: repeating-linear-gradient(
    to bottom, transparent, transparent 23px, #ede8e0 23px, #ede8e0 24px
  );
  background-position: 0 36px;
  cursor: pointer;
}

.memo-card:hover {
  transform: rotate(0deg) scale(1.03);
  box-shadow:
    0 4px 8px rgba(107,76,42,0.12),
    0 12px 28px rgba(107,76,42,0.14),
    3px 3px 0 #e0d4c4;
  z-index: 1;
}

.memo-date {
  font-size: 9px;
  color: #b0a090;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
  font-family: 'Courier New', monospace;
}

.memo-text {
  font-size: 13px;
  color: #2c1f14;
  line-height: 24px;
  min-height: 48px;
  word-break: keep-all;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.memo-footer {
  margin-top: 12px;
  font-size: 9px;
  color: #c8b8a8;
  text-align: right;
  letter-spacing: 0.1em;
  font-family: 'Hiragino Mincho ProN', 'Yu Mincho', 'MS Mincho', 'STSong', serif;
}

/* ── 상세 보기 ── */
.detail-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-label {
  font-size: 10px;
  color: #b0a090;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detail-free-text {
  font-size: 13px;
  color: #5a4535;
  line-height: 1.8;
  background: #fffdf9;
  border-radius: 12px;
  padding: 14px 16px;
  border: 1px solid #e8e0d8;
  white-space: pre-wrap;
  background-image: repeating-linear-gradient(
    to bottom, transparent, transparent 27px, #ede8df 27px, #ede8df 28px
  );
  background-position: 0 14px;
}

.detail-messages {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-msg       { display: flex; }
.detail-msg.user  { justify-content: flex-end; }

.detail-bubble {
  max-width: 80%;
  padding: 9px 13px;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.detail-msg.assistant .detail-bubble {
  background: #fffdf9;
  border: 1px solid #e8e0d8;
  color: #2c1f14;
  border-radius: 4px 13px 13px 13px;
}

.detail-msg.user .detail-bubble {
  background: #6b4c2a;
  color: #fffdf9;
  border-radius: 13px 13px 4px 13px;
}

.detail-conclusion {
  font-size: 15px;
  color: #2c1f14;
  font-weight: 500;
  line-height: 1.7;
  padding: 14px 16px;
  background: #fffef5;
  border-radius: 12px;
  border-left: 3px solid #a07850;
  word-break: keep-all;
}
</style>
