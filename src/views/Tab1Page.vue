<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Tab 1</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content :fullscreen="true">
      <ion-header collapse="condense">
        <ion-toolbar>
          <ion-title size="large">Tab 1</ion-title>
        </ion-toolbar>
      </ion-header>

      <ion-button expand="full" @click="incrementCounter">Next</ion-button>

      <ExploreContainer :name="json[counter].name" :conjugate="json[counter].conjugate" :answer="json[counter].answer" />
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { IonButton, IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/vue';
import ExploreContainer from '@/components/ExploreContainer.vue';

const json = ref([
  {
    "name": "Creid",
    "conjugate": "aimsir caite; dearfach; saorbhriathar",
    "answer": "Chreideadh"
  },
  {
    "name": "Ól",
    "conjugate": "aimsir fhaisteanach; triú phearsa; diultach; neamhspleach",
    "answer": "Ólfaidh sé"
  }
]);

const counter = ref(0);

const incrementCounter = () => {
  counter.value += 1;
  if (counter.value >= json.value.length) {
    counter.value = 0;
  }
};
</script>
