import { createRouter, createWebHistory } from "vue-router"
import ChatView from "../views/ChatView.vue"
import LoginView from "../views/LoginView.vue"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/",      component: ChatView,  meta: { requiresAuth: true } },
    { path: "/login", component: LoginView },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem("naion_access_token")
  if (to.meta.requiresAuth && !token) return "/login"
})

export default router
