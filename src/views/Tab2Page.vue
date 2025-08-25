<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>GRMMA le BuNaMo 7 Gramadán</ion-title>
      </ion-toolbar>
    </ion-header>
    <ion-content :fullscreen="true">
      <ion-header collapse="condense">
        <ion-toolbar>
          <ion-title size="large">Aidiochtaí</ion-title>
        </ion-toolbar>
      </ion-header>

      <ion-button expand="full" @click="incrementCounter">Next</ion-button>

      <AdjectiveContainer
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
import { ref } from 'vue';
import { IonButton, IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/vue';
import AdjectiveContainer from '@/components/AdjectiveContainer.vue';

const json = ref([
  {
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
  },
]);

const counter = ref(0);

const incrementCounter = () => {
  counter.value += 1;
  if (counter.value >= json.value.length) {
    counter.value = 0;
  }
};

const getData = () => {
};

getData();
</script>
