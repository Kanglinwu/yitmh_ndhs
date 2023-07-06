<!-- @format -->
<template>
  <q-ajax-bar
    ref="axiosExecuteBar"
    position="bottom"
    color="secondary"
    size="10px"
    skip-hijack
  />
  <div class="row">
    <span class="col-12 row q-ma-none q-pa-none q-pt-md q-px-md">
      <section class="col bg-orange-1 q-px-md q-mx-xs">
        <div class="text-italic text-center q-my-xs">Filter OTRS handler</div>
        <div>
          <q-btn
            size="sm"
            class="text-center full-width"
            color="white"
            text-color="primary"
            label="Reset All"
            icon="restart_alt"
            @click="group = ''"
          />
        </div>
        <q-option-group
          class="q-pa-md"
          v-model="group"
          :options="dbaPeopleList"
          color="green"
          inline
        />
      </section>
      <section class="col bg-indigo-1 q-px-md q-mx-xs">
        <div class="text-italic text-center q-my-xs">Misc OTRS function</div>
        <q-btn
          size="sm"
          class="text-center full-width q-mb-xs"
          color="white"
          text-color="primary"
          label="Expanded All"
          icon="keyboard_arrow_down"
          @click="expandedStatus = true"
        />
        <q-btn
          size="sm"
          class="text-center full-width q-mb-xs"
          color="white"
          text-color="primary"
          label="Reset All"
          icon="keyboard_arrow_up"
          @click="expandedStatus = false"
        />
        <q-btn
          size="sm"
          class="text-center full-width"
          color="white"
          text-color="primary"
          :label="'Pull Local DB - Auto sync after ' + countdown + ' seconds ..'"
          icon="sync"
          @click="pullJSMandSyncLocalDb"
        />
      </section>
    </span>
  </div>
  <DHSDbaOTRSList
    @triggerByJsmList="triggerChange"
    v-for="item in sortTicketSet"
    :key="item.sn"
    v-bind="item"
    :expandedStatus="expandedStatus"
  />
</template>
<script>
import DHSDbaOTRSList from 'components/DHSDbaOTRSList.vue'

import {
  defineComponent,
  onMounted,
  onBeforeUnmount,
  reactive,
  computed,
  ref,
  watch
} from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import _ from 'lodash'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'DHSDBAOTRSPage',
  components: { DHSDbaOTRSList },
  setup() {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const ticketSet = reactive({})
    const axiosExecuteBar = ref(null)
    const sortTicketSet = computed(() => _.orderBy(ticketSet, 'sn', ['desc'])) // order by noteSet.sequence

    const countdown = ref(120)
    const countdownTimer = setInterval(() => {
      --countdown.value
    }, 1000)

    const dbaPeopleList = [
      {
        label: 'David Tung',
        value: 'David Tung'
      },
      {
        label: 'Tony Wu',
        value: 'Tony Wu'
      },
      {
        label: 'Albert Huang',
        value: 'Albert Huang'
      },
      {
        label: 'Robert Lin',
        value: 'Robert Lin'
      },
      {
        label: 'Stanley Chen',
        value: 'Stanley Chen'
      },
      {
        label: 'Demon Wu',
        value: 'Demon Wu'
      },
      {
        label: 'Carny Chou',
        value: 'Carny Chou'
      },
      {
        label: 'Austin Chang',
        value: 'Austin Chang'
      },
      {
        label: 'William Liu',
        value: 'William Liu'
      }
    ]

    const group = ref()
    const expandedStatus = ref(false)

    function triggerChange(passObject) {
      // passObject = {target: jsmSn, issueId: OTRS ticket number}
      console.log(passObject)
      axios
        .get(
          `https://${ServiceDomainLocal}:9487/bpCowork/otrs/query/dba/${passObject.target}`
        )
        .then((response) => {
          console.log(response.data)
          ticketSet[passObject.issueId].description = response.data.description
          ticketSet[passObject.issueId].comments = response.data.comments
          ticketSet[passObject.issueId].status = response.data.status
          ticketSet[passObject.issueId].custom_handler = response.data.custom_handler
          ticketSet[passObject.issueId].custom_participant =
            response.data.custom_participant
          ticketSet[passObject.issueId].custom_category = response.data.custom_category
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function syncLocalDb(source) {
      countdown.value = 120
      const compareList = ref([])
      axios
        .get(`https://${ServiceDomainLocal}:9487/bpCowork/otrs/query/dba/OPEN`)
        .then((response) => {
          // when remote length is small than browser length, means user close the ticket, so need to find it
          if (response.data.length < Object.keys(ticketSet).length) {
            response.data.forEach((ele) => {
              compareList.value.push(ele.ticketNumber) // update the compare list
              ticketSet[ele.ticketNumber] = ele
            })
            Object.values(ticketSet).forEach(function (ele, index, object) {
              if (compareList.value.includes(ele.ticketNumber) === false) {
                delete ticketSet[ele.ticketNumber]
              }
            })
          } else {
            response.data.forEach((ele) => {
              ticketSet[ele.ticketNumber] = ele
              ticketSet[ele.ticketNumber].displayNameInclude = true
            })
          }
          if (source === 'initiative') {
            $q.notify({
              message: 'browser pull local DB successful',
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
          }
        })
        .catch((error) => {
          $q.notify({
            message: `browser pull local DB failed, reason - ${error.response.data}`,
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

    async function pullJSMandSyncLocalDb() {
      syncLocalDb('initiative')
      // const barRef = axiosExecuteBar.value // for loading bar
      // barRef.start() // start load
      // // request worklog server to pull the current JSM ticket
      // try {
      //   await axios.get(`https://${ServiceDomainLocal}:9487/bpRoutine/jsm/pull/dba`)
      //   $q.notify({
      //     message: 'Worklog server pull JSM ticket successful',
      //     color: 'green-6',
      //     progress: true,
      //     html: true,
      //     actions: [
      //       {
      //         icon: 'cancel',
      //         color: 'white',
      //         handler: () => {}
      //       }
      //     ]
      //   })
      //   syncLocalDb('initiative')
      //   barRef.stop()
      // } catch (e) {
      //   $q.notify({
      //     message: `Worklog server pull JSM ticket failed, reason - ${e.response.data}`,
      //     color: 'red-6',
      //     progress: true,
      //     html: true,
      //     actions: [
      //       {
      //         icon: 'cancel',
      //         color: 'white',
      //         handler: () => {}
      //       }
      //     ]
      //   })
      //   barRef.stop()
      // }
    }

    onMounted(async () => {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/bpCowork/otrs/query/dba/OPEN`)
        .then((response) => {
          response.data.forEach((ele) => {
            ticketSet[ele.ticketNumber] = ele
            ticketSet[ele.ticketNumber].displayNameInclude = true
          })
        })
        .catch((error) => {
          console.log(error)
        })
    })

    onBeforeUnmount(() => {
      clearInterval(countdownTimer)
    })

    watch(
      () => countdown.value,
      (curValue, oldValue) => {
        if (curValue === 0) {
          syncLocalDb()
        }
      }
    )

    watch(
      () => group.value,
      (curList, oldList) => {
        Object.values(ticketSet).forEach(function (ele, index, object) {
          if (curList !== '') {
            if (!ele.custom_handler.includes(curList)) {
              ticketSet[ele.ticketNumber].displayNameInclude = false
            } else {
              ticketSet[ele.ticketNumber].displayNameInclude = true
            }
          } else {
            ticketSet[ele.ticketNumber].displayNameInclude = true
          }
        })
      }
    )

    return {
      sortTicketSet,
      triggerChange,
      countdown,
      syncLocalDb,
      axiosExecuteBar,
      dbaPeopleList,
      group,
      pullJSMandSyncLocalDb,
      expandedStatus
    }
  }
})
</script>
