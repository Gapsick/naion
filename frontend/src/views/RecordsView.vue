<template>
  <div class="records-overlay" @click.self="$emit('close')">
    <div class="records-panel">
      <div class="records-header">
        <span class="records-title">내 기록</span>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div v-if="records.length === 0" class="empty">
        <p>아직 기록이 없어요.</p>
        <p class="empty-sub">대화를 마치면 여기에 쌓여요.</p>
      </div>

      <div v-else class="cards">
        <div
          v-for="(rec, i) in records"
          :key="rec.id"
          class="memo-card"
          :style="{ '--rotate': rotations[i % rotations.length] }"
        >
          <div class="memo-date">{{ rec.date }}</div>
          <div class="memo-text">{{ rec.conclusion }}</div>
          <div class="memo-footer">内音</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getRecords } from "../utils/records"

defineEmits(["close"])

const records = getRecords()
const rotations = ["-2deg", "1.5deg", "-1deg", "2.5deg", "-1.5deg", "1deg"]
</script>

<style scoped>
.records-overlay {
  position: fixed;
  inset: 0;
  background: rgba(44, 31, 20, 0.4);
  z-index: 100;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.records-panel {
  width: 100%;
  max-width: 680px;
  max-height: 85vh;
  background: #f7f3ee;
  border-radius: 20px 20px 0 0;
  padding: 24px 24px 40px;
  overflow-y: auto;
}

.records-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.records-title {
  font-size: 15px;
  font-weight: 600;
  color: #2c1f14;
  letter-spacing: 0.04em;
}

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #a89080;
  cursor: pointer;
  padding: 4px 8px;
}

.empty {
  text-align: center;
  padding: 60px 0;
  color: #b0a090;
  font-size: 14px;
  line-height: 2;
}

.empty-sub {
  font-size: 12px;
  color: #c8b8a8;
}

.cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 8px 4px;
}

.memo-card {
  background: #fffef5;
  border-radius: 4px;
  padding: 20px 18px 16px;
  box-shadow:
    0 2px 4px rgba(107,76,42,0.08),
    0 6px 16px rgba(107,76,42,0.10),
    3px 3px 0 #e8ddd0;
  transform: rotate(var(--rotate));
  transition: transform 0.2s;
  background-image: repeating-linear-gradient(
    to bottom,
    transparent,
    transparent 23px,
    #ede8e0 23px,
    #ede8e0 24px
  );
  background-position: 0 36px;
  cursor: default;
}

.memo-card:hover {
  transform: rotate(0deg) scale(1.02);
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
}

.memo-footer {
  margin-top: 12px;
  font-size: 9px;
  color: #c8b8a8;
  text-align: right;
  letter-spacing: 0.1em;
}
</style>
