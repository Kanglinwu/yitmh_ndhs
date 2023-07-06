<!-- @format -->
<template>
  <DHSOTRSList v-for="item in sortOtrsSet" :key="item.sn" v-bind="item"
    @adjustOTRSKpiOnlyListToPage="kpiUpdateOnOTRSList" />
</template>
<script>
import DHSOTRSList from 'components/DHSOTRSList.vue'

import {
  defineComponent,
  onMounted,
  reactive,
  computed,
  inject,
  watch
  // nextTick,
  // ref,
} from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import _ from 'lodash'
// import { scroll } from 'quasar'

export default defineComponent({
  name: 'DHSOTRSPage',
  components: {
    DHSOTRSList
  },
  setup() {
    const isLogin = inject('isLogin') // get the root isLogin dict
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const otrsSet = reactive({})
    const sortOtrsSet = computed(() => _.orderBy(otrsSet, ['customer', 'sequence'])) // order by noteSet.sequence , revserve by -> ['asc', 'desc']
    // const { getScrollTarget, setVerticalScrollPosition } = scroll // scroll function
    // const localDefineIsHiddenDeleteNote = ref(null)

    onMounted(async () => {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/bpOTRS/query/all`)
        .then(async (response) => {
          response.data.forEach((ele) => {
            otrsSet[ele.sn] = ele
          })
        })
        .catch((error) => {
          console.log(error)
        })
      // console.log(otrsSet)
      // when true, means delete ticket will show on the dashboard, otherwise reverse
      // localDefineIsHiddenDeleteNote.value = isLogin.isHiddenDelNote
      // console.log(otrsSet)
      // console.log(sortOtrsSet)
    })

    // kpi update from child ( kpi )
    function kpiUpdateOnOTRSList(targetObject) {
      // const newKpiDict = { otrsSn: props.sn, newKpiSn: newKpiSn }
      console.log('hit kpiUpdateOnOTRSList on OTRS PAGE')
      otrsSet[targetObject.otrsSn].kpi_result = targetObject.newKpiSn
    }

    // // To watch this value to make DHSNoteList delete note will display or not
    // watch(
    //   () => isLogin.isHiddenDelNote,
    //   (curKey, oldKey) => {
    //     localDefineIsHiddenDeleteNote.value = curKey
    //   }
    // )

    // Update all component here
    watch(
      () => isLogin.refreshOTRSStep,
      (curKey, oldKey) => {
        axios
          .get(`https://${ServiceDomainLocal}:9487/bpOTRS/query/all`)
          .then(async (response) => {
            response.data.forEach((ele) => {
              if (isLogin.refreshOTRSUnderEditingList.includes(ele.sn)) {
                console.log(`lock for ${ele.sn}`)
              } else {
                otrsSet[ele.sn] = ele
                // otrsSet[ele.sn].flagCloseTicket = ele.flagCloseTicket
                // otrsSet[ele.sn].kpi_result = ele.kpi_result
                // otrsSet[ele.sn].maintenance = ele.maintenance
                // otrsSet[ele.sn].sequence = ele.sequence
                // otrsSet[ele.sn].status = ele.status
                // otrsSet[ele.sn].update_by = ele.update_by
                // otrsSet[ele.sn].summary = ele.summary
                // otrsSet[ele.sn].update_summary = ele.update_summary
              }
            })
          })
          .catch((error) => {
            console.log(error)
          })
      }
    )

    return {
      otrsSet,
      sortOtrsSet,
      kpiUpdateOnOTRSList
      // localDefineIsHiddenDeleteNote
    }
  }
})
</script>
