<!-- @format -->
<template>
  <div class="q-pa-md">
    <q-dialog class="bg-teal-1" v-model="isShowTraceLog" full-width>
      <DHSNoteListLog :key="noteListKey" :title="curTitle" source="fromIncident"></DHSNoteListLog>
    </q-dialog>
    <q-table title="EVENT SUMMARY" :rows="rows" :columns="columns" row-key="name" :pagination="pagination">
      <template v-slot:body-cell-customer="props">
        <q-td :props="props">
          <q-badge class="q-mr-xs" v-for="x in props.value" color="blue-2" text-color="black" :label="x" :key="x" />
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <q-badge :color="props.value === 'Red' ? 'red' : 'yellow'"
            :text-color="props.value === 'Red' ? 'white' : 'black'" :label="props.value" />
        </q-td>
      </template>
      <template v-slot:body-cell-impactby="props">
        <q-td :props="props">
          <q-badge color="blue-2" text-color="black" :label="props.value" />
        </q-td>
      </template>
      <template v-slot:body-cell-note="props">
        <q-td :props="props">
          <span class="text-italic text-blue-8 cursor-pointer" @click="openToRelatedPage(props.row.jira_ticket)">{{
              props.value
          }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
<script>
import DHSNoteListLog from 'components/DHSNoteListLog.vue'
import { defineComponent, onMounted, ref } from 'vue'
import axios from 'axios'
import { useStore } from 'vuex'
import _ from 'lodash'
// import { date } from 'quasar'
// import { defineComponent, ref, computed, reactive, onMounted, onBeforeUnmount } from 'vue'
// import { useRouter } from 'vue-router'
// import { scroll } from 'quasar'

export default defineComponent({
  name: 'IncidentReviewPage',
  components: {
    DHSNoteListLog
  },
  setup() {
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const isShowTraceLog = ref(false)
    const noteListKey = ref(0)
    const curTitle = ref('')
    const pagination = ref({
      rowsPerPage: 0
    })

    const columns = [
      {
        name: 'data',
        required: true,
        label: 'date',
        field: 'date',
        align: 'left',
        sortable: true
      },
      {
        name: 'event_start_time',
        align: 'left',
        label: 'start_at',
        field: 'event_start_time'
      },
      { name: 'event_end_time', label: 'end_at', align: 'left', field: 'event_end_time' },
      {
        name: 'outage_time',
        label: 'outage_time (mins)',
        align: 'left',
        field: 'outage_time'
      },
      { name: 'note', label: 'refer', align: 'left', field: 'note' },
      {
        name: 'customer',
        label: 'affected_customer',
        align: 'left',
        field: 'customer'
      },
      {
        name: 'status',
        label: 'outage_level',
        align: 'left',
        field: 'status'
      },
      { name: 'impactby', label: 'root_cause', align: 'left', field: 'impactby' }
    ]

    const rows = ref([])

    function openToRelatedPage(targetList) {
      if (targetList[0] === 'note') {
        curTitle.value = targetList[1].toString()
        isShowTraceLog.value = true
      } else if (targetList[0] === 'otrs') {
        openOTRSPage(targetList[1])
      }
    }

    function openOTRSPage(otrsNumber) {
      console.log(otrsNumber)
      const targetId = ref(0)
      if (otrsNumber >= 92027180) {
        targetId.value = otrsNumber - 92000009
      } else if (otrsNumber >= 92022525) {
        targetId.value = otrsNumber - 91999956
      } else {
        targetId.value = otrsNumber - 91999952
      }
      window.open(
        `http://172.23.1.44/otrs/index.pl?Action=AgentTicketZoom;TicketID=${targetId.value}`,
        '_blank'
      )
    }

    onMounted(async () => {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/monitoringSystem/Incident/query`)
        .then((response) => {
          console.log(response.data)
          rows.value = _.cloneDeep(response.data)
        })
        .catch((error) => {
          console.log(error)
        })
    })

    return {
      columns, rows, openToRelatedPage, isShowTraceLog, noteListKey, curTitle, pagination
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

<style lang="sass">
.my-sticky-header-table
  .q-table__top,
  .q-table__bottom
    background-color: #ECEFF1
  .q-table th
    font-weight: bold !important
  .q-table td
    text-overflow: ellipsis !important
</style>
