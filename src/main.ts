import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import { useDataStore } from './stores/data'
import { useSettingsStore } from './stores/settings'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 启动时：应用字体偏好 + 预加载数据
const settings = useSettingsStore()
settings.applyFontSize()

const data = useDataStore()
void data.loadAll()

app.mount('#app')
