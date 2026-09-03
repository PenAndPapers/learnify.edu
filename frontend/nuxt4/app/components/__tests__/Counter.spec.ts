import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Counter from '../Counter.vue'

describe('Counter', () => {
  describe('default rendering', () => {
    it('renders with default initial value of 0', () => {
      const wrapper = mount(Counter)
      const valueEl = wrapper.find('[data-testid="counter-value"]')
      expect(valueEl.text()).toBe('0')
    })

    it('renders with default label "Count"', () => {
      const wrapper = mount(Counter)
      const labelEl = wrapper.find('.counter__label')
      expect(labelEl.text()).toBe('Count')
    })

    it('has three control buttons', () => {
      const wrapper = mount(Counter)
      const buttons = wrapper.findAll('button')
      expect(buttons).toHaveLength(3)
      expect(wrapper.find('[data-testid="counter-decrement"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="counter-increment"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="counter-reset"]').exists()).toBe(true)
    })
  })

  describe('custom props', () => {
    it('respects custom initialValue prop', () => {
      const wrapper = mount(Counter, {
        props: { initialValue: 5 },
      })
      const valueEl = wrapper.find('[data-testid="counter-value"]')
      expect(valueEl.text()).toBe('5')
    })

    it('renders custom label prop', () => {
      const wrapper = mount(Counter, {
        props: { label: 'Quantity' },
      })
      const labelEl = wrapper.find('.counter__label')
      expect(labelEl.text()).toBe('Quantity')
    })
  })

  describe('increment behavior', () => {
    it('increments value on + button click', async () => {
      const wrapper = mount(Counter, { props: { initialValue: 0 } })
      const incrementBtn = wrapper.find('[data-testid="counter-increment"]')
      await incrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('1')
      await incrementBtn.trigger('click')
      await incrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('3')
    })

    it('emits increment and update:modelValue events on increment', async () => {
      const wrapper = mount(Counter, { props: { initialValue: 0 } })
      await wrapper.find('[data-testid="counter-increment"]').trigger('click')

      const incrementEvents = wrapper.emitted('increment')
      expect(incrementEvents).toBeDefined()
      expect(incrementEvents && incrementEvents[0]).toEqual([1])

      const updateEvents = wrapper.emitted('update:modelValue')
      expect(updateEvents).toBeDefined()
      expect(updateEvents && updateEvents[0]).toEqual([1])
    })

    it('respects max prop and disables increment button', () => {
      const wrapper = mount(Counter, {
        props: { initialValue: 5, max: 5 },
      })
      const incrementBtn = wrapper.find('[data-testid="counter-increment"]')
      expect(incrementBtn.attributes('disabled')).toBeDefined()
    })

    it('does not increment past max value', async () => {
      const wrapper = mount(Counter, {
        props: { initialValue: 4, max: 5 },
      })
      const incrementBtn = wrapper.find('[data-testid="counter-increment"]')
      await incrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('5')
      await incrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('5')
    })
  })

  describe('decrement behavior', () => {
    it('decrements value on - button click', async () => {
      const wrapper = mount(Counter, { props: { initialValue: 5 } })
      const decrementBtn = wrapper.find('[data-testid="counter-decrement"]')
      await decrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('4')
    })

    it('emits decrement and update:modelValue events on decrement', async () => {
      const wrapper = mount(Counter, { props: { initialValue: 5 } })
      await wrapper.find('[data-testid="counter-decrement"]').trigger('click')

      const decrementEvents = wrapper.emitted('decrement')
      expect(decrementEvents).toBeDefined()
      expect(decrementEvents && decrementEvents[0]).toEqual([4])

      const updateEvents = wrapper.emitted('update:modelValue')
      expect(updateEvents).toBeDefined()
      expect(updateEvents && updateEvents[0]).toEqual([4])
    })

    it('respects min prop and disables decrement button', () => {
      const wrapper = mount(Counter, {
        props: { initialValue: 0, min: 0 },
      })
      const decrementBtn = wrapper.find('[data-testid="counter-decrement"]')
      expect(decrementBtn.attributes('disabled')).toBeDefined()
    })

    it('does not decrement below min value', async () => {
      const wrapper = mount(Counter, {
        props: { initialValue: 1, min: 0 },
      })
      const decrementBtn = wrapper.find('[data-testid="counter-decrement"]')
      await decrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('0')
      await decrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('0')
    })
  })

  describe('reset behavior', () => {
    it('resets to initialValue on reset button click', async () => {
      const wrapper = mount(Counter, { props: { initialValue: 3 } })
      const incrementBtn = wrapper.find('[data-testid="counter-increment"]')
      await incrementBtn.trigger('click')
      await incrementBtn.trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('5')

      await wrapper.find('[data-testid="counter-reset"]').trigger('click')
      expect(wrapper.find('[data-testid="counter-value"]').text()).toBe('3')
    })

    it('emits update:modelValue on reset with initialValue', async () => {
      const wrapper = mount(Counter, { props: { initialValue: 3 } })
      await wrapper.find('[data-testid="counter-increment"]').trigger('click')
      await wrapper.find('[data-testid="counter-reset"]').trigger('click')

      const emitted = wrapper.emitted('update:modelValue')
      expect(emitted).toBeDefined()
      expect(emitted && emitted[emitted.length - 1]).toEqual([3])
    })
  })
})
