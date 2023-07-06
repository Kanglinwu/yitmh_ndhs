<!-- @format -->

<template>
  <q-ajax-bar
    ref="axiosExecuteBar"
    position="bottom"
    color="secondary"
    size="10px"
    skip-hijack
  />
  <section class="q-pa-md">
    <q-table
      title="CLOSE TICKETS"
      :rows="localSet.rows"
      :columns="columns"
      :pagination="pagination"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon-right="archive"
          label="Export to csv"
          no-caps
          @click="exportTable"
        />
      </template>
      <template v-slot:header="props">
        <q-tr :props="props">
          <q-th v-for="col in props.cols" :key="col.name" :props="props">
            {{ col.label }}
          </q-th>
          <q-th auto-width> Reopen ticket </q-th>
        </q-tr>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="jsm" :props="props">
            <span
              class="text-blue cursor-pointer"
              @click="openNewPageToTicket(props.row.issueKey)"
              >{{ props.row.jsm }}</span
            >
          </q-td>
          <q-td key="category" :props="props">
            <q-badge
              class="q-mr-xs text-caption"
              v-for="x in props.row.category"
              color="blue-2"
              text-color="black"
              :label="x"
              :key="x"
            />
          </q-td>
          <q-td key="handler" :props="props">
            <span v-if="props.row.handler !== ''">
              <q-badge
                class="q-mr-xs text-caption"
                v-for="x in props.row.handler"
                color="green-2"
                text-color="black"
                :label="x"
                :key="x"
              />
            </span>
            <span v-if="props.row.participant !== ''">
              <q-badge
                class="q-mr-xs text-caption"
                v-for="x in props.row.participant"
                color="amber-2"
                text-color="black"
                :label="x"
                :key="x"
              />
            </span>
          </q-td>
          <q-td key="timestamp" :props="props">
            <q-tooltip class="bg-indigo" :offset="[10, 10]">
              <div class="text-subtitle2">Start at {{ props.row.timestamp[0] }}</div>
              <div class="text-subtitle2">Finish at {{ props.row.timestamp[1] }}</div>
            </q-tooltip>
            {{ props.row.timestamp[2] }}
          </q-td>
          <q-td class="text-center customPaddingQTbx" auto-width>
            <q-btn
              size="sm"
              class="text-center"
              push
              color="white"
              text-color="primary"
              round
              dense
              icon="lock_open"
              @click="popuptoAsk(props.row.issueKey, props.row.issueId, props.row.sn)"
            />
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-table
      v-if="localSet.isAdmin"
      class="q-my-md"
      title="REVIEW TABLE"
      :rows="localSet.effRow"
      :columns="effColumns"
      :pagination="paginationEff"
    >
      <template v-slot:body-cell-ticketNumber="props">
        <q-td :props="props">
          <span
            class="text-blue cursor-pointer text-caption"
            @click="openNewPageToTicket(props.value[0])"
            >{{ props.value[1] }}</span
          >
        </q-td>
      </template>
      <template v-slot:body-cell-content="props">
        <q-td :props="props">
          <div v-html="props.value"></div>
        </q-td>
      </template>
      <template v-slot:body-cell-updater="props">
        <q-td :props="props">
          <q-badge
            class="q-mr-xs text-caption"
            :label="props.value"
            color="green-2"
            text-color="black"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <q-badge
            class="q-mr-xs text-caption"
            v-for="x in props.value"
            color="blue-2"
            text-color="black"
            :label="x"
            :key="x"
          />
        </q-td>
      </template>
    </q-table>
  </section>
</template>

<script>
import { defineComponent, watch, onMounted, reactive, ref } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import { exportFile, useQuasar } from 'quasar'
import _ from 'lodash'
export default defineComponent({
  name: 'HistroyPage',
  props: {
    username: String,
    whichTeam: String,
    startQuery: Boolean
  },
  setup(props) {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const axiosExecuteBar = ref(null)
    const localSet = reactive({
      url: '',
      rows: [],
      isAdmin: false,
      effRow: []
    })

    const effColumns = [
      {
        name: 'ticketNumber',
        label: 'JSM',
        align: 'left',
        field: 'ticketNumber',
        sortable: true
      },
      {
        name: 'category',
        label: 'Category',
        align: 'left',
        field: 'category',
        sortable: true
      },
      {
        name: 'updater',
        align: 'left',
        label: 'Who',
        field: 'updater',
        sortable: true
      },
      { name: 'content', label: 'Content', align: 'left', field: 'content' },
      {
        name: 'at',
        label: 'Update at',
        field: 'at',
        align: 'left',
        sortable: true
      }
    ]

    const columns = [
      { name: 'jsm', label: 'JSM', align: 'left', field: 'jsm' },
      { name: 'category', label: 'Category', align: 'left', field: 'category' },
      {
        name: 'handler',
        label: 'Handler & Participant',
        align: 'left',
        field: 'handler'
      },
      {
        name: 'timestamp',
        required: true,
        label: 'Cost',
        field: 'timestamp',
        align: 'left',
        sortable: true
      }
    ]

    async function callDefaultHistory() {
      await axios
        .get(localSet.url)
        .then((res) => {
          localSet.rows = _.cloneDeep(res.data)
        })
        .catch((error) => {
          console.log(error)
        })
    }

    async function callCommentsHistory(team) {
      const postData = {
        group: team
      }
      await axios
        .post(`https://${ServiceDomainLocal}:9487/bpCowork/jsm/query/comments`, postData)
        .then((res) => {
          console.log(res.data)
          localSet.effRow = _.cloneDeep(res.data)
        })
        .catch((error) => {
          console.log(error)
        })
    }

    // export csv
    function wrapCsvValue(val, formatFn) {
      let formatted = formatFn !== void 0 ? formatFn(val) : val

      formatted = formatted === void 0 || formatted === null ? '' : String(formatted)

      formatted = formatted.split('"').join('""')
      /**
       * Excel accepts \n and \r in strings, but some other CSV parsers do not
       * Uncomment the next two lines to escape new lines
       */
      // .split('\n').join('\\n')
      // .split('\r').join('\\r')

      return `"${formatted}"`
    }

    // button for export csv
    function exportTable() {
      // naive encoding to csv format
      const content = [columns.map((col) => wrapCsvValue(col.label))]
        .concat(
          localSet.rows.map((row) =>
            columns
              .map((col) =>
                wrapCsvValue(
                  typeof col.field === 'function'
                    ? col.field(row)
                    : row[col.field === void 0 ? col.name : col.field],
                  col.format
                )
              )
              .join(',')
          )
        )
        .join('\r\n')

      const status = exportFile('table-export.csv', content, 'text/csv')

      if (status !== true) {
        $q.notify({
          message: 'Browser denied file download...',
          color: 'negative',
          icon: 'warning'
        })
      }
    }

    function openNewPageToTicket(jsm) {
      const url = `https://ict888.atlassian.net/browse/${jsm}`
      window.open(url, '_blank')
    }

    function popuptoAsk(targetIssueKey, targetIssueId, targetLocalSn) {
      $q.dialog({
        title: 'Confirm',
        message: `Would you like to reopen <b>${targetIssueKey}</b>?`,
        cancel: true,
        persistent: true,
        html: true
      }).onOk(async () => {
        const barRef = axiosExecuteBar.value // for loading bar
        barRef.start() // start load
        const postData = {
          group: props.whichTeam,
          issueKey: targetIssueKey,
          issueId: targetIssueId,
          editor: props.username,
          localDbSn: targetLocalSn
        }
        await axios
          .post(`https://${ServiceDomainLocal}:9487/bpRoutine/jsm/reopen`, postData)
          .then((res) => {
            if (res.data === 'ok') {
              $q.notify({
                message: `Reopen ${targetIssueKey} status successful!`,
                color: 'green-6',
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
              callDefaultHistory()
            } else {
              $q.notify({
                message: `Reopen ${targetIssueKey} status failed - ${res.data}!`,
                color: 'red-6',
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
          })
          .catch((error) => {
            console.log(error)
            $q.notify({
              message: `Reopen ${targetIssueKey} status failed - ${error}!`,
              color: 'red-6',
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
          })
        barRef.stop() // start load
      })
    }

    onMounted(() => {
      if (props.whichTeam === 'NET') {
        localSet.url = `https://${ServiceDomainLocal}:9487/bpCowork/query/netdb/closedTicket`
      } else if (props.whichTeam === 'SYS') {
        localSet.url = `https://${ServiceDomainLocal}:9487/bpCowork/query/sysdb/closedTicket`
      } else if (props.whichTeam === 'DBA') {
        localSet.url = `https://${ServiceDomainLocal}:9487/bpCowork/query/dbadb/closedTicket`
      } else if (props.whichTeam === 'OPS') {
        localSet.url = `https://${ServiceDomainLocal}:9487/bpCowork/query/opsdb/closedTicket`
      }
      callDefaultHistory()

      if (props.username === 'Paul.Chen') {
        localSet.isAdmin = true
        callCommentsHistory('SYS')
      } else if (props.username === 'Major.Chang') {
        localSet.isAdmin = true
        callCommentsHistory('NET')
      } else if (props.username === 'Justin.Yeh') {
        localSet.isAdmin = true
        callCommentsHistory('NET')
      } else if (props.username === 'Albert.Huang') {
        localSet.isAdmin = true
        callCommentsHistory('DBA')
      } else if (props.username === 'Allen.Yu') {
        localSet.isAdmin = true
        callCommentsHistory('OPS')
      }
    })

    watch(
      () => props.startQuery,
      (curKey, oldKey) => {
        if (curKey) {
          console.log('start load')
          callDefaultHistory()
        } else {
          console.log('stop load')
        }
      }
    )

    return {
      localSet,
      columns,
      effColumns,
      pagination: ref({
        rowsPerPage: 10
      }),
      paginationEff: ref({
        rowsPerPage: 100
      }),
      exportTable,
      openNewPageToTicket,
      popuptoAsk,
      axiosExecuteBar
    }
  }
})
</script>
