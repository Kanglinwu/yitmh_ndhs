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
    <template v-slot:top>
      <span class="col-6">ICP Status</span>
      <span class="col-6 text-right q-gutter-xs">
        <q-btn
          size="sm"
          push
          color="white"
          text-color="primary"
          round
          icon="add_circle"
          disabled
        />
        <q-btn
          size="sm"
          push
          color="white"
          text-color="primary"
          round
          icon="sync"
          @click="forceCheckICP"
        />
      </span>
    </template>
    <template v-slot:header-cell="props">
      <q-th :props="props">
        <b>{{ props.col.label }}</b>
      </q-th>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="domain" :props="props">
          <span v-if="underQuery">
            <q-skeleton animation="blink" type="text" />
          </span>
          <span v-else>
            {{ props.row.domain }}
          </span>
        </q-td>
        <q-td key="icpNumber" :props="props">
          <span v-if="underQuery">
            <q-skeleton animation="blink" type="text" />
          </span>
          <span v-else>
            {{ props.row.icpNumber }}
          </span>
        </q-td>
        <q-td key="status" :props="props">
          <span v-if="underQuery">
            <q-skeleton animation="blink" type="text" />
          </span>
          <span v-else>
            <span v-if="props.row.status === 'Good'">
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
    <template class="row text-caption" v-slot:bottom>
      <span class="col-6 q-py-sm">
        <span v-if="underQuery">Checking</span>
        <span v-else
          >Total Domain: <b>{{ pagination.rowsNumber }}</b></span
        >
      </span>
      <span class="col-6 text-right" v-html="checkTimeFull"></span>
    </template>
  </q-table>
</template>

<script>
import { defineComponent, inject, onMounted, ref, computed } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import { date, useQuasar } from 'quasar'
// import { scroll } from 'quasar'
// import _ from 'lodash'

export default defineComponent({
  name: 'DHSNotePage',
  setup() {
    const $q = useQuasar()
    const isLogin = inject('isLogin') // get the root isLogin dict
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain

    const pagination = ref({
      rowsPerPage: 0,
      rowsNumber: 0
    })

    const checkTime = ref('')
    const checkTimeFull = computed(() => {
      return `<b>Last checked</b> at <span class="text-red">${checkTime.value}</span>`
    })

    // define table columns
    const columns = [
      {
        name: 'domain',
        align: 'center',
        label: 'Domain',
        field: 'domain'
      },
      {
        name: 'icpNumber',
        align: 'center',
        label: 'ICP Number',
        field: 'icpNumber'
      },
      {
        name: 'status',
        align: 'center',
        label: 'Status',
        field: 'status'
      }
    ]

    const rows = ref([])
    const underQuery = ref(true)

    onMounted(() => {
      axios
        .get(`https://${ServiceDomainLocal}:9487/icp/query`)
        .then((response) => {
          pagination.value.rowsNumber = response.data.length
          checkTime.value = response.data[0].current_time
          response.data.forEach((element) => {
            rows.value.push({
              domain: element.each_domain,
              icpNumber: element.icp_number,
              status: element.icp_number !== 'no icp' ? 'Good' : 'Error'
            })
          })
          underQuery.value = false
        })
        .catch((error) => {
          console.log(error)
        })
    })

    function forceCheckICP() {
      // get current time
      const timeStamp = Date.now()
      const currentTime = parseInt(date.formatDate(timeStamp, 'x'), 10)
      // get last time
      const lastCheckTime = Date.parse(checkTime.value)
      // get gap
      const gap = currentTime - lastCheckTime
      if (gap < 1800000) {
        const returnMin = 30 - (parseInt(((gap * 30) / 1800000), 10))
        console.log(returnMin)
        $q.notify({
          message: `<b>[FAILED]</b> checker limitation - interval: 30 mins, please try it after <b>${returnMin}</b> mins`,
          color: 'red-12',
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
      } else {
        // console.log('do the check')
        underQuery.value = true
        axios
          .get(`https://${ServiceDomainLocal}:9487/icp/check`)
          .then((response) => {
            if (response.data === 200) {
              $q.notify({
                message: '[SUCCESS] Update ICP status table',
                color: 'green-12',
                textColor: 'dark',
                progress: true,
                actions: [
                  {
                    icon: 'cancel',
                    color: 'white',
                    handler: () => {}
                  }
                ]
              })
              isLogin.refreshICPKey += 1
            } else {
              underQuery.value = false
              $q.notify({
                message: '[FAILED] connection error - check it later after',
                color: 'red-12',
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
            console.log(response)
          })
          .catch((error) => {
            console.log(error)
            underQuery.value = false
            $q.notify({
              message: '[FAILED] connection error - check it later',
              color: 'red-12',
              progress: true,
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
    }

    return {
      isLogin,
      ServiceDomainLocal,
      columns,
      rows,
      checkTime,
      checkTimeFull,
      pagination,
      forceCheckICP,
      underQuery
    }
  }
})
</script>

<style lang="sass">
.my-sticky-header-table
  .q-table__top,
  .q-table__bottom
    background-color: #ECEFF1
  .q-table th
    font-weight: bold !important
  .q-table td
    text-overflow: ellipsis !important
    word-wrap: break-word !important
    word-break: break-all !important
</style>
