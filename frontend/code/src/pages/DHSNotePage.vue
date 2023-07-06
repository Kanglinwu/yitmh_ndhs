<!-- @format -->
<template>
  <DHSNoteList
    @adjustNoteKpiOnlyListToPage="kpiUpdateOnNoteList"
    v-for="note in sortNoteSet"
    :key="note.sn"
    v-bind="note"
    :isHidden="localDefineIsHiddenDeleteNote"
  />
</template>
<script>
import DHSNoteList from 'components/DHSNoteList.vue'

import {
  defineComponent,
  reactive,
  onMounted,
  computed,
  nextTick,
  inject,
  ref,
  watch
} from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import { scroll } from 'quasar'
import _ from 'lodash'

export default defineComponent({
  name: 'DHSNotePage',
  components: {
    DHSNoteList
  },
  setup() {
    const $store = useStore()
    const noteSet = reactive({})
    const sortNoteSet = computed(() => _.orderBy(noteSet, 'sequence')) // order by noteSet.sequence
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const { getScrollTarget, setVerticalScrollPosition } = scroll // scroll function
    const isLogin = inject('isLogin') // get the root isLogin dict
    const localDefineIsHiddenDeleteNote = ref(null)

    onMounted(() => {
      // console.log('hit DHS NOTE PAGE onMounted')
      axios
        .get(`https://${ServiceDomainLocal}:9487/notes/query/all`)
        .then(async (response) => {
          response.data.forEach((ele) => {
            noteSet[ele.sn] = ele
          })
          // wait for child component loaded
          await nextTick()
          // if isLogin.keepNoteSn !== 0, means component has been re-created due to user add new note, then hit this, will scroll to target
          if (isLogin.keepNoteSn !== 0) {
            const ele = document.getElementById('note' + isLogin.keepNoteSn)
            const target = getScrollTarget(ele)
            const offset = ele.offsetTop - 55
            const duration = 200
            setVerticalScrollPosition(target, offset, duration)
            isLogin.keepNoteSn = 0
          }
        })
        .catch((error) => {
          console.log(error)
        })
      // when true, means delete ticket will show on the dashboard, otherwise reverse
      localDefineIsHiddenDeleteNote.value = isLogin.isHiddenDelNote
    })

    // kpi update from child ( kpi )
    function kpiUpdateOnNoteList(targetObject) {
      // targetList = {kpiGroup: 460, kpisn: 1856, noteSn: 35108}
      // adjust the kpi_result then component - DHSNoteList will auto update
      noteSet[targetObject.noteSn].kpi_result = targetObject.kpisn
      noteSet[targetObject.noteSn].kpi_group = targetObject.kpiGroup
    }

    // To watch this value to make DHSNoteList delete note will display or not
    watch(
      () => isLogin.isHiddenDelNote,
      (curKey, oldKey) => {
        localDefineIsHiddenDeleteNote.value = curKey
      }
    )

    // Update all component here
    watch(
      () => isLogin.refreshNoteStep,
      (curKey, oldKey) => {
        // console.log('hit DHSNotePage watch')
        axios
          .get(`https://${ServiceDomainLocal}:9487/notes/query/all`)
          .then(async (response) => {
            response.data.forEach((ele) => {
              if (isLogin.refreshNoteUnderEditingList.includes(ele.sn)) {
                console.log(`lock for ${ele.sn}`)
              } else {
                noteSet[ele.sn] = ele
              }
            })
          })
          .catch((error) => {
            console.log(error)
          })
      }
    )

    return {
      noteSet,
      sortNoteSet,
      kpiUpdateOnNoteList,
      localDefineIsHiddenDeleteNote
    }
  }
})
</script>
