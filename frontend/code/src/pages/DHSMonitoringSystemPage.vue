<!-- @format -->
<template>
  <q-table
    class="my-sticky-header-table customChildAutoHeigth"
    dense
    :rows="rows"
    :columns="columns"
    row-key="name"
    separator="cell"
    :pagination="pagination"
  >
    <template v-slot:header="props">
      <q-tr :props="props">
        <q-th auto-width />
        <q-th v-for="col in props.cols" :key="col.name" :props="props">
          {{ col.label }}
        </q-th>
      </q-tr>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td class="text-center customPaddingQTbx" auto-width>
          <q-btn
            size="sm"
            class="text-center"
            push
            color="white"
            text-color="primary"
            round
            dense
            icon="sync"
            @click="checkService(props.row.service)"
          />
        </q-td>
        <q-td key="service" :props="props">
          <a class="customWithNone" :href="props.row.hyperlink" target="_blank"
            ><span class="text-blue">{{ props.row.service }}</span></a
          >
        </q-td>
        <q-td key="auditor" :props="props">
          {{ props.row.auditor }}
        </q-td>
        <q-td key="detail" :props="props">
          <span v-if="props.row.underQuery">
            <q-skeleton animation="blink" type="text" />
          </span>
          <span v-else>
            {{ props.row.detail }}
          </span>
        </q-td>
        <q-td key="lastCheckTime" :props="props">
          {{ props.row.lastCheckTime }}
        </q-td>
        <q-td key="status" :props="props">
          <span v-if="props.row.underQuery">
            <q-skeleton animation="blink" type="text" />
          </span>
          <span v-else>
            <span v-if="props.row.status === 'Unknown'">
              <q-badge color="yellow">
                <span class="text-black">{{ props.row.status }}</span>
              </q-badge>
            </span>
            <span v-else-if="props.row.status === 'Good'">
              <q-badge color="green">
                {{ props.row.status }}
              </q-badge>
            </span>
            <span v-else>
              <q-badge color="red">
                {{ props.row.status }}
              </q-badge>
            </span>
          </span>
        </q-td>
      </q-tr>
    </template>
    <template v-slot:top>
      <span class="col-6">Health Map</span>
      <span class="col-6 text-right q-gutter-xs">
        <q-btn
          size="sm"
          push
          color="white"
          text-color="primary"
          round
          icon="sync"
          @click="checkService('all')"
        />
      </span>
    </template>
    <template class="row text-caption" v-slot:bottom>
      <span class="col-6 q-py-sm"
        ><b>{{ pagination.rowsNumber }}</b> Services are under monitoring</span
      >
      <span class="col-6 q-py-sm text-right" v-html="checkTimeFull"></span>
    </template>
  </q-table>
</template>

<script>
import {
  defineComponent,
  inject,
  ref,
  computed,
  reactive,
  onMounted,
  onBeforeUnmount
} from 'vue'
import { date } from 'quasar'
import { useStore } from 'vuex'
import axios from 'axios'
// import { scroll } from 'quasar'
// import _ from 'lodash'

export default defineComponent({
  name: 'DHSMonitoringSystemPage',
  setup() {
    const isLogin = inject('isLogin') // get the root isLogin dict
    const CurData = inject('CurData') // get the root isLogin dict
    const CurShift = inject('CurShift') // get the root isLogin dict
    const injectChecker = ref()
    const localVer = ref('')
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const checkTime = ref('Null')
    const checkTimeFull = computed(() => {
      return `<b>Last checked</b> at <span class="text-red">${checkTime.value}</span>`
    })

    // define table columns
    const columns = [
      {
        name: 'service',
        align: 'center',
        label: 'Service',
        field: 'service'
      },
      {
        name: 'auditor',
        align: 'center',
        label: 'Auditor',
        field: 'auditor'
      },
      {
        name: 'detail',
        align: 'center',
        label: 'Detail',
        field: 'detail'
      },
      {
        name: 'lastCheckTime',
        align: 'center',
        label: 'lastCheckTime',
        field: 'lastCheckTime'
      },
      {
        name: 'status',
        align: 'center',
        label: 'Status',
        field: 'status'
      }
    ]

    const rows = ref([
      {
        service: 'WhatsUpGold',
        status: 'Unknown',
        auditor: 'Null',
        detail: 'Null',
        hyperlink:
          'http://10.99.25.64/NmConsole/Workspace/HomeWorkspace/HomeWorkspace.asp?HomeWorkspace.nWorkspaceID=10054',
        lastCheckTime: 'Null',
        underQuery: true
      },
      {
        service: 'PRTG_SUN',
        status: 'Unknown',
        auditor: 'Null',
        detail: 'Null',
        hyperlink:
          'http://10.99.25.209/sensors.htm?id=0&filter_status=5&filter_status=4&filter_status=13&filter_status=14',
        lastCheckTime: 'Null',
        underQuery: true
      },
      {
        service: 'PRTG_FRI',
        status: 'Unknown',
        auditor: 'Null',
        detail: 'Null',
        hyperlink:
          'http://10.99.25.212/sensors.htm?id=0&filter_status=5&filter_status=4&filter_status=13&filter_status=14',
        lastCheckTime: 'Null',
        underQuery: true
      },
      {
        service: 'JKB',
        status: 'Unknown',
        auditor: 'Null',
        detail: 'Null',
        hyperlink: 'http://larry.opsware.xyz:5056/',
        lastCheckTime: 'Null',
        underQuery: true
      },
      {
        service: 'PageDuty',
        status: 'Unknown',
        auditor: 'Null',
        detail: 'Null',
        hyperlink: 'http://10.7.6.221:6001/',
        lastCheckTime: 'Null',
        underQuery: true
      },
      {
        service: 'HM93',
        status: 'Unknown',
        auditor: 'Null',
        detail: 'Null',
        hyperlink: 'https://okta.opsware.xyz:9487/monitoringSystem/return/hm/pauseList93',
        lastCheckTime: 'Null',
        underQuery: true
      },
      {
        service: 'HM94',
        status: 'Unknown',
        auditor: 'Null',
        detail: 'Null',
        hyperlink: 'https://okta.opsware.xyz:9487/monitoringSystem/return/hm/pauseList94',
        lastCheckTime: 'Null',
        underQuery: true
      }
      // {
      //   service: 'HM81',
      //   status: 'Unknown',
      //   auditor: 'Null',
      //   detail: 'Null',
      //   hyperlink: 'https://okta.opsware.xyz:9487/monitoringSystem/return/hm/pauseList81',
      //   lastCheckTime: 'Null',
      //   underQuery: true
      // },
      // {
      //   service: 'HM82',
      //   status: 'Unknown',
      //   auditor: 'Null',
      //   detail: 'Null',
      //   hyperlink: 'https://okta.opsware.xyz:9487/monitoringSystem/return/hm/pauseList82',
      //   lastCheckTime: 'Null',
      //   underQuery: true
      // }
    ])

    onMounted(() => {
      // child component mounted but parent inject not ready, so need to use the setinternal to check if inject exist value
      injectChecker.value = setInterval(async () => {
        // use async / await to avoid to undefined res
        if (CurData.value && CurShift.value) {
          const res = await axios.get(
            `https://${ServiceDomainLocal}:9487/monitoringSystem/healthMap/query/${CurData.value}/${CurShift.value}`
          )
          if (res.status === 200) {
            // update by service name
            res.data.forEach(function (item, index, object) {
              if (Object.keys(item)[0] === 'verion') {
                localVer.value = Object.values(item)[0]
              } else {
                rows.value.forEach(function (item2, index2, object2) {
                  if (item2.service === Object.keys(item)[0]) {
                    object2[index2].status = Object.values(item)[0].status
                    object2[index2].auditor = Object.values(item)[0].auditor
                    object2[index2].detail = Object.values(item)[0].detail
                    object2[index2].lastCheckTime = Object.values(item)[0].lastCheckTime
                    object2[index2].underQuery = false
                  }
                })
              }
            })
            checkTime.value = date.formatDate(Date.now(), 'YYYY/MM/DD HH:mm')
          } else {
            // no row on DB
            checkTime.value = date.formatDate(Date.now(), 'YYYY/MM/DD HH:mm')
            rows.value.forEach(function (item, index, object) {
              object[index].underQuery = false
              object[index].status = 'Unknown'
              object[index].auditor = 'Null'
              object[index].detail = 'Null'
              object[index].lastCheckTime = 'Null'
            })
          }
          clearInterval(injectChecker.value)
          injectChecker.value = setInterval(async () => {
            console.log('hit second time checker')
            const res = await axios.get(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/healthMap/verion/${CurData.value}/${CurShift.value}`
            )
            if (localVer.value !== res.data) {
              isLogin.refreshMonitoringSystemKey += 1
            }
          }, 180000)
        }
      }, 2000)
    })

    onBeforeUnmount(() => {
      clearInterval(injectChecker.value)
    })

    async function checkService(target) {
      checkTime.value = date.formatDate(Date.now(), 'YYYY/MM/DD HH:mm')
      if (target !== 'all') {
        rows.value.forEach(function (item, index, object) {
          if (item.service === target) {
            object[index].underQuery = true
          }
        })
      }
      const postData = reactive({
        newEditor: isLogin.value,
        curDate: CurData.value,
        curShift: CurShift.value,
        timeStamp: checkTime.value
      })
      switch (target) {
        case 'all':
          // alert('check all service on backend')
          checkService('WhatsUpGold')
          checkService('PRTG_FRI')
          checkService('PRTG_SUN')
          checkService('PageDuty')
          // checkService('HM81')
          // checkService('HM82')
          checkService('HM93')
          checkService('HM94')
          checkService('JKB')
          break
        case 'WhatsUpGold':
          await axios
            .post(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/check/wug`,
              postData
            )
            .then((res) => {
              rows.value.forEach(function (item, index, object) {
                if (item.service === target) {
                  object[index].lastCheckTime = res.data.lastCheckTime
                  object[index].auditor = res.data.auditor
                  object[index].status = res.data.status
                  object[index].detail = res.data.detail
                  object[index].underQuery = false
                  localVer.value = res.data.verion
                }
              })
            })
            .catch((error) => {
              console.log(error)
            })
          break
        case 'PRTG_FRI':
          await axios
            .post(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/check/prtg/fri`,
              postData
            )
            .then((res) => {
              rows.value.forEach(function (item, index, object) {
                if (item.service === target) {
                  object[index].lastCheckTime = res.data.lastCheckTime
                  object[index].auditor = res.data.auditor
                  object[index].status = res.data.status
                  object[index].detail = res.data.detail
                  object[index].underQuery = false
                  localVer.value = res.data.verion
                }
              })
            })
            .catch((error) => {
              console.log(error)
            })
          break
        case 'PRTG_SUN':
          await axios
            .post(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/check/prtg/sun`,
              postData
            )
            .then((res) => {
              rows.value.forEach(function (item, index, object) {
                if (item.service === target) {
                  object[index].lastCheckTime = res.data.lastCheckTime
                  object[index].auditor = res.data.auditor
                  object[index].status = res.data.status
                  object[index].detail = res.data.detail
                  object[index].underQuery = false
                  localVer.value = res.data.verion
                }
              })
            })
            .catch((error) => {
              console.log(error)
            })
          break
        case 'PageDuty':
          await axios
            .post(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/check/pagerduty`,
              postData
            )
            .then((res) => {
              console.log()
              rows.value.forEach(function (item, index, object) {
                if (item.service === target) {
                  object[index].lastCheckTime = res.data.lastCheckTime
                  object[index].auditor = res.data.auditor
                  object[index].status = res.data.status
                  object[index].detail = res.data.detail
                  object[index].underQuery = false
                  localVer.value = res.data.verion
                }
              })
            })
            .catch((error) => {
              console.log(error)
            })
          break
        case 'JKB':
          await axios
            .post(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/check/jkb`,
              postData
            )
            .then((res) => {
              rows.value.forEach(function (item, index, object) {
                if (item.service === target) {
                  object[index].lastCheckTime = res.data.lastCheckTime
                  object[index].auditor = res.data.auditor
                  object[index].status = res.data.status
                  object[index].detail = res.data.detail
                  object[index].underQuery = false
                  localVer.value = res.data.verion
                }
              })
            })
            .catch((error) => {
              console.log(error)
            })
          break
        // case 'HM81':
        //   await axios
        //     .post(
        //       `https://${ServiceDomainLocal}:9487/monitoringSystem/check/hm/pauseList81`,
        //       postData
        //     )
        //     .then((res) => {
        //       rows.value.forEach(function (item, index, object) {
        //         if (item.service === target) {
        //           object[index].lastCheckTime = res.data.lastCheckTime
        //           object[index].auditor = res.data.auditor
        //           object[index].status = res.data.status
        //           object[index].detail = res.data.detail
        //           object[index].underQuery = false
        //           localVer.value = res.data.verion
        //         }
        //       })
        //     })
        //     .catch((error) => {
        //       console.log(error)
        //     })
        //   break
        // case 'HM82':
        //   await axios
        //     .post(
        //       `https://${ServiceDomainLocal}:9487/monitoringSystem/check/hm/pauseList82`,
        //       postData
        //     )
        //     .then((res) => {
        //       rows.value.forEach(function (item, index, object) {
        //         if (item.service === target) {
        //           object[index].lastCheckTime = res.data.lastCheckTime
        //           object[index].auditor = res.data.auditor
        //           object[index].status = res.data.status
        //           object[index].detail = res.data.detail
        //           object[index].underQuery = false
        //           localVer.value = res.data.verion
        //         }
        //       })
        //     })
        //     .catch((error) => {
        //       console.log(error)
        //     })
        //   break
        case 'HM93':
          await axios
            .post(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/check/hm/pauseList93`,
              postData
            )
            .then((res) => {
              rows.value.forEach(function (item, index, object) {
                if (item.service === target) {
                  object[index].lastCheckTime = res.data.lastCheckTime
                  object[index].auditor = res.data.auditor
                  object[index].status = res.data.status
                  object[index].detail = res.data.detail
                  object[index].underQuery = false
                  localVer.value = res.data.verion
                }
              })
            })
            .catch((error) => {
              console.log(error)
            })
          break
        case 'HM94':
          await axios
            .post(
              `https://${ServiceDomainLocal}:9487/monitoringSystem/check/hm/pauseList94`,
              postData
            )
            .then((res) => {
              rows.value.forEach(function (item, index, object) {
                if (item.service === target) {
                  object[index].lastCheckTime = res.data.lastCheckTime
                  object[index].auditor = res.data.auditor
                  object[index].status = res.data.status
                  object[index].detail = res.data.detail
                  object[index].underQuery = false
                  localVer.value = res.data.verion
                }
              })
            })
            .catch((error) => {
              console.log(error)
            })
          break
        default:
          alert(`check ${target} service on backend`)
          console.log(target)
          checkTime.value = date.formatDate(Date.now(), 'YYYY/MM/DD HH:mm')
          rows.value.forEach(function (item, index, object) {
            if (item.service === target) {
              object[index].lastCheckTime = date.formatDate(
                Date.now(),
                'YYYY/MM/DD HH:mm'
              )
            }
          })
          break
      }
    }

    return {
      isLogin,
      columns,
      rows,
      pagination: ref({
        rowsPerPage: 0,
        rowsNumber: 9
      }),
      checkTime,
      checkTimeFull,
      checkService
    }
  }
})
</script>

<style lang="scss">
a.customWithNone {
  text-decoration: none;
}

td.customPaddingQTbx {
  padding: 4px !important;
}
</style>
