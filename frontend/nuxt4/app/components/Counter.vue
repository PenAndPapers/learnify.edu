<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  initialValue?: number
  min?: number
  max?: number
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  initialValue: 0,
  min: -Infinity,
  max: Infinity,
  label: 'Count',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void
  (e: 'increment', value: number): void
  (e: 'decrement', value: number): void
}>()

const count = ref(props.initialValue)

const canIncrement = computed(() => count.value < props.max)
const canDecrement = computed(() => count.value > props.min)

function increment() {
  if (canIncrement.value) {
    count.value++
    emit('update:modelValue', count.value)
    emit('increment', count.value)
  }
}

function decrement() {
  if (canDecrement.value) {
    count.value--
    emit('update:modelValue', count.value)
    emit('decrement', count.value)
  }
}

function reset() {
  count.value = props.initialValue
  emit('update:modelValue', count.value)
}

defineExpose({
  count,
  increment,
  decrement,
  reset,
})
</script>

<template>
  <div class="counter" role="group" :aria-label="`${label} counter`">
    <div class="counter__label">{{ label }}</div>

    <div class="counter__value" :data-testid="'counter-value'">{{ count }}</div>

    <div class="counter__controls">
      <button
        type="button"
        class="counter__btn counter__btn--decrement"
        :disabled="!canDecrement"
        :aria-label="`Decrement ${label}`"
        data-testid="counter-decrement"
        @click="decrement"
      >
        &minus;
      </button>

      <button
        type="button"
        class="counter__btn counter__btn--reset"
        :aria-label="`Reset ${label}`"
        data-testid="counter-reset"
        @click="reset"
      >
        Reset
      </button>

      <button
        type="button"
        class="counter__btn counter__btn--increment"
        :disabled="!canIncrement"
        :aria-label="`Increment ${label}`"
        data-testid="counter-increment"
        @click="increment"
      >
        +
      </button>
    </div>
  </div>
</template>
