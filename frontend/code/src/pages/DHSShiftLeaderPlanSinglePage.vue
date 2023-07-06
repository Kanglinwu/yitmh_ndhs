<template>
  <div class="q-px-lg q-py-md row q-gutter-xs items-center">
    <q-banner inline-actions class="bg-grey-3 row">
      <span>What you want?</span>
      <template v-slot:action>
        <q-radio
          v-model="configDist.purpose"
          checked-icon="task_alt"
          unchecked-icon="panorama_fish_eye"
          val="review"
          label="review"
        />
        <q-radio
          v-model="configDist.purpose"
          checked-icon="task_alt"
          unchecked-icon="panorama_fish_eye"
          val="assign"
          label="assign"
        />
      </template>
    </q-banner>
  </div>
  <div class="q-px-lg row q-gutter-xs items-center" v-show="configDist.isShowAssignZone">
    <q-banner inline-actions class="bg-grey-3 row">
      <span>Setup default shift</span>
      <template v-slot:action>
        <q-radio
          v-model="configDist.curShift"
          checked-icon="task_alt"
          unchecked-icon="panorama_fish_eye"
          val="M"
          label="M"
        />
        <q-radio
          v-model="configDist.curShift"
          checked-icon="task_alt"
          unchecked-icon="panorama_fish_eye"
          val="A"
          label="A"
        />
      </template>
    </q-banner>
  </div>
  <div class="q-pa-lg row" v-show="configDist.isShowAssignZone">
    <q-date class="col-3 q-pa-xs" v-model="days" :disable="configDist.curShift === ''" />
    <q-card-section
      class="col-9 q-px-xs q-py-none q-ma-none"
      v-show="configDist.isShowArrangeTable"
    >
      <div class="q-pa-xs q-ma-none bg-cyan-2 row items-center">
        <p class="col-11 q-mb-none q-pl-lg text-left text-bold">
          {{ configDist.curDateRange }}/{{ configDist.curShift }}
        </p>
        <section class="col-1 text-right">
          <q-btn
            @click="adjustMemberList"
            size="xs"
            color="secondary"
            round
            icon="settings"
          />
        </section>
      </div>
      <q-list bordered>
        <q-item class="q-pb-none">
          <q-item-section>
            <q-item-label>Shift Leader</q-item-label>
          </q-item-section>
          <q-item-section v-if="!configDist.isOngoing">
            <q-item-label caption>
              <q-skeleton type="rect" />
            </q-item-label>
          </q-item-section>
          <q-item-section v-else side>
            <q-item-label caption>
              <span
                @click="changeShiftLeader(name)"
                class="q-pr-xs cursor-pointer"
                v-for="name in configDist.curShiftMember"
                :key="name"
              >
                <span
                  v-if="name === shiftDict.shift_leader"
                  class="text-red-8 text-bold"
                  >{{ name }}</span
                >
                <span v-else>{{ name }}</span>
              </span>
            </q-item-label>
          </q-item-section>
        </q-item>
        <q-separator color="cyan-3" spaced inset />
        <q-item class="row justify-center items-center q-pt-none">Handler</q-item>
        <q-item v-if="!configDist.isOngoing" class="row q-pb-lg">
          <q-item-section class="col">
            <q-item-label>Handover</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>
              <q-skeleton type="QSlider" />
            </q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>Alert</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>
              <q-skeleton type="QSlider" />
            </q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>Message</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>
              <q-skeleton type="QSlider" />
            </q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>Request</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>
              <q-skeleton type="QSlider" />
            </q-item-label>
          </q-item-section>
        </q-item>
        <q-item v-else class="row q-pb-lg">
          <q-item-section class="col">
            <q-item-label>Handover</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label
              @click="changeTitle('handover', name)"
              v-for="name in configDist.curShiftMember"
              :key="name"
              caption
            >
              <span
                v-if="shiftDict.title_handover.includes(name)"
                class="text-red-8 text-bold cursor-pointer"
                >{{ name }}</span
              >
              <span v-else class="cursor-pointer">{{ name }}</span>
            </q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>Alert</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label
              @click="changeTitle('alert', name)"
              v-for="name in configDist.curShiftMember"
              :key="name"
              caption
            >
              <span
                v-if="shiftDict.title_alert_handler.includes(name)"
                class="text-red-8 text-bold cursor-pointer"
                >{{ name }}</span
              >
              <span v-else class="cursor-pointer">{{ name }}</span>
            </q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>Message</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label
              @click="changeTitle('message', name)"
              v-for="name in configDist.curShiftMember"
              :key="name"
              caption
            >
              <span
                v-if="shiftDict.title_message_handler.includes(name)"
                class="text-red-8 text-bold cursor-pointer"
                >{{ name }}</span
              >
              <span v-else class="cursor-pointer">{{ name }}</span>
            </q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label>Request</q-item-label>
          </q-item-section>
          <q-item-section class="col">
            <q-item-label
              @click="changeTitle('request', name)"
              v-for="name in configDist.curShiftMember"
              :key="name"
              caption
            >
              <span
                v-if="shiftDict.title_request_handler.includes(name)"
                class="text-red-8 text-bold cursor-pointer"
                >{{ name }}</span
              >
              <span v-else class="cursor-pointer">{{ name }}</span>
            </q-item-label>
          </q-item-section>
        </q-item>
        <q-separator color="cyan-3" spaced inset />
        <q-item class="row justify-end q-pb-md">
          <q-btn :disable="!configDist.isOngoing" @click="assignNewHandler" size="sm" color="secondary" label="Update" />
        </q-item>
      </q-list>
    </q-card-section>
  </div>
  <div class="q-pa-lg row" v-show="configDist.isShowReviewZone">
    <q-date class="col-3 q-pa-xs" v-model="reviewDict.days" range />
    <q-table
      :rows="reviewDict.rowdynamic"
      :columns="reviewDict.columns"
      row-key="sn"
      class="col"
      :pagination="reviewDict.pagination"
    >
      <template v-slot:top>
        <span class="col-6 text-subtitle1 text-center">{{ reviewDict.titleDays }}</span>
        <span class="col-6 text-right q-gutter-xs">
          <div class="bg-grey-2 q-pa-sm rounded-borders">
            Only show the result when shift leader as:
            <q-option-group
              name="preferred_genre"
              v-model="reviewDict.preferred"
              :options="reviewDict.options"
              color="primary"
              inline
            />
          </div>
        </span>
      </template>
      <template v-slot:body-cell-shift_leader="props">
        <q-td :props="props">
          <q-badge class="text-white" color="blue-10" :label="props.value" />
        </q-td>
      </template>
      <template v-slot:body-cell-title_handover="props">
        <q-td :props="props">
          <div v-for="(item, index) in props.value" :key="index">
            <q-badge class="text-black" color="teal-2" :label="item" />
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-title_alert_handler="props">
        <q-td :props="props">
          <div v-for="(item, index) in props.value" :key="index">
            <q-badge class="text-black" color="teal-2" :label="item" />
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-title_message_handler="props">
        <q-td :props="props">
          <div v-for="(item, index) in props.value" :key="index">
            <q-badge class="text-black" color="teal-2" :label="item" />
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-title_request_handler="props">
        <q-td :props="props">
          <div v-for="(item, index) in props.value" :key="index">
            <q-badge class="text-black" color="teal-2" :label="item" />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
  <q-dialog v-model="configDist.isShowAdjustMemberList" persistent>
    <q-card style="min-width: 800px">
      <q-card-section>
        <div class="text-h6">
          Current Member on {{ configDist.curDateRange }}/{{ configDist.curShift }}
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-select
          filled
          use-chips
          stack-label
          v-model="configDist.curShiftMember"
          multiple
          virtual-scroll-horizontal
          :options="memberDefaultList"
          label="On the shift"
        />
      </q-card-section>

      <q-card-actions align="right" class="text-primary">
        <q-btn flat label="ok" @click="assignNewHandler" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { reactive, ref, watch, computed } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import axios from 'axios'

export default {
  setup() {
    // dynamic domain
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain

    // alert purpose
    const $q = useQuasar()

    const days = ref([])

    const shiftLeaderDefaultList = [
      'Cadalora',
      'Keven',
      'Larry',
      'Danny',
      'Aiden',
      'Asky'
    ]

    const memberDefaultList = ref([
      'Aiden',
      'Albert',
      'Alex',
      'Asky',
      'Bob',
      'Cadalora',
      'Cyril',
      'Daniel',
      'Eric',
      'Gary',
      'Thurston',
      'Rorschach',
      'Bayu',
      'Danny',
      'Huck',
      'Ivan',
      'Keven',
      'Larry'
    ])

    const reviewDict = reactive({
      pagination: {
        rowsPerPage: 0
      },
      preferred: '',
      options: [
        {
          label: 'Without filter',
          value: ''
        },
        {
          label: 'Aiden',
          value: 'Aiden'
        },
        {
          label: 'Asky',
          value: 'Asky'
        },
        {
          label: 'Cadalora',
          value: 'Cadalora'
        },
        {
          label: 'Danny',
          value: 'Danny'
        },
        {
          label: 'Keven',
          value: 'Keven'
        },
        {
          label: 'Larry',
          value: 'Larry'
        }
      ],
      days: '',
      titleDays: computed(() => {
        if (typeof reviewDict.days === 'string') {
          return reviewDict.days
        } else {
          try {
            return `from ${reviewDict.days.from} to ${reviewDict.days.to}`
          } catch (error) {
            return ''
          }
        }
      }),
      rows: [],
      rowdynamic: computed(() => {
        if (reviewDict.preferred === '') {
          return reviewDict.rows
        } else {
          return reviewDict.rows.filter(
            (row) => row.shift_leader === reviewDict.preferred
          )
        }
      }),
      columns: [
        {
          name: 'shift_leader',
          label: 'shift_leader',
          field: 'shift_leader',
          sortable: true,
          align: 'center'
        },
        {
          name: 'shift',
          label: 'shift',
          field: 'shift',
          sortable: true,
          align: 'center'
        },
        {
          name: 'date',
          label: 'date',
          field: 'date',
          sortable: true,
          align: 'center'
        },
        {
          name: 'title_handover',
          label: 'title_handover',
          field: 'title_handover',
          sortable: true,
          align: 'right'
        },
        {
          name: 'title_alert_handler',
          label: 'title_alert_handler',
          field: 'title_alert_handler',
          sortable: true,
          align: 'right'
        },
        {
          name: 'title_message_handler',
          field: 'title_message_handler',
          label: 'title_message_handler',
          sortable: true,
          align: 'right'
        },
        {
          name: 'title_request_handler',
          label: 'title_request_handler',
          field: 'title_request_handler',
          sortable: true,
          align: 'right'
        }
      ]
    })

    const configDist = reactive({
      purpose: '',
      isShowAssignZone: false,
      isShowReviewZone: false,
      isShowArrangeTable: false,
      isShowAdjustMemberList: false,
      isOngoing: true,
      curShift: '',
      curDateRange: '',
      curShiftMember: []
    })

    const shiftDict = reactive({
      shift_leader: '',
      title_handover: [],
      title_alert_handler: [],
      title_message_handler: [],
      title_request_handler: []
    })

    function adjustMemberList() {
      configDist.isShowAdjustMemberList = true
    }

    async function checkShiftMember(targetDate) {
      if (configDist.isOngoing) {
        configDist.isOngoing = false
        const postData = reactive({
          shift: configDist.curShift,
          dateRange: targetDate
        })
        await axios
          .post(`https://${ServiceDomainLocal}:9486/shiftleader/api/queryraw`, postData)
          .then((res) => {
            console.log(res.data)
            if (res.data.status === 'success') {
              resetAll()
              configDist.curDateRange = targetDate
              if (res.data.result._type === 'api') {
                configDist.curShiftMember = res.data.result.teammates
                // check if first item is the shift leader
                if (shiftLeaderDefaultList.includes(res.data.result.teammates[0])) {
                  shiftDict.shift_leader = res.data.result.teammates[0]
                }
              } else {
                shiftDict.shift_leader = res.data.result.shift_leader
                configDist.curShiftMember = res.data.result.teammates
                shiftDict.title_alert_handler = res.data.result.title_alert_handler
                shiftDict.title_handover = res.data.result.title_handover
                shiftDict.title_message_handler = res.data.result.title_message_handler
                shiftDict.title_request_handler = res.data.result.title_request_handler
              }
            } else {
              resetAll()
              if (typeof targetDate === 'string') {
                $q.notify({
                  message: `Get error when you query the ${res.data.date}-${res.data.shift}:<br><b>${res.data.result}</b>`,
                  color: 'red-6',
                  html: true,
                  progress: true,
                  actions: [
                    {
                      icon: 'cancel',
                      color: 'white',
                      handler: () => {}
                    }
                  ]
                })
              } else {
                console.log('total result')
                console.log(res.data.result)
                console.log('diff date')
                console.log(res.data.diffDay)
                $q.notify({
                  message: `Get error when you query from ${res.data.originDateRange.from} to ${res.data.originDateRange.to}:<br><b>${res.data.details}</b><br>If you want to see the more detail, open the console.log to see the diff`,
                  color: 'red-6',
                  html: true,
                  progress: true,
                  actions: [
                    {
                      icon: 'cancel',
                      color: 'white',
                      handler: () => {}
                    }
                  ]
                })
              }
            }
          })
          .catch((error) => {
            console.log(error)
          })
      } else {
        console.log('Check progress is ongoing')
      }
    }

    async function reviewGetShiftLeaders(targetDate) {
      const postData = reactive({
        dateRange: targetDate
      })

      await axios
        .post(`https://${ServiceDomainLocal}:9486/shiftleader/api/reviewdate`, postData)
        .then((res) => {
          console.log(res)
          if (res.data.status === 'success') {
            reviewDict.rows = res.data.result
          } else {
            reviewDict.rows = []
            $q.notify({
              message: `Get error when you want to review ${targetDate} data:<br><b>${res.data.result}</b>`,
              color: 'red-6',
              html: true,
              progress: true,
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

    function resetAll() {
      shiftDict.shift_leader = ''
      shiftDict.title_handover = []
      shiftDict.title_alert_handler = []
      shiftDict.title_message_handler = []
      shiftDict.title_request_handler = []
      configDist.curDateRange = ''
      configDist.curShiftMember = []
      configDist.isOngoing = true
    }

    function changeShiftLeader(targetName) {
      shiftDict.shift_leader = targetName
    }

    function changeTitle(source, targetName) {
      switch (source) {
        case 'handover':
          if (shiftDict.title_handover.includes(targetName)) {
            shiftDict.title_handover.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_handover.push(targetName)
          }
          break
        case 'alert':
          if (shiftDict.title_alert_handler.includes(targetName)) {
            shiftDict.title_alert_handler.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_alert_handler.push(targetName)
          }
          break
        case 'message':
          if (shiftDict.title_message_handler.includes(targetName)) {
            shiftDict.title_message_handler.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_message_handler.push(targetName)
          }
          break
        case 'request':
          if (shiftDict.title_request_handler.includes(targetName)) {
            shiftDict.title_request_handler.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_request_handler.push(targetName)
          }
          break
      }
    }

    async function assignNewHandler() {
      const postData = reactive({
        shiftDetails: shiftDict,
        curTeammates: configDist.curShiftMember,
        dateRange: configDist.curDateRange,
        whichShift: configDist.curShift
      })
      await axios
        .post(`https://${ServiceDomainLocal}:9486/shiftleader/api/assign`, postData)
        .then((res) => {
          if (res.status === 200) {
            $q.notify({
              message: `[Status]: <b>${res.data}</b>`,
              color: 'green-6',
              html: true,
              progress: true,
              actions: [
                {
                  icon: 'cancel',
                  color: 'white',
                  handler: () => {}
                }
              ]
            })
          } else {
            $q.notify({
              message: `[Status]: <b>${res.data}</b>`,
              color: 'red-6',
              html: true,
              progress: true,
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

    watch(
      () => days.value,
      (curValue, oldValue) => {
        console.log('hit watch')
        if (curValue) {
          checkShiftMember(curValue)
        } else {
          resetAll()
        }
      }
    )

    watch(
      () => configDist.curShift,
      (curValue, oldValue) => {
        console.log(curValue)
        if (configDist.curDateRange !== '') {
          checkShiftMember(configDist.curDateRange)
        }
      }
    )

    watch(
      () => configDist.curDateRange,
      (curValue, oldValue) => {
        if (curValue === '') {
          configDist.isShowArrangeTable = false
        } else {
          configDist.isShowArrangeTable = true
        }
      }
    )

    watch(
      () => configDist.purpose,
      (curValue, oldValue) => {
        if (curValue === 'review') {
          resetAll()
          configDist.isShowArrangeTable = false
          configDist.isShowAssignZone = false
          configDist.isShowReviewZone = true
        } else {
          resetAll()
          configDist.isShowAssignZone = true
          configDist.isShowReviewZone = false
          reviewDict.days = ''
        }
      }
    )

    watch(
      () => reviewDict.days,
      (curValue, oldValue) => {
        console.log()
        if (typeof curValue === 'string' && curValue.length !== 0) {
          reviewGetShiftLeaders(curValue)
          console.log('one date')
        } else if (typeof curValue === 'object' && curValue !== null) {
          console.log(curValue)
          reviewGetShiftLeaders(curValue)
          console.log('date range')
        } else {
          console.log('on the assign zone - no need')
        }
      }
    )

    return {
      days,
      reviewDict,
      configDist,
      shiftDict,
      checkShiftMember,
      changeShiftLeader,
      changeTitle,
      reviewGetShiftLeaders,
      assignNewHandler,
      shiftLeaderDefaultList,
      memberDefaultList,
      adjustMemberList
    }
  }
}
</script>
