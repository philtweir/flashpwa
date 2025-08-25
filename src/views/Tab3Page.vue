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
          <ion-title size="large">Clásal Coibhneasta</ion-title>
        </ion-toolbar>
      </ion-header>

      <ion-button expand="full" @click="loadNext">Next</ion-button>

      <ClasalCoibhneastaContainer
          v-if="currentItem"
          :data="currentItem"
          :challengeType="challengeType"
          :selectedSubitem="selectedSubitem"
      />
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { IonButton, IonButtons, IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/vue';
import ClasalCoibhneastaContainer from '@/components/ClasalCoibhneastaContainer.vue';
import InstallButton from '@/components/InstallButton.vue';

const examplesData = ref<any[]>([]);
const currentItem = ref<any>(null);
const challengeType = ref<string>('');
const selectedSubitem = ref<any>(null);

const loadNext = () => {
  if (examplesData.value.length === 0) return;
  
  // Select a random item from the data
  const randomIndex = Math.floor(Math.random() * examplesData.value.length);
  currentItem.value = examplesData.value[randomIndex];
  
  // Select a random subitem (excluding "Unchanged")
  const subitems = currentItem.value.filter((item: any) => item[0] !== 'Unchanged');
  const randomSubitemIndex = Math.floor(Math.random() * subitems.length);
  selectedSubitem.value = subitems[randomSubitemIndex];
  challengeType.value = selectedSubitem.value[0];
};

onMounted(async () => {
  try {
    const response = await fetch('/flashpwa/python/examples.json');
    examplesData.value = await response.json();
    loadNext();
  } catch (error) {
    console.error('Failed to load examples data:', error);
  }
});
</script>
