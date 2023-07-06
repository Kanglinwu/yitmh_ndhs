<!-- @format -->

<template>
  <div class="q-px-lg q-pb-md">
    <q-timeline :layout="layout" color="secondary">
      <q-timeline-entry
        :subtitle="'Total comments - ' + localCommentList.length"
        color="red"
        icon="tag"
      >
      </q-timeline-entry>
      <!-- <q-timeline-entry
        :title="'Handling by ' + localContainer.CreateBy.editor"
        :subtitle="localContainer.CreateBy.date + '-' + localContainer.CreateBy.shift"
        color="orange"
        :avatar="
          'https://' +
          ServiceDomainLocal +
          ':9487/review/avatar/' +
          localContainer.CreateBy.editor
        "
      >
        <div v-html="localContainer.CreateBy.summary"></div>
      </q-timeline-entry> -->
      <q-timeline-entry
        v-for="(value, index) in localCommentList"
        :key="index"
        :title="'Update by ' + value.handler"
        :subtitle="value.timestamp"
        color="green"
        :side="value.commentType == 1 ? 'right' : 'left'"
        :avatar="'https://' + ServiceDomainLocal + ':9487/review/avatar/' + value.handler"
      >
        <div v-html="value.content"></div>
      </q-timeline-entry>
    </q-timeline>
  </div>
</template>

<script>
import { defineComponent, onMounted, ref, computed } from 'vue'
// import { defineComponent, onMounted, reactive, ref } from 'vue'import { computed } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import { useQuasar } from 'quasar'

export default defineComponent({
  name: 'DHSReviewPageComments',
  props: {
    targetSn: Number
  },
  setup(props) {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const localCommentList = ref([])
    // const localContainer = reactive({
    //   CreateBy: {},
    //   UpdateList: [],
    //   dayCounter: '',
    //   diff: []
    // })

    onMounted(async () => {
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/bpOTRS/jsm/get/allcomments/${props.targetSn}`
      )
      localCommentList.value = res.data
      // for (const [key, value] of Object.entries(res.data)) {
      //   localContainer[key] = value
      //   if (key === 'diff') {
      //     if (value.length !== 0) {
      //       console.log(value)
      //       // const DMP = new window.diff_match_patch()
      //       // const d = DMP.diff_main(value[1], value[2])
      //       // const ds = DMP.diff_prettyHtml(d)
      //       // console.log(ds)
      //     }
      //   }
      // }
    })
    return {
      localCommentList,
      ServiceDomainLocal,
      layout: computed(() => {
        return $q.screen.lt.sm ? 'dense' : $q.screen.lt.md ? 'comfortable' : 'loose'
      })
    }
    // return {
    //   localContainer,
    //   ServiceDomainLocal,
    //   expanded: ref(false)
    // }
  }
})
</script>

<style lang="scss">
div.custWordBreak {
  word-break: break-word;
}
</style>
