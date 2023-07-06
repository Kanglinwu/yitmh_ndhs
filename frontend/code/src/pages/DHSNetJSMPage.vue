<!-- @format -->
<template>
  <q-ajax-bar ref="axiosExecuteBar" position="bottom" color="secondary" size="10px" skip-hijack />
  <q-dialog v-model="filterSet.isDisplayCard">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Choose the target</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="emptyFilter" />
      </q-card-section>

      <q-card-section>
        <div class="q-gutter-sm">
          <span v-for="x in filterSet.targetList" v-bind:key="x">
            <q-radio v-model="filterSet.curShape" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="x"
              :label="x" />
          </span>
        </div>
      </q-card-section>
      <q-separator />
      <q-card-section v-if="filterSet.curShape !== ''">
        <div class="q-gutter-sm" v-if="filterSet.curShape == 'handler'">
          <span v-for="y in netPeopleList" v-bind:key="y.label">
            <q-radio v-model="filterSet.curValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye"
              :val="y.value" :label="y.label" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="filterSet.curShape == 'participant'">
          <span v-for="y in netPeopleList" v-bind:key="y.label">
            <q-radio v-model="filterSet.curValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye"
              :val="y.value" :label="y.label" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="filterSet.curShape == 'category'">
          <span v-for="(value, key) in filterSet.targetCategory" v-bind:key="key">
            <q-radio v-model="filterSet.curValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye"
              :val="value" :label="value" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="filterSet.curShape == 'facilities'">
          <span v-for="(value, key) in filterSet.targetFacilities" v-bind:key="key">
            <q-radio v-model="filterSet.curValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye"
              :val="value" :label="value" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="filterSet.curShape == 'infra'">
          <span v-for="y in filterSet.targetInfra" v-bind:key="y">
            <q-radio v-model="filterSet.curValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="y"
              :label="y" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="filterSet.curShape == 'vendor'">
          <span v-for="y in filterSet.targetVendor" v-bind:key="y">
            <q-radio v-model="filterSet.curValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="y"
              :label="y" />
          </span>
        </div>
      </q-card-section>
      <q-separator />
      <q-card-section v-if="(filterSet.curShape !== '') && (filterSet.curValue !== '')">
        <div class="row justify-between">
          <q-chip class="col row" square>
            <q-avatar icon="flag" color="red" text-color="white" />
            <span class="col text-center">
              {{ filterSet.curShape }} == {{ filterSet.curValue }}
            </span>
          </q-chip>
          <q-btn color="white" text-color="black" label="Confirm" @click="targetConfirm" />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
  <div class="row">
    <span class="col-12 row q-ma-none q-pa-none q-pt-md q-px-md">
      <section class="col bg-cyan-1 q-px-md q-mx-xs">
        <div class="text-italic text-center q-my-xs">Filter by Status</div>
        <div v-if="filterTarget === 'Total'" class="cursor-pointer text-bold">
          <span> Total : </span>
          <q-badge color="yellow-6" text-color="black" :label="sortTicketSet.length" />
        </div>
        <li v-else class="q-pl-lg cursor-pointer" @click="filterTarget = 'Total'">
          <span> Total :</span>
          <span>{{ sortTicketSet.length }}</span>
        </li>
        <div v-if="filterTarget === 'InProgess'" class="cursor-pointer text-bold">
          <span> In Progess : </span>
          <q-badge color="yellow-6" text-color="black" :label="inProgressSet.length" />
        </div>
        <li v-else class="q-pl-lg cursor-pointer" @click="filterTarget = 'InProgess'">
          <span> In Progess : </span>
          <span> {{ inProgressSet.length }} </span>
        </li>
        <div v-if="filterTarget === 'Completed'" class="cursor-pointer text-bold">
          <span> Completed : </span>
          <q-badge color="yellow-6" text-color="black" :label="completedSet.length" />
        </div>
        <li v-else class="q-pl-lg cursor-pointer" @click="filterTarget = 'Completed'">
          <span> Completed : </span>
          <span> {{ completedSet.length }} </span>
        </li>
        <div v-if="filterTarget === 'Canceled'" class="cursor-pointer text-bold">
          <span> Canceled : </span>
          <q-badge color="yellow-6" text-color="black" :label="canceledSet.length" />
        </div>
        <li v-else class="q-pl-lg cursor-pointer" @click="filterTarget = 'Canceled'">
          <span> Canceled : </span>
          <span> {{ canceledSet.length }} </span>
        </li>
        <div v-if="filterTarget === 'Open'" class="cursor-pointer text-bold">
          <span> Open : </span>
          <q-badge color="yellow-6" text-color="black" :label="openSet.length" />
        </div>
        <li v-else class="q-pl-lg cursor-pointer" @click="filterTarget = 'Open'">
          <span> Open : </span>
          <span> {{ openSet.length }} </span>
        </li>
        <div v-if="filterTarget === 'Reopened'" class="cursor-pointer text-bold">
          <span> Reopened : </span>
          <q-badge color="yellow-6" text-color="black" :label="reopenSet.length" />
        </div>
        <li v-else class="q-pl-lg cursor-pointer" @click="filterTarget = 'Reopened'">
          <span> Reopened : </span>
          <span> {{ reopenSet.length }} </span>
        </li>
        <div class="q-py-xs"></div>
      </section>
      <section class="col bg-teal-1 q-px-md q-mx-xs">
        <div class="text-italic text-center q-my-xs">Filter function</div>
        <div>
          <q-btn size="sm" class="text-center full-width q-mb-xs" color="white" text-color="primary" label="Reset"
            icon="restart_alt" @click="emptyFilter" />
          <q-btn size="sm" class="text-center full-width q-mb-xs" color="white" text-color="primary"
            :label="dynamicbuttonname()" icon="add_circle_outline" @click="enableFilterCard" />
          <q-chip class="col row" square>
            <q-avatar icon="flag" color="red" text-color="white" />
            <span class="col text-center">
              {{ filterSet.curShape }} == {{ filterSet.curValue }}
            </span>
          </q-chip>
        </div>
      </section>
      <section class="col bg-cyan-1 q-px-md q-mx-xs">
        <div class="text-italic text-center q-my-xs">Misc function</div>
        <q-btn size="sm" class="text-center full-width q-mb-xs" color="white" text-color="primary" label="Expanded All"
          icon="keyboard_arrow_down" @click="expandedStatus = true" />
        <q-btn size="sm" class="text-center full-width q-mb-xs" color="white" text-color="primary" label="Reset All"
          icon="keyboard_arrow_up" @click="expandedStatus = false" />
        <q-btn size="sm" class="text-center full-width" color="white" text-color="primary"
          :label="'Pull JSM - Auto sync after ' + countdown + ' seconds ..'" icon="sync"
          @click="pullJSMandSyncLocalDb" />
      </section>
    </span>
  </div>
  <DHSNetJSMList @triggerByJsmList="triggerCommentChange" @triggerByChangeQ="triigerChangeQueue"
    v-for="item in sortTicketSet" :key="item.sn" v-bind="item" :all="item" :isShow="filterStatus"
    :expandedStatus="expandedStatus" />
</template>
<script>
import DHSNetJSMList from 'components/DHSNetJSMList.vue'

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
  name: 'DHSNETJSMPage',
  components: { DHSNetJSMList },
  setup() {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const ticketSet = reactive({})
    const axiosExecuteBar = ref(null)
    const filterTarget = ref('Total')
    const filterStatus = ref(99)
    const sortTicketSet = computed(() => _.orderBy(ticketSet, 'sn', ['desc'])) // order by noteSet.sequence
    const inProgressSet = computed(() =>
      _.filter(ticketSet, function (o) {
        return (o.jiraStatus === 3) | (o.jiraStatus === 101) | (o.jiraStatus === 241)
      })
    )
    const completedSet = computed(() =>
      _.filter(ticketSet, function (o) {
        return (o.jiraStatus === 61) | (o.jiraStatus === 10129) | (o.jiraStatus === 10011)
      })
    )
    const canceledSet = computed(() =>
      _.filter(ticketSet, function (o) {
        return (
          (o.jiraStatus === 191) |
          (o.jiraStatus === 211) |
          (o.jiraStatus === 251) |
          (o.jiraStatus === 10004) |
          (o.jiraStatus === 10114)
        )
      })
    )

    const reopenSet = computed(() =>
      _.filter(ticketSet, function (o) {
        return o.jiraStatus === 4
      })
    )

    const openSet = computed(() =>
      _.filter(ticketSet, function (o) {
        return o.jiraStatus === 1
      })
    )

    const countdown = ref(120)

    const countdownTimer = setInterval(() => {
      --countdown.value
    }, 1000)

    const netPeopleList = [
      {
        label: 'Justin Yeh',
        value: 'Justin Yeh'
      },
      {
        label: 'Josh Liu',
        value: 'Josh Liu'
      },
      {
        label: 'Ryo Bing',
        value: 'Ryo Bing'
      },
      {
        label: 'Ray Hong',
        value: 'Ray Hong'
      },
      {
        label: 'Chris Yen',
        value: 'Chris Yen'
      },
      {
        label: 'Shane Tzou',
        value: 'Shane Tzou'
      }
    ]

    const expandedStatus = ref(false)

    const filterSet = reactive({
      isDisplayCard: false,
      targetList: ['handler', 'participant', 'category', 'facilities', 'infra', 'vendor'],
      targetCategory: [],
      targetFacilities: [],
      targetInfra: [],
      targetVendor: [],
      curShape: '', // filter target group, filter which item
      curValue: '' // filter target item value
    })

    // reset the filter function button
    function emptyFilter() {
      Object.values(ticketSet).forEach(function (ele, index, object) {
        ticketSet[ele.issueId].displayNameInclude = true
      })
      filterSet.curShape = ''
      filterSet.curValue = ''
      filterSet.isDisplayCard = false
    }

    // return the button name based on filter target exist or not
    function dynamicbuttonname() {
      if ((filterSet.curShape === '') && (filterSet.curValue === '')) {
        return 'Add the filter'
      } else {
        return 'Adjust the filter'
      }
    }

    // pull the db option list when user click the filter button
    async function enableFilterCard() {
      await axios
        .get(
          `https://${ServiceDomainLocal}:9487/bpCowork/jsm/createTicket/field/NET`
        )
        .then((response) => {
          console.log(response)
          filterSet.targetCategory = response.data.categoryOptions
          filterSet.targetFacilities = response.data.facilitiesOptions
          filterSet.targetInfra = response.data.infraOptions
          filterSet.targetVendor = response.data.vendorOptions
        })
        .catch((error) => {
          console.log(error)
        })
      filterSet.isDisplayCard = true
    }

    // after user choose the filter target, click the confirm button, front-end page will adjsut accordingly.
    function targetConfirm() {
      Object.values(ticketSet).forEach(function (ele, index, object) {
        if (filterSet.curShape === 'handler') {
          if (!ele.custom_handler.includes(filterSet.curValue)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        } else if (filterSet.curShape === 'participant') {
          if (ele.custom_participant) {
            if (!ele.custom_participant.includes(filterSet.curValue)) {
              ticketSet[ele.issueId].displayNameInclude = false
            } else {
              ticketSet[ele.issueId].displayNameInclude = true
            }
          } else {
            ticketSet[ele.issueId].displayNameInclude = false
          }
        } else if (filterSet.curShape === 'category') {
          if (!ele.custom_category.includes(filterSet.curValue)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        } else if (filterSet.curShape === 'facilities') {
          if (ele.custom_facilities === filterSet.curValue) {
            ticketSet[ele.issueId].displayNameInclude = true
          } else {
            ticketSet[ele.issueId].displayNameInclude = false
          }
        } else if (filterSet.curShape === 'infra') {
          if (!ele.custom_infra.includes(filterSet.curValue)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        } else if (filterSet.curShape === 'vendor') {
          if (!ele.custom_vendor.includes(filterSet.curValue)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        }
      })
      filterSet.isDisplayCard = false
    }

    function triigerChangeQueue() {
      syncLocalDb()
    }

    function triggerCommentChange(passObject) {
      // passObject = {target: jsmSn, issueId: JSM issueId}
      axios
        .get(
          `https://${ServiceDomainLocal}:9487/bpCowork/query/netdb/${passObject.target}`
        )
        .then((response) => {
          console.log(response)
          ticketSet[passObject.issueId].title = response.data.title
          ticketSet[passObject.issueId].description = response.data.description
          ticketSet[passObject.issueId].content_html = response.data.content_html
          ticketSet[passObject.issueId].comments = response.data.comments
          ticketSet[passObject.issueId].jiraStatus = response.data.jiraStatus
          ticketSet[passObject.issueId].ticketStatus = response.data.ticketStatus
          ticketSet[passObject.issueId].custom_handler = response.data.custom_handler
          ticketSet[passObject.issueId].custom_participant =
            response.data.custom_participant
          ticketSet[passObject.issueId].custom_category = response.data.custom_category
          ticketSet[passObject.issueId].custom_facilities =
            response.data.custom_facilities
          ticketSet[passObject.issueId].custom_infra = response.data.custom_infra
          ticketSet[passObject.issueId].custom_vendor = response.data.custom_vendor
          ticketSet[passObject.issueId].endTime = response.data.endTime
          ticketSet[passObject.issueId].startTime = response.data.startTime
          ticketSet[passObject.issueId].displayNameInclude = true
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function syncLocalDb(source) {
      console.log('hit syncLocalDb')
      countdown.value = 120
      const compareList = ref([])
      axios
        .get(`https://${ServiceDomainLocal}:9487/bpCowork/query/netdb`)
        .then((response) => {
          console.log('syncLocalDb resposne')
          console.log(response)
          // when remote length is small than browser length, means user close the ticket, so need to find it
          if (response.data.length < Object.keys(ticketSet).length) {
            response.data.forEach((ele) => {
              compareList.value.push(ele.issueId) // update the compare list
              ticketSet[ele.issueId] = ele
              ticketSet[ele.issueId].displayNameInclude = true
            })
            Object.values(ticketSet).forEach(function (ele, index, object) {
              if (compareList.value.includes(ele.issueId) === false) {
                delete ticketSet[ele.issueId]
              }
            })
          } else {
            response.data.forEach((ele) => {
              ticketSet[ele.issueId] = ele
              if (filterSet.curShape !== '' && filterSet.curValue !== '') {
                targetConfirm()
              } else {
                ticketSet[ele.issueId].displayNameInclude = true
              }
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
                  handler: () => { }
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
                handler: () => { }
              }
            ]
          })
        })
    }

    async function pullJSMandSyncLocalDb() {
      const barRef = axiosExecuteBar.value // for loading bar
      barRef.start() // start load
      // request worklog server to pull the current JSM ticket
      try {
        await axios.get(`https://${ServiceDomainLocal}:9487/bpRoutine/jsm/pull/net`)
        $q.notify({
          message: 'Worklog server pull JSM ticket successful',
          color: 'green-6',
          progress: true,
          html: true,
          actions: [
            {
              icon: 'cancel',
              color: 'white',
              handler: () => { }
            }
          ]
        })
        syncLocalDb('initiative')
        barRef.stop()
      } catch (e) {
        $q.notify({
          message: `Worklog server pull JSM ticket failed, reason - ${e.response.data}`,
          color: 'red-6',
          progress: true,
          html: true,
          actions: [
            {
              icon: 'cancel',
              color: 'white',
              handler: () => { }
            }
          ]
        })
        barRef.stop()
      }
    }

    onMounted(async () => {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/bpCowork/query/netdb`)
        .then((response) => {
          response.data.forEach((ele) => {
            ticketSet[ele.issueId] = ele
            ticketSet[ele.issueId].displayNameInclude = true
          })
          // JiraList = Object.assign([], response.data.jiraList)
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
      () => filterTarget.value,
      (curValue, oldValue) => {
        if (curValue === 'Total') {
          filterStatus.value = 99
        } else if (curValue === 'InProgess') {
          filterStatus.value = 3
        } else if (curValue === 'Completed') {
          filterStatus.value = 10129
        } else if (curValue === 'Canceled') {
          filterStatus.value = 10114
        } else if (curValue === 'Open') {
          filterStatus.value = 10132
        } else if (curValue === 'Reopened') {
          filterStatus.value = 4
        }
      }
    )

    return {
      sortTicketSet,
      triggerCommentChange,
      inProgressSet,
      completedSet,
      canceledSet,
      reopenSet,
      openSet,
      syncLocalDb,
      countdown,
      axiosExecuteBar,
      pullJSMandSyncLocalDb,
      filterTarget,
      filterStatus,
      netPeopleList,
      expandedStatus,
      triigerChangeQueue,
      filterSet, // reactive dict
      emptyFilter, // func
      dynamicbuttonname, // func
      enableFilterCard, // func
      targetConfirm // func
    }
  }
})
</script>
