<!-- @format -->

<template>
  <q-item clickable @click="updateDbforCounter" dense>
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
      <q-item-label caption>
        {{ caption }}
      </q-item-label>
    </q-item-section>
    <q-item-section side>
      {{ counter }}
    </q-item-section>
  </q-item>
</template>

<script>
import { defineComponent, inject } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

export default defineComponent({
  name: 'EssentialLink',
  props: {
    sn: {
      type: Number
    },

    title: {
      type: String,
      required: true
    },

    caption: {
      type: String,
      default: ''
    },

    link: {
      type: String,
      default: '#'
    },

    icon: {
      type: String,
      default: ''
    },

    counter: {
      type: Number
    }
  },
  setup(props) {
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const isLogin = inject('isLogin') // get the root isLogin dict
    function updateDbforCounter() {
      const postData = {
        dbSn: props.sn,
        action: 'updateCounter'
      }
      axios
        .post(`https://${ServiceDomainLocal}:9487/hyperlink`, postData)
        .then((res) => {
          if (res.status === 200) {
            if (props.title === 'NXG route profiles') {
              const newTargetLinkForNxgProfile = `${props.link}?user=${isLogin.value}`
              window.open(newTargetLinkForNxgProfile, '_blank')
            } else {
              window.open(props.link, '_blank')
            }
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    return {
      updateDbforCounter,
      ServiceDomainLocal
    }
  }
})
</script>
