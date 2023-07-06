<!-- @format -->

<template>
  <div class="q-px-lg q-pb-md" :class="{ 'bg-teal-1': source === 'fromSearch' }">
    <q-timeline color="secondary">
      <q-timeline-entry
        :subtitle="'How long - ' + localContainer.dayCounter"
        color="red"
        icon="timer"
      >
      </q-timeline-entry>
      <q-timeline-entry
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
      </q-timeline-entry>
      <q-timeline-entry
        v-for="(value, index) in localContainer.UpdateList"
        :key="index"
        :title="'Update by ' + value.editor"
        :subtitle="value.date + '-' + value.shift"
        color="green"
        :avatar="'https://' + ServiceDomainLocal + ':9487/review/avatar/' + value.editor"
      >
        <div v-html="value.updateSummary"></div>
      </q-timeline-entry>
    </q-timeline>
    <q-separator color="indigo-1" class="q-pb-xs q-mb-md" />
    <section class="row q-px-md q-gutter-xs full-width">
      <q-list class="full-width dense" bordered separator>
        <q-expansion-item
          group="somegroup"
          v-for="(value, index) in localContainer.diff"
          :key="index"
          :label="'Content adjust - ' + value[0]"
        >
          <q-card class="row q-pa-md custWordBreak">
            <q-card-section class="col-4 column">
              <div class="text-center bg-blue-grey-2 text-bold q-mx-xs">
                {{ value[2] }}
              </div>
              <div class="q-mx-md" v-html="value[3]"></div>
            </q-card-section>
            <q-card-section class="col-4 column">
              <div class="text-center bg-blue-grey-2 text-bold q-mx-xs">
                {{ value[0] }}
              </div>
              <div class="q-mx-md" v-html="value[5]"></div>
            </q-card-section>
            <q-card-section class="col-4 column">
              <div class="text-center bg-blue-grey-2 text-bold">Show the diff</div>
              <div class="q-mx-md" v-html="value[1]"></div>
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </q-list>
    </section>
  </div>
</template>

<script>
import { defineComponent, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

export default defineComponent({
  name: 'DHSOTRSListLog',
  props: {
    ticketNumber: Number,
    source: String
  },
  setup(props) {
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const localContainer = reactive({
      CreateBy: {},
      UpdateList: [],
      dayCounter: '',
      diff: []
    })

    onMounted(async () => {
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/bpOTRS/traceLog/${props.ticketNumber}`
      )
      console.log(res)
      for (const [key, value] of Object.entries(res.data)) {
        localContainer[key] = value
        if (key === 'diff') {
          if (value.length !== 0) {
            console.log(value)
            // const DMP = new window.diff_match_patch()
            // const d = DMP.diff_main(value[1], value[2])
            // const ds = DMP.diff_prettyHtml(d)
            // console.log(ds)
          }
        }
      }
    })
    return {
      localContainer,
      ServiceDomainLocal,
      expanded: ref(false)
    }
  }
})
</script>

<style lang="scss">
div.custWordBreak {
  word-break: break-word;
}
</style>
