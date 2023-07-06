<!-- @format -->
<template>
  <section v-if="hasCookie">
    <q-fab
      v-model="isShowFloatBtn"
      class="fixed-top-right q-mt-lg q-mr-lg"
      color="purple"
      square
      vertical-actions-align="right"
      icon="keyboard_arrow_left"
      direction="left"
    >
      <q-fab-action
        label-class="bg-grey-3 text-dark"
        external-label
        label-position="bottom"
        color="orange"
        icon="undo"
        label="Back"
        to="/handover"
      />
      <q-fab-action
        label-class="bg-grey-3 text-dark"
        external-label
        label-position="bottom"
        color="primary"
        icon="table_view"
        label="Table"
        @click.prevent="reviewTable"
      />
      <q-fab-action
        label-class="bg-grey-3 text-dark"
        external-label
        label-position="bottom"
        color="secondary"
        icon="send"
        label="Send"
        :loading="isSending"
        :disable="isSending"
        @click.prevent="confirmToSendTheHandover"
      />
      <!-- <q-fab-action
        label-class="bg-grey-3 text-dark"
        external-label
        label-position="bottom"
        color="secondary"
        icon="send"
        label="Send"
        :disable="isSendButton"
        @click.prevent="confirmToSendTheHandover"
      /> -->
    </q-fab>
    <div class="q-px-lg q-py-md" v-html="ReviewHtml"></div>
    <q-inner-loading
      :showing="isSending"
      label="Please wait..."
      label-class="text-teal"
      label-style="font-size: 1.1em"
    />
    <q-fab
      v-model="isShowFileButton"
      class="fixed-bottom-right q-mb-lg q-mr-lg"
      label-class="bg-grey-3 text-purple"
      color="teal"
      square
      vertical-actions-align="right"
      icon="keyboard_arrow_left"
      direction="left"
    >
      <q-fab-action
        v-for="(item, index) in hyperList"
        :key="index"
        color="primary"
        @click.prevent="attachmentOpen(item[2])"
        :icon="defineAttachmentImage(item[1])"
        :label="'[' + item[3] + '] ' + item[0]"
        square
      />
      <q-fab-action label-position="top" color="teal" label="Attachments" square />
    </q-fab>
  </section>
  <section v-else>
    <div class="row justify-center q-pa-lg q-ma-lg borders-radius-inherit">
      <div class="col-3 column q-pt-md q-pb-lg customLoginWarningBorder rounded-borders">
        <span class="text-h2 col text-center text-red"><q-icon name="gpp_maybe" /></span>
        <span class="text-h2 col text-center text-bold q-mb-lg">Please Login</span>
        <q-btn
          to="/handover"
          class="col self-center"
          rounded
          icon="login"
          color="white"
          text-color="black"
        />
      </div>
    </div>
  </section>
</template>
<script>
import { defineComponent, ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default defineComponent({
  name: 'DHSConfirmPage',
  setup() {
    const $q = useQuasar()
    const $store = useStore()
    const $router = useRouter()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const hasCookie = $q.cookies.has('handoverEditor')
    const messageSet = reactive({
      date: '',
      shift: '',
      title: '',
      step: 2,
      // denySend: true,
      wholeMessage: computed(() => {
        return `Are you sure to send ${messageSet.title}`
      }),
      labelName: computed(() => {
        if (messageSet.step === 1) {
          return 'Check'
        } else {
          return 'Send'
        }
      })
    })
    const ReviewHtml = ref('')
    const isShowFloatBtn = ref(true)
    const isShowFileButton = ref(false)
    const isSendButton = ref(false)
    const isSending = ref(false)
    // store attachment hyperlink
    const hyperList = ref()

    if (hasCookie) {
      // means user already login
      axios
        .get(`https://${ServiceDomainLocal}:9487/bpEmail/exportword`)
        .then((response) => {
          console.log(response)
          ReviewHtml.value = response.data[0]
          messageSet.title = response.data[3]
          messageSet.date = response.data[4]
          messageSet.shift = response.data[5]
          if (response.data[1]) {
            isShowFileButton.value = true
            hyperList.value = response.data[2]
          } else {
            isShowFileButton.value = false
          }
          console.log(messageSet)
        })
        .catch((error) => {
          console.log(error)
        })
    }

    // click attachment button and open new page to see the attachment
    function attachmentOpen(attachmentSn) {
      window.open(
        `https://${ServiceDomainLocal}:9487/bpNote/attachment/get/${attachmentSn}`,
        '_blank'
      )
      isShowFileButton.value = true
    }

    function confirmToSendTheHandover() {
      $q.dialog({
        title: 'Confirm',
        message: messageSet.wholeMessage,
        ok: {
          push: true,
          label: messageSet.labelName
        },
        cancel: true,
        persistent: true,
        html: true
      })
        .onOk(() => {
          if (messageSet.step === 1) {
            window.open(
              `http://10.7.6.199/handover/confirm_check_ticket.php?date=${messageSet.date}&shift=${messageSet.shift}`,
              '_blank'
            )
            messageSet.step = 2
            confirmToSendTheHandover()
          } else if (messageSet.step === 2) {
            sendHandover()
          }
        })
        .onCancel(() => {
          // console.log('>>>> Cancel')
        })
        .onDismiss(() => {
          // console.log('I am triggered on both OK and Cancel')
        })
    }

    function sendHandover() {
      // disable the send button
      isSendButton.value = true
      // show the loadding
      isSending.value = true
      // do the send on backend
      const postData = reactive({
        sender: $q.cookies.get('handoverEditor')
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/bpEmail/export`, postData)
        .then((res) => {
          console.log(res)
          isSending.value = false
          isSendButton.value = false
          $q.notify({
            message: '<b>Send Handover Success !</b>',
            color: 'green-6',
            progress: true,
            html: true,
            actions: [
              {
                icon: 'cancel',
                color: 'white',
                handler: () => {
                  $router.push('/handover')
                }
              }
            ]
          })
          $router.push('/handover')
        })
        .catch((error) => {
          console.log(error)
          isSending.value = false
          isSendButton.value = false
          $q.notify({
            message: `<b>Send Handover Failed, Due To ${error} !</b>`,
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
        })
    }

    async function reviewTable() {
      const res = await axios.get(`https://${ServiceDomainLocal}:9487/bpEmail/export`)
      $q.dialog({
        message: res.data,
        html: true,
        style: 'height: 600px; width: 1200px !important; max-width: 1200px !important'
      })
    }

    function defineAttachmentImage(fileType) {
      switch (fileType) {
        case 'docx':
          return 'far fa-file-word'
        case 'xlsx':
        case 'csv':
          return 'far fa-file-excel'
        case 'pptx':
          return 'far fa-file-powerpoint'
        case 'txt':
          return 'text_snippet'
        case 'pdf':
          return 'far fa-file-pdf'
        case 'rar':
        case 'zip':
          return 'far fa-file-archive'
        default:
          return 'image'
      }
    }

    function triggerWindowOpen() {
      console.log('hit triggerWindowOpen')
    }

    return {
      hasCookie,
      ReviewHtml,
      isShowFloatBtn,
      isShowFileButton,
      isSendButton,
      reviewTable,
      hyperList,
      attachmentOpen,
      sendHandover,
      isSending,
      confirmToSendTheHandover,
      defineAttachmentImage,
      messageSet,
      triggerWindowOpen
    }
  }
})
</script>

<style lang="scss">
div.customLoginWarningBorder {
  border: solid;
}
</style>
