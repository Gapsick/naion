<template>
  <div class="desktop-wrapper">
    <div class="phone-frame">
      <div class="phone-screen">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router"
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f7f3ee;
}

/* 모바일: 프레임 없이 풀스크린 */
.desktop-wrapper { width: 100%; height: 100dvh; display: flex; }
.phone-frame { width: 100%; height: 100%; display: flex; flex-direction: column; }
.phone-screen { width: 100%; height: 100%; overflow: hidden; position: relative; }

/* 데스크탑: 폰 프레임 */
@media (min-width: 768px) {
  body {
    background: #e8e0d8;
  }

  .desktop-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100dvh;
  }

  .phone-frame {
    width: min(390px, 46vh);
    height: min(844px, 92vh);
    background: #1a1a1a;
    border-radius: 52px;
    padding: 14px;
    box-shadow:
      0 0 0 2px #3a3a3a,
      0 30px 80px rgba(0,0,0,0.4),
      inset 0 0 0 1px #2a2a2a;
    position: relative;
  }

  /* 상단 노치 */
  .phone-frame::before {
    content: '';
    position: absolute;
    top: 14px;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 34px;
    background: #1a1a1a;
    border-radius: 0 0 20px 20px;
    z-index: 10;
  }

  /* 사이드 버튼들 */
  .phone-frame::after {
    content: '';
    position: absolute;
    right: -4px;
    top: 160px;
    width: 4px;
    height: 70px;
    background: #3a3a3a;
    border-radius: 0 3px 3px 0;
    box-shadow: 0 90px 0 #3a3a3a;
  }

  .phone-screen {
    width: 100%;
    height: 100%;
    border-radius: 42px;
    overflow: hidden;
    background: #f7f3ee;
  }
}
</style>
