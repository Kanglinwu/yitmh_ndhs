<!-- @format -->

<template>
  <div
    class="q-px-lg q-pb-md"
    :class="{ 'bg-teal-1': source === 'fromSearch' || 'fromIncident' }"
  >
    <q-timeline color="secondary">
      <q-timeline-entry
        v-if="source !== 'fromIncident'"
        :subtitle="'How long - ' + localContainer.dayCounter"
        color="red"
        icon="timer"
      >
      </q-timeline-entry>
      <q-timeline-entry
        :title="'Create by ' + localContainer.CreateBy.editor"
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
      <!-- <q-timeline-entry heading> {{ localContainer.dayCounter }} </q-timeline-entry>
      <section>
        {{ localContainer.CreateBy }}
      </section>-->
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
    <section class="flex q-px-md q-gutter-xs">
      <div
        v-for="(value, index) in localContainer.AttachmentList"
        :key="index"
        :class="
          value.fileType !== 'png' && value.fileType !== 'jpg'
            ? 'order-last'
            : 'order-first'
        "
      >
        <div
          v-if="value.fileType !== 'png' && value.fileType !== 'jpg'"
          class="cursor-pointer text-subtitle2 bg-blue-grey-2 q-pa-xs rounded-borders"
          @click.self="popuptheattachment(value.sn)"
        >
          <q-avatar rounded>
            <img
              :src="
                'https://' +
                ServiceDomainLocal +
                ':9487/bpNote/attachment/review/' +
                value.sn
              "
            />
          </q-avatar>
          {{ value.fileName }}
        </div>
        <div v-else>
          <img
            @click.self="popuptheattachment(value.sn)"
            class="cursor-pointer"
            style="max-width: 75px"
            :alt="value.fileName"
            :src="
              'https://' +
              ServiceDomainLocal +
              ':9487/bpNote/attachment/review/' +
              value.sn
            "
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { defineComponent, onMounted, reactive } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

export default defineComponent({
  name: 'DHSNoteListLog',
  props: {
    title: String,
    source: String
  },
  setup(props) {
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const localContainer = reactive({
      CreateBy: {},
      UpdateList: [],
      dayCounter: '',
      AttachmentList: []
    })

    function popuptheattachment(targetSn) {
      window.open(
        `https://${ServiceDomainLocal}:9487/bpNote/attachment/get/${targetSn}`,
        '_blank'
      )
    }

    onMounted(async () => {
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/notes/traceLog/${props.source}/${props.title}`
      )
      for (const [key, value] of Object.entries(res.data)) {
        localContainer[key] = value
      }
    })
    return {
      localContainer,
      ServiceDomainLocal,
      popuptheattachment
    }
  }
})
</script>
