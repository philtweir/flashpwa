<template>
  <ion-button 
    v-if="canInstall" 
    @click="installApp"
    fill="clear" 
    size="small"
    class="install-button"
  >
    <ion-icon :icon="downloadOutline" slot="start"></ion-icon>
    Install
  </ion-button>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { IonButton, IonIcon } from '@ionic/vue'
import { downloadOutline } from 'ionicons/icons'

const canInstall = ref(false)
const deferredPrompt = ref<any>(null)

const handleBeforeInstallPrompt = (event: Event) => {
  // Prevent the mini-infobar from appearing on mobile
  event.preventDefault()
  
  // Save the event so it can be triggered later
  deferredPrompt.value = event
  canInstall.value = true
}

const handleAppInstalled = () => {
  // Hide the install button after installation
  canInstall.value = false
  deferredPrompt.value = null
  console.log('PWA was installed')
}

const installApp = async () => {
  if (!deferredPrompt.value) {
    return
  }

  // Show the install prompt
  deferredPrompt.value.prompt()

  // Wait for the user to respond to the prompt
  const { outcome } = await deferredPrompt.value.userChoice
  
  if (outcome === 'accepted') {
    console.log('User accepted the install prompt')
  } else {
    console.log('User dismissed the install prompt')
  }

  // Clear the deferredPrompt
  deferredPrompt.value = null
  canInstall.value = false
}

const checkIfInstalled = () => {
  // Check if app is already installed (running in standalone mode)
  if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
    canInstall.value = false
    return true
  }
  
  // Check if launched from home screen on iOS
  if ((window.navigator as any).standalone === true) {
    canInstall.value = false
    return true
  }
  
  return false
}

onMounted(() => {
  // Don't show install button if already installed
  if (checkIfInstalled()) {
    return
  }

  // Listen for the beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  
  // Listen for the appinstalled event
  window.addEventListener('appinstalled', handleAppInstalled)
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.removeEventListener('appinstalled', handleAppInstalled)
})
</script>

<style scoped>
.install-button {
  --color: #ffffff;
  --background: transparent;
  --background-hover: rgba(255, 255, 255, 0.1);
  margin: 0;
  font-size: 14px;
}

.install-button ion-icon {
  font-size: 16px;
}

@media (max-width: 768px) {
  .install-button {
    font-size: 12px;
  }
  
  .install-button ion-icon {
    font-size: 14px;
  }
}
</style>