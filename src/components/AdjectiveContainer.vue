<template>
  <div id="container">
    <ion-card @click="toggleContent">
      <ion-card-header>
        <ion-card-content>
          <p>{{ prefix }}</p>
          <p>&plus;</p>
          <p>{{ article }} {{ noun }}</p>
          <p>&plus;</p>
          <p>{{ adjective }}</p>
        </ion-card-content>
      </ion-card-header>

      <Transition name="bounce">
        <ion-card-content class="breakdown" v-if="isContentShown">
          <span class="prefix">{{ prefix }}</span>&nbsp;
          <span class="mut-1">{{ articleMut }}</span>&nbsp;
          <span class="mut-2">{{ nounMutFront }}</span>
          <span class="noun-body">{{ nounMutMid }}</span>
          <span class="mut-3">{{ nounMutBack }}</span>&nbsp;
          <span class="mut-4">{{ adjMutFront }}</span>
          <span class="adj-body">{{ adjMutMid }}</span>
          <span class="mut-5">{{ adjMutBack }}</span>
        </ion-card-content>
      </Transition>
    </ion-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  IonCard,
  IonCardHeader,
  IonCardContent,
} from '@ionic/vue';

const isContentShown = ref(false);

const props = defineProps({
  prefix: String,
  article: String,
  articleMut: String,
  noun: String,
  nounMutFront: String,
  nounMutMid: String,
  nounMutBack: String,
  adjective: String,
  adjMutFront: String,
  adjMutMid: String,
  adjMutBack: String,
});

watch(() => props.name, () => { isContentShown.value = false });

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

.breakdown {
  font-size: 150%
}

.mut-1 {
  font-weight: bold
}

.mut-2 {
  font-weight: bold
}

.mut-3 {
  font-weight: bold
}

.mut-4 {
  font-weight: bold
}

.mut-5 {
  font-weight: bold
}
</style>
