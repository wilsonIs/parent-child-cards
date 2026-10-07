import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/home' },
  {
    path: '/home',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/eat',
    name: 'eat',
    component: () => import('@/views/EatView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/story',
    name: 'story',
    component: () => import('@/views/StoryView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/story/:id',
    name: 'story-player',
    component: () => import('@/views/StoryPlayerView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/series/:name',
    name: 'series',
    component: () => import('@/views/SeriesView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/play',
    name: 'play',
    component: () => import('@/views/PlayView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/play/:scene',
    name: 'play-scene',
    component: () => import('@/views/PlaySceneView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/learn',
    name: 'learn',
    component: () => import('@/views/LearnView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/poems',
    name: 'poems',
    component: () => import('@/views/PoemsView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/today',
    name: 'today',
    component: () => import('@/views/TodayView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('@/views/FavoritesView.vue'),
    meta: { keepAlive: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { keepAlive: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/home' },
]

export const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})
