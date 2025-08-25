<template>
  <div id="container">
    <ion-card @click="toggleContent">
      <ion-card-header>
        <ion-card-content>
          <p class="challenge-type">{{ challengeType }}</p>
          <div class="word-display">
            <p class="verb-root">{{ verbRoot }}</p>
            <p v-for="word in displayWordsWithTags" :key="word.tag" :class="`tag-${word.tag}`">{{ word.text }}</p>
          </div>
          <p class="phrase" v-html="displayPhrase"></p>
          <p class="template-phrase" v-html="templatePhrase"></p>
        </ion-card-content>
      </ion-card-header>

      <Transition name="bounce">
        <ion-card-content class="answer" v-if="isContentShown">
          <p v-html="answerPhrase"></p>
        </ion-card-content>
      </Transition>
    </ion-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  IonCard,
  IonCardHeader,
  IonCardContent,
} from '@ionic/vue';

const isContentShown = ref(false);

const props = defineProps({
  data: Object,
  challengeType: String,
  selectedSubitem: Object,
});

watch(() => props.data, () => { isContentShown.value = false });

const toggleContent = () => {
  isContentShown.value = !isContentShown.value;
}

// Color palette for tags
const tagColors: Record<string, string> = {
  'D0': '#e74c3c', // red
  'I0': '#3498db', // blue
  'D1': '#2ecc71', // green
  'I1': '#f39c12', // orange
  'D2': '#9b59b6', // purple
  'I2': '#1abc9c', // teal
  'D3': '#e67e22', // dark orange
  'I3': '#34495e', // dark gray
};

const getTagColor = (tag: string) => {
  return tagColors[tag] || '#95a5a6'; // default gray if tag not in palette
};

const verbRoot = computed(() => {
  if (!props.selectedSubitem) return '';
  const subitemData = props.selectedSubitem[1];
  return subitemData._root || '';
});

const displayWordsWithTags = computed(() => {
  if (!props.selectedSubitem) return [];
  const words: Array<{text: string, tag: string}> = [];
  const subitemData = props.selectedSubitem[1];
  
  // Extract D0, I0, etc. keys and get the first element with tag info
  Object.keys(subitemData)
    .filter(key => key !== '_root' && key !== '_coded' && subitemData[key] && Array.isArray(subitemData[key]))
    .sort() // Sort to ensure consistent order
    .forEach(key => {
      words.push({
        text: subitemData[key][0],
        tag: key
      });
    });
  
  return words;
});

const displayPhrase = computed(() => {
  if (!props.data) return '';
  
  // Find the "Unchanged" item
  const unchangedItem = props.data.find(item => item[0] === 'Unchanged');
  if (!unchangedItem) return '';
  
  const unchangedData = unchangedItem[1];
  let phrase = unchangedData._coded;
  
  // Replace placeholders with colored versions
  Object.keys(unchangedData).forEach(key => {
    if (key !== '_root' && key !== '_coded' && unchangedData[key] && Array.isArray(unchangedData[key])) {
      const placeholder = `\${${key}}`;
      const color = getTagColor(key);
      const replacement = `<span style="color: ${color}; font-weight: bold;">${unchangedData[key][1]}</span>`;
      phrase = phrase.replace(placeholder, replacement);
    }
  });
  
  return phrase;
});

const templatePhrase = computed(() => {
  if (!props.selectedSubitem) return '';
  
  const subitemData = props.selectedSubitem[1];
  const shapes: string[] = [];
  
  // Extract tags in order from the _coded phrase
  const codedPhrase = subitemData._coded;
  const tagPattern = /\$\{([DI]\d+)\}/g;
  let match;
  
  while ((match = tagPattern.exec(codedPhrase)) !== null) {
    const tag = match[1];
    const color = getTagColor(tag);
    // Use different shapes for D (direct) and I (indirect) tags
    const shape = tag.startsWith('D') ? 'circle' : 'square';
    shapes.push(`<span class="shape ${shape}" style="background-color: ${color};"></span>`);
  }
  
  // Join shapes with arrows
  return shapes.join(' <span class="arrow">→</span> ');
});

const answerPhrase = computed(() => {
  if (!props.selectedSubitem) return '';
  
  const subitemData = props.selectedSubitem[1];
  let phrase = subitemData._coded;
  
  // Replace placeholders with colored versions
  Object.keys(subitemData).forEach(key => {
    if (key !== '_root' && key !== '_coded' && subitemData[key] && Array.isArray(subitemData[key])) {
      const placeholder = `\${${key}}`;
      const color = getTagColor(key);
      const replacement = `<span style="color: ${color}; font-weight: bold;">${subitemData[key][1]}</span>`;
      phrase = phrase.replace(placeholder, replacement);
    }
  });
  
  return phrase;
});
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

.challenge-type {
  font-size: 20px;
  font-weight: bold;
  color: #3880ff;
  margin-bottom: 15px;
}

.word-display {
  margin: 15px 0;
}

.word-display p {
  display: block;
  margin: 5px 0;
  font-size: 16px;
  font-weight: bold;
}

.verb-root {
  color: #222;
  font-style: italic;
}

/* Tag-specific colors */
.tag-D0 { color: #e74c3c; }
.tag-I0 { color: #3498db; }
.tag-D1 { color: #2ecc71; }
.tag-I1 { color: #f39c12; }
.tag-D2 { color: #9b59b6; }
.tag-I2 { color: #1abc9c; }
.tag-D3 { color: #e67e22; }
.tag-I3 { color: #34495e; }

.phrase {
  font-size: 20px;
  line-height: 30px;
  color: #222;
  margin-top: 20px;
  padding-bottom: 20px;
}

.answer {
  font-size: 20px;
  line-height: 30px;
  padding: 20px;
}

:deep(.highlight) {
  color: #3880ff;
  font-weight: bold;
}

.template-phrase {
  display: inline-block;
  font-size: 20px;
  line-height: 30px;
  color: #222;
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

:deep(.shape) {
  display: inline-block;
  width: 20px;
  height: 20px;
  margin: 0 4px;
  vertical-align: middle;
}

:deep(.shape.circle) {
  border-radius: 50%;
}

:deep(.shape.square) {
  border-radius: 3px;
}

:deep(.arrow) {
  font-size: 24px;
  color: #666;
  margin: 0 8px;
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
