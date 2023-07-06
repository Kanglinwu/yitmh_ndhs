<!-- @format -->
<template>
  <q-ajax-bar ref="axiosExecuteBar" position="bottom" color="secondary" size="10px" skip-hijack />
  <q-dialog v-model="card">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Choose the target</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="emptyFilter" />
      </q-card-section>

      <q-card-section>
        <div class="q-gutter-sm">
          <span v-for="x in targetlist" v-bind:key="x">
            <q-radio v-model="shape" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="x" :label="x" />
          </span>
        </div>
      </q-card-section>
      <q-separator />
      <q-card-section v-if="shape !== ''">
        <div class="q-gutter-sm" v-if="shape == 'handler'">
          <span v-for="y in dbaPeopleList" v-bind:key="y.label">
            <q-radio v-model="targetValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="y.value"
              :label="y.label" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="shape == 'participant'">
          <span v-for="y in dbaPeopleList" v-bind:key="y.label">
            <q-radio v-model="targetValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="y.value"
              :label="y.label" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="shape == 'bizUnit'">
          <span v-for="(value, key) in targetOption.bizUnit" v-bind:key="key">
            <q-radio v-model="targetValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="value"
              :label="value" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="shape == 'category'">
          <span v-for="(value, key) in targetOption.category" v-bind:key="key">
            <q-radio v-model="targetValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="value"
              :label="value" />
          </span>
        </div>
        <div class="q-gutter-sm" v-if="shape == 'priority'">
          <span v-for="y in targetPriorityList" v-bind:key="y">
            <q-radio v-model="targetValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" :val="y"
              :label="y" />
          </span>
        </div>
        <!-- <div class="q-gutter-sm" v-if="shape == 'impact'">
          <q-radio v-model="targetValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" val="Yes"
            label="Yes" />
          <q-radio v-model="targetValue" checked-icon="task_alt" unchecked-icon="panorama_fish_eye" val="No"
            label="No" />
        </div> -->
      </q-card-section>
      <q-separator />
      <q-card-section v-if="(shape !== '') && (targetValue !== '')">
        <div class="row justify-between">
          <q-chip class="col row" square>
            <q-avatar icon="flag" color="red" text-color="white" />
            <span class="col text-center">
              {{ shape }} == {{ targetValue }}
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
        <div class="text-italic text-center q-my-xs">Filter JSM Status</div>
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
              {{ shape }} == {{ targetValue }}
            </span>
          </q-chip>
        </div>
        <!-- <q-option-group class="q-pa-md" v-model="group" :options="dbaPeopleList" color="green" inline /> -->
      </section>
      <section class="col bg-cyan-1 q-px-md q-mx-xs">
        <div class="text-italic text-center q-my-xs">Misc JSM function</div>
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
  <DHSDbaJSMList @triggerByJsmList="triggerChange" @triggerByChangeQ="triigerChangeQueue" v-for="item in sortTicketSet"
    :key="item.sn" v-bind="item" :all="item" :isShow="filterStatus" :expandedStatus="expandedStatus" />

</template>
<script>
import DHSDbaJSMList from 'components/DHSDbaJSMList.vue'

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
  name: 'DHSDBAJSMPage',
  components: { DHSDbaJSMList },
  setup() {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const ticketSet = reactive({})
    const axiosExecuteBar = ref(null)
    const filterTarget = ref('Total')
    const filterStatus = ref(99)
    // const filterName = ref(true)
    const sortTicketSet = computed(() => _.orderBy(ticketSet, ['ticketStatus', 'sn'], ['asc', 'desc'])) // order by noteSet.sequence
    const inProgressSet = computed(() =>
      _.filter(ticketSet, function (o) {
        return (o.jiraStatus === 3) | (o.jiraStatus === 101) | (o.jiraStatus === 241)
      })
    )
    const completedSet = computed(() =>
      _.filter(ticketSet, function (o) {
        return (o.jiraStatus === 61) | (o.jiraStatus === 10011) | (o.jiraStatus === 10129)
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
        return o.jiraStatus === 1 | o.jiraStatus === 10132
      })
    )

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

    const expandedStatus = ref(false)

    const card = ref(false) // open the filter function popup window or not
    const targetlist = ref([
      'handler',
      'participant',
      'bizUnit',
      'category',
      'priority'
    ])
    const targetPriorityList = ref([
      'Highest',
      'High',
      'Medium',
      'Low',
      'Lowest'
    ])
    const shape = ref('') // filter target group, filter which item
    const targetValue = ref('') // filter target item value
    const targetOption = reactive({})

    function enableFilterCard() {
      axios
        .get(
          `https://${ServiceDomainLocal}:9487/bpCowork/jsm/createTicket/field/DBA`
        )
        .then((response) => {
          targetOption.bizUnit = response.data.bizUnitOptions
          targetOption.category = response.data.categoryOptions
        })
        .catch((error) => {
          console.log(error)
        })
      card.value = true
    }

    function targetConfirm() {
      Object.values(ticketSet).forEach(function (ele, index, object) {
        if (shape.value === 'handler') {
          if (!ele.custom_handler.includes(targetValue.value)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        } else if (shape.value === 'participant') {
          if (ele.custom_participant) {
            if (!ele.custom_participant.includes(targetValue.value)) {
              ticketSet[ele.issueId].displayNameInclude = false
            } else {
              ticketSet[ele.issueId].displayNameInclude = true
            }
          } else {
            ticketSet[ele.issueId].displayNameInclude = false
          }
        } else if (shape.value === 'bizUnit') {
          if (!ele.custom_bizUnit.includes(targetValue.value)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        } else if (shape.value === 'category') {
          if (!ele.custom_category.includes(targetValue.value)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        } else if (shape.value === 'priority') {
          if (!ele.custom_priority.includes(targetValue.value)) {
            ticketSet[ele.issueId].displayNameInclude = false
          } else {
            ticketSet[ele.issueId].displayNameInclude = true
          }
        }
      })
      card.value = false
    }

    // return the button name based on filter target exist or not
    function dynamicbuttonname() {
      if ((shape.value === '') && (targetValue.value === '')) {
        return 'Add the filter'
      } else {
        return 'Adjust the filter'
      }
    }

    function triggerChange(passObject) {
      // passObject = {target: jsmSn, issueId: JSM issueId}
      axios
        .get(
          `https://${ServiceDomainLocal}:9487/bpCowork/query/dbadb/${passObject.target}`
        )
        .then((response) => {
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
          ticketSet[passObject.issueId].custom_bizUnit = response.data.custom_bizUnit
          ticketSet[passObject.issueId].custom_priority = response.data.custom_priority
          ticketSet[passObject.issueId].custom_isImpact = response.data.custom_isImpact
          ticketSet[passObject.issueId].custom_workLogValue =
            response.data.custom_workLogValue
          ticketSet[passObject.issueId].custom_workLogId = response.data.custom_workLogId
          ticketSet[passObject.issueId].endTime = response.data.endTime
          ticketSet[passObject.issueId].startTime = response.data.startTime
          ticketSet[passObject.issueId].displayNameInclude = true
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function syncLocalDb(source) {
      countdown.value = 120
      const compareList = ref([])
      axios
        .get(`https://${ServiceDomainLocal}:9487/bpCowork/query/dbadb`)
        .then((response) => {
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
              if (shape.value !== '' && targetValue.value !== '') {
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
        await axios.get(`https://${ServiceDomainLocal}:9487/bpRoutine/jsm/pull/dba`)
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

    // reset the filter function button
    function emptyFilter() {
      Object.values(ticketSet).forEach(function (ele, index, object) {
        ticketSet[ele.issueId].displayNameInclude = true
      })
      shape.value = ''
      targetValue.value = ''
      card.value = false
    }

    function triigerChangeQueue() {
      console.log('hit triigerChangeQueue')
      syncLocalDb()
    }

    onMounted(async () => {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/bpCowork/query/dbadb`)
        .then((response) => {
          console.log(response)
          response.data.forEach((ele) => {
            ticketSet[ele.issueId] = ele
            ticketSet[ele.issueId].displayNameInclude = true
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
      triggerChange,
      inProgressSet,
      completedSet,
      canceledSet,
      reopenSet,
      openSet,
      countdown,
      syncLocalDb,
      axiosExecuteBar,
      pullJSMandSyncLocalDb,
      filterTarget,
      filterStatus,
      dbaPeopleList,
      expandedStatus,
      triigerChangeQueue,
      card, // for filter function popup card
      shape,
      targetlist,
      targetValue,
      targetOption,
      targetPriorityList,
      targetConfirm, // func
      enableFilterCard, // func
      dynamicbuttonname, // func
      emptyFilter // func
    }
  }
})
</script>
