<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>GRMMA le BuNaMo 7 Gramadán</ion-title>
        <ion-buttons slot="end">
          <InstallButton />
        </ion-buttons>
      </ion-toolbar>
    </ion-header>
    <ion-content :fullscreen="true">
      <ion-header collapse="condense">
        <ion-toolbar>
          <ion-title size="large">Aidiochtaí</ion-title>
        </ion-toolbar>
      </ion-header>

      <ion-button expand="full" @click="incrementCounter" :disabled="loading || json.length === 0">
        {{ loading ? 'Loading...' : 'Next' }}
      </ion-button>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <AdjectiveContainer
          v-if="json.length > 0 && json[counter]"
          :name="json[counter].name"
          :prefix="json[counter].prefix"
          :article="json[counter].article"
          :articleMut="json[counter].articleMut"
          :noun="json[counter].noun"
          :nounMutFront="json[counter].nounMutFront"
          :nounMutMid="json[counter].nounMutMid"
          :nounMutBack="json[counter].nounMutBack"
          :adjective="json[counter].adjective"
          :adjMutFront="json[counter].adjMutFront"
          :adjMutMid="json[counter].adjMutMid"
          :adjMutBack="json[counter].adjMutBack"
      />
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { IonButton, IonButtons, IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/vue';
import AdjectiveContainer from '@/components/AdjectiveContainer.vue';
import InstallButton from '@/components/InstallButton.vue';

const json = ref<any[]>([]);
const counter = ref(0);
const loading = ref(true);
const error = ref<string | null>(null);

const incrementCounter = () => {
  if (json.value.length > 0) {
    counter.value += 1;
    if (counter.value >= json.value.length) {
      counter.value = 0;
    }
  }
};

const loadAdjectiveData = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const response = await fetch('/flashpwa/python/adjectives.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (Array.isArray(data) && data.length > 0) {
      json.value = data;
    } else {
      // Fallback to mock data if no adjectives.json or empty
      json.value = [{
        "name": "mór",
        "prefix": "i ndiaidh",
        "article": "na", 
        "articleMut": "na",
        "noun": "múinteoirí",
        "nounMutFront": "m",
        "nounMutMid": "úinteo",
        "nounMutBack": "ra",
        "adjective": "mór",
        "adjMutFront": "m",
        "adjMutMid": "ó",
        "adjMutBack": "ra",
      }];
    }
  } catch (err) {
    console.error('Failed to load adjective data:', err);
    error.value = `Failed to load data: ${err}`;
    
    // Use fallback data
    json.value = [{
      "name": "mór",
      "prefix": "i ndiaidh", 
      "article": "na",
      "articleMut": "na",
      "noun": "múinteoirí",
      "nounMutFront": "m",
      "nounMutMid": "úinteo",
      "nounMutBack": "ra", 
      "adjective": "mór",
      "adjMutFront": "m",
      "adjMutMid": "ó",
      "adjMutBack": "ra",
    }];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadAdjectiveData();
});
</script>

<style scoped>
.error-message {
  color: #e74c3c;
  padding: 20px;
  text-align: center;
  font-weight: bold;
}
</style>
