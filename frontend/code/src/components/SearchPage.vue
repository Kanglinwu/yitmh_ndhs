<!-- @format -->

<template>
  <q-page class="q-pa-xl bg-red-1 q-gutter-xs column">
    <q-dialog class="bg-teal-1" v-model="isShowTraceLog" full-width>
      <DHSNoteListLog
        v-if="targetSource === 'NOTE'"
        :key="showLogKey"
        :title="showLogTarget"
        source="fromSearch"
      ></DHSNoteListLog>
      <DHSOTRSListLog
        v-if="targetSource === 'OTRS'"
        :key="showLogKey"
        :ticketNumber="showLogTarget"
        source="fromSearch"
      ></DHSOTRSListLog>
    </q-dialog>
    <div class="q-gutter-sm">
      <q-radio
        v-model="targetSource"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="NOTE"
        label="NOTE"
      />
      <q-radio
        v-model="targetSource"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="OTRS"
        label="OTRS"
      />
    </div>
    <q-input filled v-model="curKeyWord" type="search" hint="Search">
      <template v-slot:append>
        <q-icon name="search" />
      </template>
    </q-input>
    <div class="row justify-center" v-show="buffer">
      <q-circular-progress
        indeterminate
        size="90px"
        :thickness="0.2"
        color="lime"
        center-color="grey-8"
        track-color="transparent"
        class="q-ma-md"
      />
    </div>
    <q-table grid :rows="rows" :columns="columns" row-key="name" v-if="buffer === false">
      <template v-slot:top>
        <span class="col-6"
          >Total search result counters: {{ searchResultCount }}<br />
          You are reading
          <input
            :disabled="curKeyWord.length === 0"
            @focus="fakeDisplayNone = true"
            @blur="fakeDisplayNone = false"
            v-model.lazy.number="searchStep"
          />
          to {{ searchStep + 4 }}</span
        >
        <span class="col-6 text-right q-gutter-xs">
          <q-btn
            :class="{ hidden: fakeDisplayNone === true }"
            size="lg"
            @click="backToPreviousGroup"
            push
            color="white"
            text-color="yellow"
            round
            icon="fas fa-backward"
            :disable="searchResultCount === 0 || searchStep === 0 || buffer"
          />
          <q-btn
            :class="{ hidden: fakeDisplayNone === true }"
            size="lg"
            @click="callNextGroup"
            push
            color="white"
            text-color="red"
            round
            icon="fas fa-forward"
            :disable="searchResultCount === 0 || buffer"
          />
        </span>
      </template>
      <template v-slot:bottom>
        <span class="col-6"
          >Current keyword: <b>{{ curKeyWord }}</b
          ><br />
          <li>Not case sensitive</li>
          <li>Ignore spaces</li></span
        >
        <span class="col-6 text-right q-gutter-xs">
          <q-btn
            :class="{ hidden: fakeDisplayNone === true }"
            size="lg"
            @click="backToPreviousGroup"
            push
            color="white"
            text-color="yellow"
            round
            icon="fas fa-backward"
            :disable="searchResultCount === 0 || searchStep === 0 || buffer"
          />
          <q-btn
            :class="{ hidden: fakeDisplayNone === true }"
            size="lg"
            @click="callNextGroup"
            push
            color="white"
            text-color="red"
            round
            icon="fas fa-forward"
            :disable="searchResultCount === 0 || buffer"
          />
        </span>
      </template>
      <template v-slot:item="props">
        <div class="q-pa-xs col-xs-3 col-sm-3 col-md-3 col-lg-3 grid-style-transition">
          <q-card>
            <q-card-section>
              <section class="row">
                <div class="col-6">
                  <span v-if="targetSource === 'NOTE'" class="text-subtitle1 text-bold">{{
                    props.row.subject
                  }}</span>
                  <span
                    v-else-if="targetSource === 'OTRS'"
                    class="text-subtitle1 text-bold cursor-pointer text-blue-14"
                    @click="otrsOpenToNewPage(props.row.sourceSn)"
                    >{{ props.row.subject }}</span
                  >
                </div>
                <div class="col-6 text-right">
                  <q-chip
                    v-if="targetSource === 'NOTE'"
                    @click="showLogByComponent(props.row.subject)"
                    square
                    text-color="white"
                    color="blue"
                    :label="`${props.row.date}/${props.row.shift}/${props.row.source}`"
                    clickable
                  ></q-chip>
                  <q-chip
                    v-if="targetSource === 'OTRS'"
                    @click="showLogByComponent(props.row.sourceSn)"
                    square
                    text-color="white"
                    color="blue"
                    :label="`${props.row.date}/${props.row.shift}/${props.row.source}`"
                    clickable
                  ></q-chip>
                </div>
              </section>
            </q-card-section>
            <q-card-section>
              <div class="custWordBreak" v-html="props.row.content"></div>
            </q-card-section>
            <q-card-section
              v-if="
                props.row.updateContent !== false && props.row.updateContent !== 'New'
              "
            >
              <div class="custWordBreak" v-html="props.row.updateContent"></div>
            </q-card-section>
          </q-card>
        </div>
      </template>
    </q-table>
  </q-page>
</template>

<script>
import { defineComponent, inject, ref, reactive, watch } from 'vue'
import axios from 'axios'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
// components
import DHSNoteListLog from 'components/DHSNoteListLog.vue'
import DHSOTRSListLog from 'components/DHSOTRSListLog.vue'
export default defineComponent({
  name: 'SearchPage',
  components: {
    DHSNoteListLog,
    DHSOTRSListLog
  },
  setup() {
    const $q = useQuasar()
    const isLogin = inject('isLogin')
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const targetSource = ref('NOTE')
    const curKeyWord = ref('')
    const searchStep = ref(0)
    const searchResultCount = ref(0)
    const buffer = ref(false)
    const fakeDisplayNone = ref(false)
    const isShowTraceLog = ref(false)
    const showLogTarget = ref('')
    const showLogKey = ref(0)
    const columns = [
      {
        name: 'date',
        align: 'left',
        label: 'Date (YYYY/MM/DD)',
        field: 'date',
        sortable: true
      },
      {
        name: 'shift',
        align: 'left',
        label: 'Shift (M/A/N)',
        field: 'shift'
      },
      {
        name: 'subject',
        align: 'left',
        label: 'Subject',
        field: 'subject'
      },
      {
        name: 'content',
        align: 'left',
        label: 'Content',
        field: 'content'
      },
      {
        name: 'updateContent',
        align: 'left',
        label: 'Update Content',
        field: 'updateContent'
      },
      {
        name: 'source',
        align: 'left',
        label: 'Source',
        field: 'source'
      }
    ]

    const rows = ref([])

    function showLogByComponent(targetTitle) {
      console.log(`hit showLogByComponent - target is ${targetTitle}`)
      showLogTarget.value = targetTitle
      isShowTraceLog.value = true
      showLogKey.value += 1
    }

    function callNextGroup() {
      if (searchStep.value < searchResultCount.value - 4) {
        buffer.value = true
        searchStep.value += 4
        updateTheTable(curKeyWord.value, searchStep.value)
      } else {
        $q.notify({
          message: 'At the end of results',
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
    }

    function backToPreviousGroup() {
      if (searchStep.value >= 4) {
        searchStep.value -= 4
      } else {
        // step = 0 ~ 5, only need to assign to 0
        searchStep.value = 0
      }
      buffer.value = true
      updateTheTable(curKeyWord.value, searchStep.value)
    }

    function resetAll() {
      rows.value = []
      searchResultCount.value = 0
      searchStep.value = 0
    }

    function otrsOpenToNewPage(ticketNumber) {
      const targetId = ref(0)
      if (ticketNumber >= 92027180) {
        targetId.value = ticketNumber - 92000009
      } else if (ticketNumber >= 92022525) {
        targetId.value = ticketNumber - 91999956
      } else {
        targetId.value = ticketNumber - 91999952
      }
      window.open(
        `http://172.23.1.44/otrs/index.pl?Action=AgentTicketZoom;TicketID=${targetId.value}`,
        '_blank'
      )
    }

    async function updateTheTable(targetKeyWord, step) {
      if (targetKeyWord === 'notNeedToCallBackEnd') {
        console.log('hit notNeedToCallBackEnd')
        resetAll()
      } else {
        const postData = reactive({
          keyword: targetKeyWord,
          curOffset: step,
          targetSource: targetSource.value,
          firstTime: searchResultCount.value
        })
        await axios
          .post(`https://${ServiceDomainLocal}:9487/searchPage/query`, postData)
          .then((res) => {
            console.log(res)
            // due to backend return keyword is no space, so need to trim() to remove space to match the result
            if (curKeyWord.value.trim() === res.data[2]) {
              buffer.value = false
              rows.value = res.data[0]
              searchStep.value = step
              searchResultCount.value = res.data[1]
              if (res.data[1] === 0) {
                $q.notify({
                  message: `No result has been found (Keyword: ${res.data[2]}) on ${targetSource.value}`,
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
            }
          })
          .catch((error) => {
            console.log(error)
          })
      }
    }

    watch(
      () => curKeyWord.value,
      (curValue) => {
        if (curValue) {
          buffer.value = true
          searchStep.value = 0
          searchResultCount.value = 0
          updateTheTable(curValue, searchStep.value)
        } else {
          updateTheTable('notNeedToCallBackEnd')
        }
      }
    )

    watch(
      () => targetSource.value,
      (curOption) => {
        if (curKeyWord.value) {
          buffer.value = true
          searchStep.value = 0
          searchResultCount.value = 0
          updateTheTable(curKeyWord.value, searchStep.value)
        } else {
          resetAll()
        }
      }
    )

    watch(
      () => searchStep.value,
      (curStep) => {
        if (searchResultCount.value !== 0) {
          const newStep = curStep | 0
          buffer.value = true
          updateTheTable(curKeyWord.value, newStep)
        }
      }
    )

    return {
      isLogin,
      curKeyWord,
      columns,
      rows,
      searchResultCount,
      searchStep,
      callNextGroup,
      backToPreviousGroup,
      buffer,
      fakeDisplayNone,
      targetSource,
      isShowTraceLog,
      showLogByComponent,
      showLogTarget,
      showLogKey,
      otrsOpenToNewPage
    }
  }
})
</script>
