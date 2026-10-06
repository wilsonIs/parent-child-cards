<script setup lang="ts"></script>

<template>
  <div class="flex h-full flex-col pb-2">
    <RouterView v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </RouterView>
  </div>
</template>
