<template>
  <div id="container">
    <ion-card @click="toggleContent">
      <ion-card-header>
        <ion-card-title>{{ name }}</ion-card-title>
        <ion-card-title>{{ conjugate }}</ion-card-title>
      </ion-card-header>

      <Transition name="bounce">
        <ion-card-content v-if="isContentShown">
          {{ answer }}
        </ion-card-content>
      </Transition>
    </ion-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  IonCard,
  IonCardTitle,
  IonCardHeader,
  IonCardContent,
} from '@ionic/vue';

const isContentShown = ref(false);

defineProps({
  name: String,
  conjugate: String,
  answer: String,
});

const toggleContent = () => {
  isContentShown.value = !isContentShown.value;
}
</script>

<style scoped>
#container {
  text-align: center;
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}

#container strong {
  font-size: 20px;
  line-height: 26px;
}

#container p {
  font-size: 16px;
  line-height: 22px;
  color: #8c8c8c;
  margin: 0;
}

#container a {
  text-decoration: none;
}

.bounce-enter-active {
  animation: bounce-in 0.5s;
}

.bounce-leave-active {
  animation: bounce-in 0.5s reverse;
}

@keyframes bounce-in {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.25);
  }
  100% {
    transform: scale(1);
  }
}
</style>
