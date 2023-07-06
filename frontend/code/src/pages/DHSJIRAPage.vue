<!-- @format -->
<template>
  <!-- <DHSOTRSList
    v-for="item in sortOtrsSet"
    :key="item.sn"
    v-bind="item"
    @adjustOTRSKpiOnlyListToPage="kpiUpdateOnOTRSList"
  /> -->
  <JiraTicketList
    v-for="item in sortJiraList"
    :key="item.ticketSn"
    v-bind="item"
    @adjustJIRAKpiOnlyListToPage="kpiUpdateOnJIRAList"
  />
</template>
<script>
// import DHSOTRSList from 'components/DHSOTRSList.vue'
import JiraTicketList from 'components/JiraTicketList.vue'

import { defineComponent, onMounted, inject, reactive, watch, computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import axios from 'axios'
import _ from 'lodash'

export default defineComponent({
  name: 'DHSJIRAPage',
  components: {
    // DHSOTRSList
    JiraTicketList
  },
  setup() {
    const $q = useQuasar()
    const isLogin = inject('isLogin') // get the root isLogin dict
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const JiraList = reactive({})
    const sortJiraList = computed(() => _.orderBy(JiraList, 'ticketSn', ['desc'])) // order by noteSet.sequence

    onMounted(async () => {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/query/all_issues/jiraTicketList`)
        .then((response) => {
          response.data.forEach((ele) => {
            JiraList[ele.ticketSn] = ele
          })
          // JiraList = Object.assign([], response.data.jiraList)
        })
        .catch((error) => {
          console.log(error)
        })
    })

    // kpi update from child ( kpi )
    function kpiUpdateOnJIRAList(targetObject) {
      // targetObject = [ticketSn, kpiSn]
      // const newKpiDict = { otrsSn: props.sn, newKpiSn: newKpiSn }
      console.log('hit kpiUpdateOnJIRAList on JIRA PAGE')
      console.log(targetObject[0])
      console.log((JiraList[targetObject[0]].flagKpiSn = targetObject[1]))
      // otrsSet[targetObject.otrsSn].kpi_result = targetObject.newKpiSn
    }

    // Update all component here
    watch(
      () => isLogin.refreshJIRAStep,
      (curKey, oldKey) => {
        axios
          .get(`https://${ServiceDomainLocal}:9487/query/all_issues/jiraTicketList`)
          .then(async (response) => {
            response.data.forEach((ele, index, object) => {
              if (isLogin.refreshJIRAUnderEditingList.includes(ele.ticketSn)) {
                console.log(`lock for ${ele.ticketSn}`)
              } else {
                JiraList[ele.ticketSn] = ele
              }
            })
          })
          .catch((error) => {
            console.log(error)
          })
      }
    )

    // adjust the display by parent isLogin.filterJiraTicket
    watch(
      () => isLogin.filterJiraTicket,
      (curFilterStatus, oldFilterStatus) => {
        const tmpCounter = ref(0)
        for (const [key, object] of Object.entries(JiraList)) {
          if (curFilterStatus === 'All') {
            JiraList[key].isDisplay = true
            tmpCounter.value++
          } else {
            if (object.flagJiraTicketStatus !== curFilterStatus) {
              JiraList[key].isDisplay = false
            } else {
              JiraList[key].isDisplay = true
              tmpCounter.value++
            }
          }
        }
        $q.notify({
          message: curFilterStatus === 'All' ? `Display all JIRA Ticket, Total ticket counter: <b>${tmpCounter.value}</b>` : `Filter all JIRA Ticket status match ${curFilterStatus}, result counter: <b>${tmpCounter.value}</b>`,
          color: 'green-12',
          textColor: 'dark',
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
    )

    return {
      JiraList,
      sortJiraList,
      kpiUpdateOnJIRAList
    }
  }
})
</script>
