import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/home' },
  {
    path: '/home',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/eat',
    name: 'eat',
    component: () => import('@/views/EatView.vue'),
  },
  {
    path: '/story',
    name: 'story',
    component: () => import('@/views/StoryView.vue'),
  },
  {
    path: '/story/:id',
    name: 'story-player',
    component: () => import('@/views/StoryPlayerView.vue'),
  },
  {
    path: '/series/:name',
    name: 'series',
    component: () => import('@/views/SeriesView.vue'),
  },
  {
    path: '/play',
    name: 'play',
    component: () => import('@/views/PlayView.vue'),
  },
  {
    path: '/play/:scene',
    name: 'play-scene',
    component: () => import('@/views/PlaySceneView.vue'),
  },
  {
    path: '/learn',
    name: 'learn',
    component: () => import('@/views/LearnView.vue'),
  },
  {
    path: '/poems',
    name: 'poems',
    component: () => import('@/views/PoemsView.vue'),
  },
  {
    path: '/today',
    name: 'today',
    component: () => import('@/views/TodayView.vue'),
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('@/views/FavoritesView.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
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
