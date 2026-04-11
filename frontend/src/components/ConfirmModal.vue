<template>
  <Transition name="modal">
    <div v-if="show" class="modal-overlay">
      <div class="modal-card">
        <p class="modal-message">{{ message }}</p>
        <div class="modal-actions">
          <button class="modal-cancel" @click="$emit('cancel')">취소</button>
          <button class="modal-confirm" @click="$emit('confirm')">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
defineProps<{ show: boolean; message: string; confirmText?: string }>()
defineEmits(["confirm", "cancel"])
</script>

<style scoped>
.modal-overlay {
  position: absolute; inset: 0;
  background: rgba(44, 31, 20, 0.45);
  z-index: 200;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(2px);
}

.modal-card {
  background: #fffdf9;
  border-radius: 16px;
  padding: 24px 20px 18px;
  width: 80%;
  max-width: 280px;
  box-shadow: 0 8px 32px rgba(44, 31, 20, 0.18);
  display: flex; flex-direction: column; gap: 20px;
}

.modal-message {
  font-size: 14px; color: #2c1f14;
  line-height: 1.6; text-align: center;
  white-space: pre-line;
}

.modal-actions {
  display: flex; gap: 8px;
}

.modal-cancel {
  flex: 1; padding: 10px;
  background: #f0ebe4; border: none;
  border-radius: 10px; font-size: 13px;
  color: #a89080; cursor: pointer; transition: background 0.2s;
}
.modal-cancel:hover { background: #e8e0d8; }

.modal-confirm {
  flex: 1; padding: 10px;
  background: #6b4c2a; border: none;
  border-radius: 10px; font-size: 13px;
  color: #fffdf9; cursor: pointer; transition: background 0.2s;
}
.modal-confirm:hover { background: #5a3e22; }

.modal-enter-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.modal-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.modal-enter-from { opacity: 0; transform: scale(0.95); }
.modal-leave-to   { opacity: 0; transform: scale(0.95); }
</style>
