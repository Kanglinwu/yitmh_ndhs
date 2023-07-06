<!-- @format -->
<template>
  <q-dialog v-model="isShowPopUpWindow" full-width>
    <q-card>
      <q-card-section>
        <div v-html="creatingEventColor[0]"></div>
      </q-card-section>
      <q-stepper v-model="step" ref="stepper" color="primary" animated>
        <q-step :name="1" title="When?" icon="settings" :done="step > 1">
          <q-input
            label="Start time"
            filled
            v-model="eventObject.startTime"
            standout="bg-blue-3 text-bold text-dark"
          >
            <template v-slot:append>
              <q-icon name="access_time" class="cursor-pointer">
                <q-popup-proxy
                  class="row q-pa-xs bg-blue-3"
                  cover
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <q-date
                    class="q-pa-xs"
                    v-model="eventObject.startTime"
                    mask="YYYY-MM-DD HH:mm"
                  >
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-date>
                  <q-time
                    v-model="eventObject.startTime"
                    class="q-pa-xs"
                    mask="YYYY-MM-DD HH:mm"
                    format24h
                  >
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-time>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
          <q-input
            label="End time"
            filled
            v-model="eventObject.endTime"
            standout="bg-blue-3 text-bold text-dark"
          >
            <template v-slot:append>
              <q-icon name="access_time" class="cursor-pointer">
                <q-popup-proxy
                  class="row q-pa-xs bg-blue-3"
                  cover
                  transition-show="scale"
                  transition-hide="scale"
                >
                  <q-date
                    class="q-pa-xs"
                    v-model="eventObject.endTime"
                    mask="YYYY-MM-DD HH:mm"
                  >
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-date>
                  <q-time
                    v-model="eventObject.endTime"
                    class="q-pa-xs"
                    mask="YYYY-MM-DD HH:mm"
                    format24h
                  >
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-time>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </q-step>
        <q-step :name="2" title="Affected BU?" icon="settings" :done="step > 2">
          <!-- {{ buList }} -->
          <q-option-group
            :options="eventObject.affectedBuList"
            type="checkbox"
            v-model="eventObject.affectedBuValue"
          />
        </q-step>

        <q-step
          :name="3"
          title="What is the root cause?"
          icon="settings"
          :done="step > 3"
        >
          <q-option-group
            :options="eventObject.rootcauseList"
            type="radio"
            v-model="eventObject.rootcauseValue"
          />
        </q-step>

        <q-step :name="4" title="Related to?" icon="settings" :done="step > 4">
          <q-option-group
            :options="eventObject.relatedList"
            type="radio"
            v-model="eventObject.relatedValue"
          />
        </q-step>

        <q-step :name="5" title="Summarize and confirm it" icon="settings">
          <q-markup-table>
            <thead>
              <tr>
                <th class="text-left">Date</th>
                <th class="text-right">Outage(minutes)</th>
                <th class="text-right">Start at</th>
                <th class="text-right">End at</th>
                <th class="text-right">Affected service(s)</th>
                <th class="text-right">Root cause</th>
                <th class="text-right">Refer to</th>
                <th class="text-right">Event Level</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-left">{{ eventObject.dateTime }}</td>
                <td class="text-right">{{ eventObject.outageTime[0] }}</td>
                <td class="text-right">{{ eventObject.startTime }}</td>
                <td class="text-right">{{ eventObject.endTime }}</td>
                <td class="text-right">{{ eventObject.affectedBuValue.toString() }}</td>
                <td class="text-right">{{ eventObject.rootcauseValue }}</td>
                <td class="text-right">{{ eventObject.relatedValueToUser }}</td>
                <td class="text-right">{{ creatingEventColor[1] }}</td>
              </tr>
            </tbody>
          </q-markup-table>
        </q-step>

        <template v-slot:navigation>
          <q-stepper-navigation>
            <q-btn
              @click="stepperController"
              color="primary"
              :label="step === 5 ? 'Update to DB' : 'Continue'"
              :disable="defineNextButtonStatus"
            />
            <q-btn
              v-if="step > 1"
              flat
              color="primary"
              @click="$refs.stepper.previous()"
              label="Back"
              class="q-ml-sm"
            />
            <q-btn
              v-if="step === 5"
              flat
              color="primary"
              label="Reset"
              class="q-ml-sm"
              @click="resetAllValue"
            />
          </q-stepper-navigation>
        </template>
      </q-stepper>
    </q-card>
  </q-dialog>
  <q-table
    class="my-sticky-header-table customChildAutoHeigth"
    dense
    :rows="rows"
    :columns="columns"
    row-key="name"
    :pagination="pagination"
  >
    <template v-slot:top>
      <span class="col-6">Service Status</span>
      <span class="col-6 text-right q-gutter-xs">
        <q-btn
          size="sm"
          @click="preQuery('Red')"
          push
          color="white"
          text-color="red"
          round
          icon="add_circle"
        />
        <q-btn
          size="sm"
          @click="preQuery('Yellow')"
          push
          color="white"
          text-color="yellow"
          round
          icon="add_circle"
        />
      </span>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="customer" :props="props">
          {{ props.row.customer }}
        </q-td>
        <q-td key="status" :props="props">
          <span v-if="props.row.status === 'Green'">
            <q-badge color="green">
              {{ props.row.status }}
            </q-badge>
          </span>
          <span v-else class="row justify-center">
            <span
              class="col-12"
              v-for="(value, index) in props.row.status[1]"
              :key="index"
            >
              <span v-if="value[0][0] === 'Red'">
                <q-badge color="red">Red</q-badge>
              </span>
              <span v-else>
                <q-badge color="yellow"><span class="text-black">Yellow</span></q-badge>
              </span>
              <span class="q-pl-xs" v-for="x in value" :key="x[2]">
                {{ x[1] }}
                <q-btn
                  outline
                  round
                  icon="delete"
                  size="xs"
                  class="q-mx-xs"
                  @click="removeEvent(props.row.customer, x[2])"
                />
                <q-btn
                  outline
                  round
                  icon="search"
                  size="xs"
                  @click="findTheEvent(x[3])"
                />
              </span>
            </span>
          </span>
        </q-td>
        <q-separator />
      </q-tr>
    </template>
    <template class="row text-caption" v-slot:bottom>
      <span class="col-3 q-py-sm"
        >Total Customers: <b>{{ pagination.rowsNumber }}</b>
      </span>
      <span class="col-9 q-py-sm text-right">
        <q-badge color="green">Green</q-badge> No Incident |
        <q-badge color="red">Red</q-badge> Critical Incident Ongoing |
        <q-badge color="yellow"><span class="text-dark">Yellow</span></q-badge>
        Incident Ongoing or Critical Incident Recovered
      </span>
    </template>
  </q-table>
</template>

<script>
import { defineComponent, inject, ref, reactive, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { date, useQuasar, scroll } from 'quasar'
import axios from 'axios'
// import _ from 'lodash'

export default defineComponent({
  name: 'DHSCustomerStatusPage',
  setup() {
    const isLogin = inject('isLogin') // get the root isLogin dict
    const CurData = inject('CurData')
    const CurShift = inject('CurShift')
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const $q = useQuasar()
    const { getScrollTarget, setVerticalScrollPosition } = scroll // scroll function
    const eventLevelReminder = ref(
      '<span class="text-black">Green</span> - No Incident / [Red - Critical Incident pending] / [Yellow - Incident pending or critical incident recovered]'
    )

    // define table columns
    const columns = [
      {
        name: 'customer',
        align: 'left',
        label: 'BU',
        field: 'customer',
        headerStyle: 'width: 50%'
      },
      {
        name: 'status',
        align: 'left',
        label: 'Status',
        field: 'status',
        headerStyle: 'width: 50%'
      }
    ]

    const rows = ref([
      { customer: '188A', status: 'Green' },
      { customer: 'LDR', status: 'Green' },
      { customer: 'SBK', status: 'Green' },
      { customer: 'KENO', status: 'Green' },
      { customer: 'GICT', status: 'Green' },
      { customer: 'Others', status: 'Green' }
    ])

    // create red / yellow event v-model
    const isShowPopUpWindow = ref(false)

    // target color
    const creatingEventColor = ref('')

    // stepper
    const step = ref(1)

    // eventObject -- reactive
    const eventObject = reactive({
      dateTime: computed(() => {
        return ref(date.formatDate(new Date(eventObject.startTime), 'YYYY-MM-DD'))
      }),
      startTime: ref(''),
      endTime: ref(''),
      outageTime: computed(() => {
        if (date.isValid(eventObject.startTime) && date.isValid(eventObject.endTime)) {
          const startTimeObject = new Date(eventObject.startTime)
          const endTimeObject = new Date(eventObject.endTime)
          const diff = date.getDateDiff(endTimeObject, startTimeObject, 'minutes')
          if (diff > 0) {
            return [diff, false]
          } else {
            return [diff, true]
          }
        } else {
          return [0, true]
        }
      }),
      affectedBuList: ref([]),
      affectedBuValue: ref([]),
      rootcauseList: ref([
        { value: 'Application', label: 'Application' },
        { value: 'DB', label: 'DB' },
        { value: 'Network', label: 'Network' },
        { value: 'DDoS', label: 'DDoS' },
        { value: 'CDN', label: 'CDN' },
        { value: 'Redirect', label: 'Redirect' },
        { value: 'ICP', label: 'ICP' },
        { value: 'DNS Poision', label: 'DNS Poision' },
        { value: 'Other', label: 'Other' }
      ]),
      rootcauseValue: ref(''),
      relatedList: ref([]),
      relatedValue: ref(''),
      relatedValueToUser: computed(() => {
        const returnContainer = ref('')
        for (const item of Object.entries(eventObject.relatedList)) {
          if (item[1].value === eventObject.relatedValue) {
            returnContainer.value = item[1].label
          }
        }
        return returnContainer.value
      })
    })

    // endTime
    const eventStartTime = ref('')
    const eventEndTime = ref('')

    // use this to check the stepper can go to next step
    const defineNextButtonStatus = computed(() => {
      if (step.value === 1) {
        // start time and end time selector
        return eventObject.outageTime[1]
      } else if (step.value === 2) {
        // affected service selector
        if (eventObject.affectedBuValue.length !== 0) {
          return false
        } else {
          return true
        }
      } else if (step.value === 3) {
        return false
      } else if (step.value === 4) {
        if (eventObject.relatedValue !== '') {
          return false
        } else {
          return true
        }
      } else if (step.value === 5) {
        return false
      } else {
        return false
      }
    })

    onMounted(async () => {
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/customerStatus/query/last`
      )
      for (const [key, value] of Object.entries(res.data)) {
        switch (key) {
          case '_188A':
            rows.value[0].status = value
            break
          case 'LDR':
            rows.value[1].status = value
            break
          case 'SBK':
            rows.value[2].status = value
            break
          case 'KENO':
            rows.value[3].status = value
            break
          case 'GICT':
            rows.value[4].status = value
            break
          case 'Others':
            rows.value[5].status = value
            break
          default:
            console.log('hit default')
            break
        }
      }
    })

    async function preQuery(eventColor) {
      // get bu list when user click create the new event
      eventObject.affectedBuList = rows.value.map((item) => ({
        label: item.customer,
        value: item.customer
      }))
      // to get current note / otrs / jira list
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/customerStatus/query/relateItem`
      )
      eventObject.relatedList = res.data
      // update the current event color
      if (eventColor === 'Red') {
        creatingEventColor.value = [
          '<span class="text-h6">Creating <span class="text-red">Red</span> Event</span>',
          'Red'
        ]
      } else {
        creatingEventColor.value = [
          '<span class="text-h6">Creating <span class="text-yellow-9">Yellow</span> Event</span>',
          'Yellow'
        ]
      }
      // assign current time to start time
      eventObject.startTime = ref(date.formatDate(Date.now(), 'YYYY-MM-DD HH:mm'))
      // enable popup window
      isShowPopUpWindow.value = true
    }

    function stepperController() {
      if (step.value === 5) {
        if (window.confirm('Confirm?')) {
          updateEventToDb()
        } else {
          console.log('has been canceled')
        }
      } else {
        step.value = ++step.value
      }
    }

    function resetAllValue() {
      eventObject.startTime = ''
      eventObject.endTime = ''
      eventObject.rootcauseValue = ''
      eventObject.relatedValue = ''
      eventObject.affectedBuValue = []
      step.value = 1
    }

    function updateEventToDb() {
      const postData = reactive({
        targetDate: CurData,
        targetShift: CurShift,
        affectedBuList: eventObject.affectedBuValue,
        relatedItem: eventObject.relatedValueToUser,
        relatedItemRow: eventObject.relatedValue,
        rootcause: eventObject.rootcauseValue,
        eventLevel: creatingEventColor.value[1],
        eventStartTime: eventObject.startTime,
        eventEndTime: eventObject.endTime,
        eventOutage: eventObject.outageTime
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/customerStatus/update`, postData)
        .then((res) => {
          console.log(res)
          if (res.status === 200) {
            isLogin.refreshCustomerStatusKey += 1
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function removeEvent(targetService, eventSn) {
      if (window.confirm('Delete this event?')) {
        const postData = reactive({
          targetSn: eventSn,
          targetService: targetService,
          targetDate: CurData,
          targetShift: CurShift
        })
        axios
          .post(`https://${ServiceDomainLocal}:9487/customerStatus/delete`, postData)
          .then((res) => {
            console.log(res)
            if (res.status === 200) {
              isLogin.refreshCustomerStatusKey += 1
            }
          })
          .catch((error) => {
            console.log(error)
          })
      } else {
        console.log('has been canceled')
      }
    }

    function findTheEvent(targetEvent) {
      console.log(targetEvent)
      const ele = document.getElementById(targetEvent)
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - 55
      const duration = 200
      ele.classList.add('ballon', 'bg-yellow-1')
      setVerticalScrollPosition(target, offset, duration)
      window.setTimeout(() => ele.classList.remove('ballon', 'bg-yellow-1'), 11000)
    }

    watch(
      () => eventObject.rootcauseValue,
      (curValue, preValue) => {
        if (curValue === 'Other') {
          $q.dialog({
            title: 'Other',
            message: 'What is the rootcause?',
            prompt: {
              model: '',
              type: 'text' // optional
            },
            cancel: true,
            persistent: true
          }).onOk((data) => {
            eventObject.rootcauseValue = data
            eventObject.rootcauseList[8] = { value: data, label: data }
          })
        } else if (curValue && preValue !== 'Other') {
          eventObject.rootcauseList[8] = { value: 'Other', label: 'Other' }
        }
      }
    )

    return {
      isLogin,
      // ServiceDomainLocal,
      columns,
      rows,
      pagination: ref({
        rowsPerPage: 0,
        rowsNumber: 7
      }),
      eventLevelReminder,
      isShowPopUpWindow,
      preQuery,
      step,
      creatingEventColor,
      eventStartTime,
      eventEndTime,
      defineNextButtonStatus,
      eventObject,
      stepperController,
      resetAllValue,
      removeEvent,
      findTheEvent
    }
  }
})
</script>

<style lang="scss" scoped>
a.customWithNone {
  text-decoration: none;
}

td.customPaddingQTbx {
  padding: 4px !important;
}
</style>
