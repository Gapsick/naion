<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <h1 class="auth-title">内音</h1>
      <p class="auth-sub">나의 감정을 언어로</p>

      <div class="tabs">
        <button :class="['tab', { active: mode === 'login' }]"    @click="mode = 'login'">로그인</button>
        <button :class="['tab', { active: mode === 'register' }]" @click="mode = 'register'">회원가입</button>
      </div>

      <form @submit.prevent="submit">
        <div class="field">
          <label>닉네임</label>
          <input v-model="nickname" type="text" placeholder="나만의 이름" autocomplete="username" required />
        </div>
        <div class="field">
          <label>비밀번호</label>
          <input v-model="password" type="password" placeholder="••••••" autocomplete="current-password" required />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button class="submit-btn" type="submit" :disabled="loading">
          {{ loading ? "잠깐만요..." : mode === "login" ? "시작하기" : "가입하기" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { login, register, storeAuth } from "../api/auth"

const router = useRouter()
const mode     = ref<"login" | "register">("login")
const nickname = ref("")
const password = ref("")
const error    = ref("")
const loading  = ref(false)

async function submit() {
  error.value   = ""
  loading.value = true
  try {
    const fn   = mode.value === "login" ? login : register
    const data = await fn(nickname.value.trim(), password.value)
    storeAuth(data)
    router.push("/")
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrap {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f3ee;
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 360px;
  background: #fffdf9;
  border-radius: 20px;
  padding: 40px 32px 36px;
  box-shadow: 0 4px 24px rgba(107, 76, 42, 0.10);
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c1f14;
  text-align: center;
  font-family: 'Hiragino Mincho ProN', 'Yu Mincho', serif;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.auth-sub {
  text-align: center;
  font-size: 12px;
  color: #b0a090;
  margin-bottom: 28px;
  letter-spacing: 0.05em;
}

.tabs {
  display: flex;
  border-radius: 10px;
  background: #f0ebe4;
  padding: 3px;
  margin-bottom: 28px;
  gap: 3px;
}

.tab {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 8px;
  background: none;
  font-size: 13px;
  color: #a89080;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.tab.active {
  background: #fffdf9;
  color: #2c1f14;
  box-shadow: 0 1px 4px rgba(107, 76, 42, 0.12);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.field label {
  font-size: 11px;
  color: #a89080;
  letter-spacing: 0.05em;
}

.field input {
  padding: 11px 14px;
  border: 1px solid #e8e0d8;
  border-radius: 10px;
  font-size: 14px;
  color: #2c1f14;
  background: #f7f3ee;
  outline: none;
  transition: border-color 0.2s;
}
.field input:focus {
  border-color: #a07850;
  background: #fffdf9;
}

.error {
  font-size: 12px;
  color: #c0604a;
  text-align: center;
  margin-bottom: 12px;
}

.submit-btn {
  width: 100%;
  padding: 13px;
  background: #6b4c2a;
  color: #fffdf9;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 4px;
}
.submit-btn:hover:not(:disabled) { background: #5a3d20; }
.submit-btn:disabled { opacity: 0.55; cursor: not-allowed; }
</style>
