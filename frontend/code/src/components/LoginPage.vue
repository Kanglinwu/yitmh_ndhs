<!-- @format -->

<template>
  <q-page class="q-pa-xl bg-red-1 q-gutter-xs column">
    <q-input
      filled
      v-model="adAccount"
      label="AD Account"
      placeholder="example such as 09099.saul.goodman"
    />
    <q-input
      v-model="adPassword"
      filled
      :type="isPwd ? 'password' : 'text'"
      label="AD Password"
      v-on:keyup.enter="updateStatus"
    >
      <template v-slot:append>
        <q-icon
          :name="isPwd ? 'visibility_off' : 'visibility'"
          class="cursor-pointer"
          @click="isPwd = !isPwd"
        />
      </template>
    </q-input>
    <q-btn
      @click="updateStatus"
      color="blue-grey-10"
      text-color="blue-grey-1"
      label="Login"
    />
  </q-page>
</template>

<script>
import { defineComponent, inject, ref, reactive } from 'vue'
import { useQuasar } from 'quasar'
import { useStore } from 'vuex'
import axios from 'axios'

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const isLogin = inject('isLogin')
    const adAccount = ref('')
    const adPassword = ref('')
    const isPwd = ref(true)

    function updateStatus() {
      // console.log('hit the updateStatus function')
      // $q.cookies.set('handoverEditor', adAccount.value)
      // isLogin.value = adAccount.value
      // isLogin.status = true
      const postData = reactive({
        userAccount: adAccount.value,
        userPassword: adPassword.value
      })
      axios
        .post(`https://${ServiceDomainLocal}:9486/loginCheck`, postData)
        .then((res) => {
          console.log(res.data)
          if (res.data.status === 'success') {
            $q.notify({
              message: `Login success, username is ${res.data.user}`,
              color: 'green-6',
              progress: true,
              html: true,
              actions: [
                {
                  icon: 'cancel',
                  color: 'white',
                  handler: () => {}
                }
              ]
            })
            $q.cookies.set('handoverEditor', res.data.user)
            $q.cookies.set('handoverGroup', res.data.group)
            isLogin.value = res.data.user
            isLogin.group = res.data.group
            isLogin.status = true
          } else {
            $q.notify({
              message: `${res.data.status}`,
              color: 'red-6',
              progress: true,
              html: true,
              actions: [
                {
                  icon: 'cancel',
                  color: 'white',
                  handler: () => {}
                }
              ]
            })
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }
    return {
      updateStatus,
      isLogin,
      adAccount,
      adPassword,
      isPwd
    }
  }
})
</script>
