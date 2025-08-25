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
import { IonButton, IonButtons, IonPage, IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/vue';
import ExploreContainer from '@/components/ExploreContainer.vue';
import InstallButton from '@/components/InstallButton.vue';

const langMapping: Map<string, string> = new Map([
  ["Cond", "MCo."],
  ["Auto", "Saorb."],
  ["Interrog", "Cei."],
  ["Declar", "Tás."],
  ["Pos", "Dear."],
  ["Neg", "Diul."],
  ["PastCont", "Gnáthch."],
  ["Fut", "AFh."],
  ["Past", "ACh."],
  ["Pres", "AL."],
  ["Sg1", "1ph. UUa."],
  ["Sg2", "2ph. UUa."],
  ["Sg3Fem", "3ph. UUa. Bai."],
  ["Sg3Masc", "3ph. UUa. Fir."],
  ["Pl1", "1ph. UIo."],
  ["Pl2", "2ph. UIo."],
  ["Pl3", "3ph. UIo."],
  ["verbal noun", "AinmBr"],
  ["verbal adjective", "AidBr"],
])

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

interface Entry {
  name: string,
  conjugate: string,
  answer: string,
  multiplier: string,
}

const n = ref(Math.floor(Math.random() * 1000))
const getData = () => {
  fetch(`flashpwa/samples/forms-${n.value}.json`).
    then(res => res.json()).
    then((response) => {
      const translated = response.map((entry: Entry) => {
        entry["conjugate"] = langMapping.get("conjugate") || entry["conjugate"];
        const conjugate = entry["conjugate"].split(" ").map(
          term => langMapping.get(term) || term
        ).join(" ");
        return {
          ...entry,
          conjugate
        };
      });
      json.value = translated;
    });
};

getData();
</script>
