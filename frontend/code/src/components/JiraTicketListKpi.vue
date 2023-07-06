<!-- @format -->

<template>
  <!-- <JiraTicketListKpi :jiraIssueId="ticketSn" :kpiSn="flagKpiSn" @adjustTicketKpiOnly="kpiUpdate" /> -->
  <!-- Page will use axios to query kpi result by kpiSn, if result equal true, kpiSummary is true, display the summary only, otherwise show the q-select -->
  <div v-if="kpiSummary">
    <span v-if="kpiResult.type === '1'">
      <span>KPI has been assigned as <b>regular operation</b></span
      ><br />
      <span>Handler: {{ kpiResult.handler }}</span>
    </span>
    <span v-if="kpiResult.type === '2'">
      <span>KPI has been assigned as <b>troubleshooting</b></span
      ><br />
      <span>Handler: {{ kpiResult.handler }}</span
      ><br />
      <span>Handler(deputy): {{ kpiResult.handler_second }}</span
      ><br />
      <span>Participant(s): {{ kpiResult.participant }}</span
      ><br />
      <span>Solved?: {{ kpiResult.resolve_status }}</span>
    </span>
    <span v-if="kpiResult.type === '3'">
      <div>KPI has been assigned as <b>advanced troubleshooting</b></div>
      <div>Handler: {{ kpiResult.handler }}</div>
      <div v-if="kpiResult.handler_second">
        Handler(deputy): {{ kpiResult.handler_second }}
      </div>
      <div v-if="kpiResult.participant">Participant(s): {{ kpiResult.participant }}</div>
      <div>
        Description:
        <div v-html="kpiResult.description"></div>
      </div>
      <div>Solved?: {{ kpiResult.resolve_status }}</div>
      <div>
        Post-mortem:
        <img
          @click="
            popupKpiFile(
              kpiResult.related_date,
              kpiResult.related_shift,
              kpiResult.related_sn,
              kpiResult.file_path
            )
          "
          class="rounded-borders cursor-pointer"
          :src="
            'https://' +
            ServiceDomainLocal +
            ':9487/review/kpi/' +
            kpiResult.related_date +
            '/' +
            kpiResult.related_shift +
            '/jira/' +
            kpiResult.related_sn +
            '/' +
            kpiResult.file_path
          "
          style="height: 50px; max-width: 50px"
        />
      </div>
    </span>
    <q-btn class="full-width q-mt-md q-mx-md text-bold" @click="kpiSummary = !kpiSummary"
      >Edit</q-btn
    >
  </div>
  <span v-else>
    <div class="row">
      <q-select
        class="col-12 q-mb-xs"
        outlined
        v-model="kpiResult.type"
        :options="typeOptions"
        emit-value
        map-options
        label="Type *"
        @update:model-value="kpiResultTypeChange(kpiResult.type)"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-crosshairs" @click.stop />
        </template>
      </q-select>
    </div>
    <div v-if="kpiResult.type === '1'" class="row">
      <!-- <div class="col-12 text-center">Detail for regular operation</div> -->
      <!-- emit-value & map-options will let v-model only update / remove by desc -->
      <q-select
        v-model="kpiResult.handler"
        :options="handlerOptions"
        behavior="dialog"
        outlined
        multiple
        use-chips
        stack-label
        emit-value
        map-options
        label="Handler, Choose one at least *"
        class="col-12 q-mb-xs"
        option-value="desc"
        option-label="desc"
        option-disable="inactive"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-users" />
        </template>
      </q-select>
      <span class="col-6 q-pr-xs">
        <q-tooltip
          class="bg-pink-2 text-black"
          anchor="top middle"
          self="bottom middle"
          :delay="100"
          :offset="[10, 10]"
        >
          <span
            >If you want to reset these options, please <b>double click</b> the
            button</span
          >
        </q-tooltip>
        <q-btn
          @dblclick="resetButton"
          class="full-width"
          style="height: 100%"
          label="Reset"
          type="submit"
          color="pink-4"
        />
      </span>
      <q-btn
        @click="updateButton('1')"
        class="col-6"
        label="Confirm"
        type="submit"
        color="pink-4"
        :disable="
          typeof kpiResult.handler === 'undefined' ||
          kpiResult.handler === null ||
          kpiResult.handler.length === 0
        "
      />
    </div>
    <div v-if="kpiResult.type === '2'" class="row">
      <q-select
        v-model="kpiResult.handler"
        :options="handlerOptions"
        behavior="dialog"
        outlined
        emit-value
        map-options
        clearable
        stack-label
        label="Handler, single choice *"
        class="col-12 q-mb-xs"
        option-value="desc"
        option-label="desc"
        option-disable="inactive"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-user" @click.stop />
        </template>
      </q-select>
      <q-select
        v-model="kpiResult.handler_second"
        :options="handlerDeputyOptions"
        behavior="dialog"
        outlined
        multiple
        use-chips
        stack-label
        label="Handler(deputy), optional"
        class="col-12 q-mb-xs"
        emit-value
        map-options
        option-value="desc"
        option-label="desc"
        option-disable="inactive"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-users" @click.stop />
        </template>
      </q-select>
      <q-select
        v-model="kpiResult.participant"
        :options="ParticipantOptions"
        behavior="dialog"
        outlined
        multiple
        use-chips
        stack-label
        label="Participant(s), optional"
        class="col-12 q-mb-xs"
        emit-value
        map-options
        option-value="desc"
        option-label="desc"
        option-disable="inactive"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-users" @click.stop />
        </template>
      </q-select>
      <q-separator spaced inset />
      <div class="col">
        <q-toggle
          v-model="kpiResult.resolve_status"
          unchecked-icon="clear"
          checked-icon="check"
          color="green"
          :label="
            kpiResult.resolve_status
              ? 'Ticket has been solved? YES'
              : 'Ticket has been solved? NO'
          "
        />
      </div>
      <span class="col q-mr-xs">
        <q-tooltip
          class="bg-pink-2 text-black"
          anchor="top middle"
          self="bottom middle"
          :delay="100"
          :offset="[10, 10]"
        >
          <span
            >If you want to reset these options, please <b>double click</b> the
            button</span
          >
        </q-tooltip>
        <q-btn
          @dblclick="resetButton"
          class="full-width"
          style="height: 100%"
          label="Reset"
          type="submit"
          color="pink-4"
        />
      </span>
      <span class="col">
        <q-tooltip
          class="bg-pink-2 text-black"
          anchor="top middle"
          self="bottom middle"
          :delay="100"
          :offset="[10, 10]"
          v-if="typeof kpiResult.handler === 'undefined' || kpiResult.handler === null"
        >
          Miss handler!
        </q-tooltip>
        <q-btn
          @click="updateButton('2')"
          class="full-width"
          style="height: 100%"
          label="Confirm"
          type="submit"
          color="pink-4"
          :disable="
            typeof kpiResult.handler === 'undefined' || kpiResult.handler === null
          "
        />
      </span>
    </div>
    <div v-if="kpiResult.type === '3'" class="row">
      <q-select
        v-model="kpiResult.handler"
        :options="handlerOptions"
        behavior="dialog"
        outlined
        emit-value
        map-options
        clearable
        stack-label
        label="Handler, single choice *"
        class="col-12 q-mb-xs"
        option-value="desc"
        option-label="desc"
        option-disable="inactive"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-user" @click.stop />
        </template>
      </q-select>
      <q-select
        v-model="kpiResult.handler_second"
        :options="handlerDeputyOptions"
        behavior="dialog"
        outlined
        multiple
        use-chips
        stack-label
        label="Handler(deputy), optional"
        class="col-12 q-mb-xs"
        emit-value
        map-options
        option-value="desc"
        option-label="desc"
        option-disable="inactive"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-users" @click.stop />
        </template>
      </q-select>
      <q-select
        v-model="kpiResult.participant"
        :options="ParticipantOptions"
        behavior="dialog"
        outlined
        multiple
        use-chips
        stack-label
        label="Participant(s), optional"
        class="col-12 q-mb-xs"
        emit-value
        map-options
        option-value="desc"
        option-label="desc"
        option-disable="inactive"
      >
        <template v-slot:prepend>
          <q-icon name="fas fa-users" @click.stop />
        </template>
      </q-select>
      <div class="col-6 rounded-borders q-pa-xs text-center">
        <q-icon
          class="q-ma-xs q-pr-sm"
          size="sm"
          color="grey-8"
          name="fas fa-file-import"
        />Post-mortem *
      </div>
      <div class="col-6 rounded-borders q-pa-xs text-center">
        <q-icon
          class="q-ma-xs q-pr-sm"
          size="sm"
          color="grey-8"
          name="fas fa-info-circle"
        />Description
      </div>
      <q-uploader
        :url="'https://' + ServiceDomainLocal + ':9487/update/db/kpi/filePath'"
        color="pink-4"
        flat
        bordered
        class="col-6"
        :headers="[{ name: 'dbSn', value: jiraIssueId }, { name: 'zone', value: 'jira' }]"
        @uploaded="updateKpiAtFile($event)"
        @failed="updateKpiAtFileFailed($event)"
      />
      <q-editor
        class="col-6"
        v-model="kpiResult.description"
        ref="targetRef"
        :toolbar="customEditorToolBar"
      >
        <template v-slot:token>
          <q-btn-dropdown
            dense
            split
            unelevated
            padding="xs"
            fab-mini
            flat
            ref="kpiEditorBtnDropDownColor"
            icon="format_color_text"
            v-bind:text-color="
              foreColor ? ConvertforeColor('fore') : ConvertforeColor('fore')
            "
            @click="adjustFontColor('foreColor', foreColor)"
          >
            <q-list dense>
              <q-item
                tag="label"
                clickable
                @click="adjustFontColor('foreColor', foreColor)"
              >
                <q-item-section>
                  <q-color
                    v-model="foreColor"
                    no-header
                    no-footer
                    default-view="palette"
                    :palette="[
                      '#FFFF00',
                      '#FF0000',
                      '#0000FF',
                      '#008000',
                      '#1D1D1D',
                      '#FFFFFF',
                      '#808080'
                    ]"
                    class="my-picker"
                    square
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </template>
        <template v-slot:token2>
          <q-btn-dropdown
            dense
            split
            unelevated
            padding="xs"
            fab-mini
            flat
            ref="kpiEditorBtnDropDownBGColor"
            icon="font_download"
            v-bind:text-color="
              backColor ? ConvertforeColor('back') : ConvertforeColor('back')
            "
            @click="adjustFontColor('backColor', backColor)"
            push
          >
            <q-list dense>
              <q-item
                tag="label"
                clickable
                @click="adjustFontColor('backColor', backColor)"
              >
                <q-item-section>
                  <q-color
                    v-model="backColor"
                    no-header
                    no-footer
                    default-view="palette"
                    :palette="[
                      '#FFFF00',
                      '#FF0000',
                      '#0000FF',
                      '#008000',
                      '#1D1D1D',
                      '#FFFFFF',
                      '#808080'
                    ]"
                    class="my-picker"
                    square
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </template>
      </q-editor>
      <q-separator class="col-12" spaced inset />
      <div class="col">
        <q-toggle
          v-model="kpiResult.resolve_status"
          unchecked-icon="clear"
          checked-icon="check"
          color="green"
          :label="
            kpiResult.resolve_status
              ? 'Ticket has been solved? YES'
              : 'Ticket has been solved? NO'
          "
        />
      </div>
      <span class="col q-mr-xs">
        <q-tooltip
          class="bg-pink-2 text-black"
          anchor="top middle"
          self="bottom middle"
          :delay="100"
          :offset="[10, 10]"
        >
          <span
            >If you want to reset these options, please <b>double click</b> the
            button</span
          >
        </q-tooltip>
        <q-btn
          @dblclick="resetButton"
          class="full-width"
          style="height: 100%"
          label="Reset"
          type="submit"
          color="pink-4"
        />
      </span>
      <span class="col">
        <q-tooltip
          class="bg-pink-2 text-black"
          anchor="top middle"
          self="bottom middle"
          :delay="100"
          :offset="[10, 10]"
          v-if="
            typeof kpiResult.handler === 'undefined' ||
            kpiResult.handler === null ||
            kpiResult.file_path === null
          "
        >
          <span
            v-if="typeof kpiResult.handler === 'undefined' || kpiResult.handler === null"
            >Miss Handler!<br
          /></span>
          <span v-if="kpiResult.file_path === null">Miss Post-mortem!</span>
        </q-tooltip>
        <q-btn
          @click="updateButton('3')"
          class="full-width"
          style="height: 100%"
          label="Confirm"
          type="submit"
          color="pink-4"
          :disable="
            typeof kpiResult.handler === 'undefined' ||
            kpiResult.handler === null ||
            kpiResult.file_path === null
          "
        />
      </span>
    </div>
  </span>
</template>

<script>
import {
  defineComponent,
  ref,
  reactive,
  onMounted,
  onBeforeUnmount,
  watch,
  getCurrentInstance,
  inject
  // onUpdated
} from 'vue'
import axios from 'axios'
import _ from 'lodash'
import { useQuasar } from 'quasar'
import { useStore } from 'vuex'
// import { defineComponent, ref, reactive, getCurrentInstance, inject, watch } from 'vue'
// import { scroll, useQuasar, dom } from 'quasar'
// import { useQuasar, Cookies } from 'quasar'

export default defineComponent({
  name: 'JiraTicketListKpi',
  props: {
    jiraIssueId: Number,
    kpiSn: Number
  },
  emits: ['adjustTicketKpiOnly'],
  setup(props, context) {
    const $q = useQuasar()
    const $store = useStore()
    const CurShift = inject('CurShift')
    const CurData = inject('CurData')
    const selfTimer = ref(null)
    const kpiResult = reactive({})
    const kpiSummary = ref(false)
    const typeOptions = ref([
      {
        label: 'regular operation',
        value: '1'
      },
      {
        label: 'troubleshooting',
        value: '2'
      },
      {
        label: 'advanced troubleshooting',
        value: '3'
      }
    ])
    const defaultPersonOptions = ref([
      {
        id: 'YT0098',
        desc: 'Aiden',
        inactive: false
      },
      {
        id: 'YT0028',
        desc: 'Albert',
        inactive: false
      },
      {
        id: 'YT0130',
        desc: 'Alex',
        inactive: false
      },
      {
        id: 'YT0082',
        desc: 'Asky',
        inactive: false
      },
      {
        id: 'YT0101',
        desc: 'Bayu',
        inactive: false
      },
      {
        id: 'YT0091',
        desc: 'Bob',
        inactive: false
      },
      {
        id: 'YT0066',
        desc: 'Cadalora',
        inactive: false
      },
      {
        id: 'YT0016',
        desc: 'Cyril',
        inactive: false
      },
      {
        id: 'YT0003',
        desc: 'Daniel',
        inactive: false
      },
      {
        id: 'YT0063',
        desc: 'Danny',
        inactive: false
      },
      {
        id: 'YT0120',
        desc: 'Eric',
        inactive: false
      },
      {
        id: 'YT0060',
        desc: 'Gary',
        inactive: false
      },
      {
        id: 'YT0022',
        desc: 'Huck',
        inactive: false
      },
      {
        id: 'YT0068',
        desc: 'Ivan',
        inactive: false
      },
      {
        id: 'YT0037',
        desc: 'Keven',
        inactive: false
      },
      {
        id: 'YT0069',
        desc: 'Larry',
        inactive: false
      },
      {
        id: 'YT0079',
        desc: 'Thurston',
        inactive: false
      },
      {
        id: 'YT0156',
        desc: 'Rorschach',
        inactive: false
      }
    ])

    const handlerOptions = _.cloneDeep(defaultPersonOptions)
    const handlerDeputyOptions = _.cloneDeep(defaultPersonOptions)
    const ParticipantOptions = _.cloneDeep(defaultPersonOptions)

    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain

    // rich editor
    const customEditorToolBar = ref([
      [
        'bold',
        'italic',
        'strike',
        'underline',
        'subscript',
        'superscript',
        'removeFormat'
      ],
      ['link'],
      ['token'],
      ['token2'],
      ['fullscreen']
    ])
    const foreColor = ref('#000000')
    const backColor = ref('#ffff00')
    const targetRef = ref(null)
    const kpiEditorBtnDropDownColor = ref(null)
    const kpiEditorBtnDropDownBGColor = ref(null)
    const { proxy } = getCurrentInstance()

    function resetButton() {
      // need to delete DB value by axios
      // need to remove object data with default - don't care what the current type
      if (kpiResult.sn) {
        console.log('need to post the data to remove DB data')
        const postData = reactive({
          dataSource: 'Jira',
          targetDate: CurData.value,
          originSourceSn: props.jiraIssueId,
          _type: 'reset'
        })
        axios
          .post(`https://${ServiceDomainLocal}:9487/update/db/kpi/status`, postData)
          .then((res) => {
            console.log(res)
            if (res.status === 200) {
              $q.notify({
                message: '<b>RESET SUCCESS!</b>',
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
            }
          })
          .catch((error) => {
            console.log(error)
          })
      }
      // front data only -
      // reset all options
      Object.assign(handlerOptions, _.cloneDeep(defaultPersonOptions))
      Object.assign(handlerDeputyOptions, _.cloneDeep(defaultPersonOptions))
      Object.assign(ParticipantOptions, _.cloneDeep(defaultPersonOptions))
      // use for to reset reactive object
      for (const [key] of Object.entries(kpiResult)) {
        kpiResult[key] = null
      }
    }

    // KPI confirm button function, parameter is KPI type ( 1, 2, 3 )
    function updateButton(type) {
      if (type === '1') {
        // regular operation
        console.log('regular operation')
        // need to update the kpi by axios post to update the DB
        // - what is the data need to update to DB
        const postData = reactive({
          type: '1',
          handler: kpiResult.handler,
          dataSource: 'Jira',
          originSourceSn: props.jiraIssueId,
          targetDate: CurData.value,
          targetShift: CurShift.value,
          _type: 'update'
        })
        axios
          .post(`https://${ServiceDomainLocal}:9487/update/db/kpi/status`, postData)
          .then((res) => {
            $q.notify({
              message: 'KPI UPDATE <b>SUCCESS</b>!',
              color: 'pink-6',
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
            // updateKpiDataBySn(res.data)
            kpiSummary.value = true
            context.emit('adjustTicketKpiOnly', res.data)
          })
          .catch((error) => {
            console.log(error)
          })
        // need to update and release the disabled button - but can't clear the textarea
      } else if (type === '2') {
        // troubleshooting
        console.log('troubleshooting')
        const postData = reactive({
          type: '2',
          handler: kpiResult.handler,
          handlerSecond: kpiResult.handler_second,
          participant: kpiResult.participant,
          isSolved: kpiResult.resolve_status,
          dataSource: 'Jira',
          originSourceSn: props.jiraIssueId,
          targetDate: CurData.value,
          targetShift: CurShift.value,
          _type: 'update'
        })
        axios
          .post(`https://${ServiceDomainLocal}:9487/update/db/kpi/status`, postData)
          .then((res) => {
            console.log(res)
            $q.notify({
              message: 'KPI UPDATE <b>SUCCESS</b>!',
              color: 'pink-6',
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
            kpiSummary.value = true
            context.emit('adjustTicketKpiOnly')
          })
          .catch((error) => {
            console.log(error)
          })
      } else if (type === '3') {
        // advanced troubleshooting
        console.log('advanced troubleshooting')
        // when user click the button with type 3, need to update the KpiResult ( date / shift / sn ), avoid page can't load the image
        kpiResult.related_sn = props.jiraIssueId
        kpiResult.related_date = CurData.value
        kpiResult.related_shift = CurShift.value
        const postData = reactive({
          type: '3',
          handler: kpiResult.handler,
          handlerSecond: kpiResult.handler_second,
          participant: kpiResult.participant,
          filePath: kpiResult.file_path,
          description: kpiResult.description,
          isSolved: kpiResult.resolve_status,
          dataSource: 'Jira',
          originSourceSn: props.jiraIssueId,
          targetDate: CurData.value,
          targetShift: CurShift.value,
          _type: 'update'
        })
        axios
          .post(`https://${ServiceDomainLocal}:9487/update/db/kpi/status`, postData)
          .then((res) => {
            console.log(res)
            $q.notify({
              message: 'KPI UPDATE <b>SUCCESS</b>!',
              color: 'pink-6',
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
            kpiSummary.value = true
            context.emit('adjustTicketKpiOnly')
          })
          .catch((error) => {
            console.log(error)
          })
      }
    }

    function kpiResultTypeChange(curType) {
      console.log(`kpiResult Type change to ${curType}`)
      // need to reset all option due to type change, to avoid error, single and multiple select issue
      for (const [key] of Object.entries(kpiResult)) {
        kpiResult[key] = ref(null)
      }
      kpiResult.type = ref(curType)
      kpiResult.resolve_status = ref(false)
      kpiResult.description = ref('')
      Object.assign(handlerOptions, _.cloneDeep(defaultPersonOptions))
      Object.assign(handlerDeputyOptions, _.cloneDeep(defaultPersonOptions))
      Object.assign(ParticipantOptions, _.cloneDeep(defaultPersonOptions))
      console.log(kpiResult)
    }

    function ConvertforeColor(target) {
      if (target === 'fore') {
        if (foreColor.value === '#ffff00') {
          return 'yellow-6'
        } else if (foreColor.value === '#ff0000') {
          return 'red-6'
        } else if (foreColor.value === '#0000ff') {
          return 'blue-10'
        } else if (foreColor.value === '#008000') {
          return 'green-8'
        } else if (foreColor.value === '#808080') {
          return 'grey-6'
        } else {
          return 'dark'
        }
      } else {
        if (backColor.value === '#ffff00') {
          return 'yellow-6'
        } else if (backColor.value === '#ff0000') {
          return 'red-6'
        } else if (backColor.value === '#0000ff') {
          return 'blue-10'
        } else if (backColor.value === '#008000') {
          return 'green-8'
        } else if (backColor.value === '#808080') {
          return 'grey-6'
        } else {
          return 'dark'
        }
      }
    }

    function adjustFontColor(cmd, name) {
      proxy.kpiEditorBtnDropDownColor.hide()
      proxy.kpiEditorBtnDropDownBGColor.hide()
      proxy.targetRef.runCmd(cmd, name)
      proxy.targetRef.focus()
    }

    function updateKpiAtFile(event) {
      kpiResult.file_path = event.xhr.responseText
    }

    function updateKpiAtFileFailed(event) {
      console.log(event)
      console.log('failed upload, please try later')
    }

    function updateKpiDataBySn() {
      // console.log(`hit updateKpiDataBySn = ${props.kpiSn}`)
      // only when KpiSn has data, then use the setinterval to get new data
      selfTimer.value = setInterval(async () => {
        if (props.kpiSn) {
          if (kpiSummary.value) {
            await axios
              .get(`https://${ServiceDomainLocal}:9487/kpi/view/${props.kpiSn}`)
              .then((res) => {
                // console.log(`axios query ok - by setinterval: ${props.kpiSn}`)
                kpiResult.sn = res.data.sn
                kpiResult.type = res.data.type
                kpiResult.resolve_status = res.data.resolve_status
                kpiResult.handler = res.data.handler
                kpiResult.handler_second = res.data.handler_second
                kpiResult.participant = res.data.participant
                kpiResult.origin_source = res.data.origin_source
                kpiResult.origin_source_subject = res.data.origin_source_subject
                kpiResult.related_sn = res.data.related_sn
                kpiResult.related_date = res.data.related_date
                kpiResult.related_shift = res.data.related_shift
                kpiResult.related_group = res.data.related_group
                kpiResult.description = res.data.description
                kpiResult.file_path = res.data.file_path
              })
              .catch((error) => {
                console.log(error)
              })
          } else {
            await console.log(`user is editing this KPI - ${props.kpiSn}`)
          }
        }
        // } else {
        //   await console.log(`no value for props.kpiSn - ${props.kpiSn}`)
        // }
      }, 60000)
    }

    function popupKpiFile(date, shift, sn, path) {
      window.open(
        `https://${ServiceDomainLocal}:9487/query/kpi/${date}/${shift}/jira/${sn}/${path}`,
        '_blank'
      )
    }

    onMounted(async () => {
      // setinterval to query last data
      updateKpiDataBySn()
      if (props.kpiSn) {
        // first time to query
        const res = await axios.get(`https://${ServiceDomainLocal}:9487/kpi/view/${props.kpiSn}`)
        console.log(`KPI record - ${res.data.origin_source_subject}`)
        kpiResult.sn = res.data.sn
        kpiResult.type = res.data.type
        kpiResult.resolve_status = res.data.resolve_status
        kpiResult.handler = res.data.handler
        kpiResult.handler_second = res.data.handler_second
        kpiResult.participant = res.data.participant
        kpiResult.origin_source = res.data.origin_source
        kpiResult.origin_source_subject = res.data.origin_source_subject
        kpiResult.related_sn = res.data.related_sn
        kpiResult.related_date = res.data.related_date
        kpiResult.related_shift = res.data.related_shift
        kpiResult.related_group = res.data.related_group
        kpiResult.description = res.data.description
        kpiResult.file_path = res.data.file_path
        kpiSummary.value = true
      } else {
        // this ticket don't have kpi log
        kpiResult.resolve_status = ref(false)
        kpiResult.description = ref('')
        kpiResult.file_path = ref(null)
      }
    })

    // need to this one to remove the old setinterval id
    onBeforeUnmount(() => {
      clearInterval(selfTimer.value)
    })

    // A user create KPI record, B user will use this watch to update the JiraTicketListKPI zone data
    watch(
      () => props.kpiSn,
      (curValue, oldValue) => {
        // console.log('jiraTicketListKpi watch props.kpiSn')
        // console.log(`curValue = ${curValue}, oldValue = ${oldValue}`)
        if (curValue !== null) {
          axios
            .get(`https://${ServiceDomainLocal}:9487/kpi/view/${curValue}`)
            .then((res) => {
              // console.log(res)
              kpiResult.sn = res.data.sn
              kpiResult.type = res.data.type
              kpiResult.resolve_status = res.data.resolve_status
              kpiResult.handler = res.data.handler
              kpiResult.handler_second = res.data.handler_second
              kpiResult.participant = res.data.participant
              kpiResult.origin_source = res.data.origin_source
              kpiResult.origin_source_subject = res.data.origin_source_subject
              kpiResult.related_sn = res.data.related_sn
              kpiResult.related_date = res.data.related_date
              kpiResult.related_shift = res.data.related_shift
              kpiResult.related_group = res.data.related_group
              kpiResult.description = res.data.description
              kpiResult.file_path = res.data.file_path
              kpiSummary.value = true
            })
            .catch((error) => {
              console.log(error)
            })
        }
      }
    )

    watch(
      () => kpiResult.handler,
      (curKey, oldKey) => {
        if (!curKey && !oldKey) {
          // console.log('hit both key are null in handler')
        } else if (curKey && !oldKey) {
          // handler column first time add user, but only T or AT need to adjust options
          if (kpiResult.type === '3' || kpiResult.type === '2') {
            handlerDeputyOptions.value.forEach(function (ele2, index2, object2) {
              if (curKey === ele2.desc) {
                object2[index2].inactive = true
              }
            })
            ParticipantOptions.value.forEach(function (ele3, index3, object3) {
              if (curKey === ele3.desc) {
                object3[index3].inactive = true
              }
            })
          }
        } else if (!curKey && oldKey) {
          // last user has been removed from handler, only T or AT need to adjust options
          if (kpiResult.type === '3' || kpiResult.type === '2') {
            handlerDeputyOptions.value.forEach(function (ele2, index2, object2) {
              if (oldKey === ele2.desc) {
                object2[index2].inactive = false
              }
            })
            ParticipantOptions.value.forEach(function (ele3, index3, object3) {
              if (oldKey === ele3.desc) {
                object3[index3].inactive = false
              }
            })
          }
        } else if (kpiResult.type === '2' || kpiResult.type === '3') {
          // only when single select has been changed
          handlerDeputyOptions.value.forEach(function (ele2, index2, object2) {
            if (oldKey === ele2.desc) {
              object2[index2].inactive = false
            }
            if (curKey === ele2.desc) {
              object2[index2].inactive = true
            }
          })
          ParticipantOptions.value.forEach(function (ele3, index3, object3) {
            if (oldKey === ele3.desc) {
              object3[index3].inactive = false
            }
            if (curKey === ele3.desc) {
              object3[index3].inactive = true
            }
          })
        }
      }
    )

    watch(
      () => kpiResult.handler_second,
      (curKey, oldKey) => {
        // console.log('watch kpiResult.handler_second')
        if (!curKey && !oldKey) {
          // console.log('hit both key are null - handler_second')
        } else if (curKey && !oldKey) {
          // first time
          // handlerSecond are optionals, hence the value will store by array (list)
          // avoid the data is query from DB, so need to use the forEach to set the inactive value for these users have been selected.
          curKey.forEach(function (ele, index, object) {
            handlerOptions.value.forEach(function (ele2, index2, object2) {
              if (ele === ele2.desc) {
                object2[index2].inactive = true
              }
            })
            ParticipantOptions.value.forEach(function (ele3, index3, object3) {
              if (ele === ele3.desc) {
                object3[index3].inactive = true
              }
            })
          })
        } else if (!curKey && oldKey) {
          // remove last selected from handlerSecond
          handlerOptions.value.forEach(function (ele2, index2, object2) {
            if (oldKey === ele2.desc) {
              object2[index2].inactive = true
            }
          })
          ParticipantOptions.value.forEach(function (ele3, index3, object3) {
            if (oldKey === ele3.desc) {
              object3[index3].inactive = true
            }
          })
        } else if (curKey.length > oldKey.length) {
          // Add - handler_second
          const addNewItem = curKey.filter((item) => {
            return !oldKey.includes(item)
          })

          handlerOptions.value.forEach(function (ele2, index2, object2) {
            if (addNewItem[0] === ele2.desc) {
              object2[index2].inactive = true
            }
          })

          ParticipantOptions.value.forEach(function (ele3, index3, object3) {
            if (addNewItem[0] === ele3.desc) {
              object3[index3].inactive = true
            }
          })
        } else if (curKey.length < oldKey.length) {
          // Remove - handler_second
          const removeItem = oldKey.filter((item) => {
            return !curKey.includes(item)
          })

          handlerOptions.value.forEach(function (ele2, index2, object2) {
            if (removeItem[0] === ele2.desc) {
              object2[index2].inactive = false
            }
          })

          ParticipantOptions.value.forEach(function (ele3, index3, object3) {
            if (removeItem[0] === ele3.desc) {
              object3[index3].inactive = false
            }
          })
        }
      }
    )

    watch(
      () => kpiResult.participant,
      (curKey, oldKey) => {
        // console.log('watch kpiResult.participant')
        if (!curKey && !oldKey) {
          // console.log('hit both key are null - participant')
        } else if (curKey && !oldKey) {
          // first time - participants
          curKey.forEach(function (ele, index, object) {
            handlerOptions.value.forEach(function (ele2, index2, object2) {
              if (ele === ele2.desc) {
                object2[index2].inactive = true
              }
            })
            handlerDeputyOptions.value.forEach(function (ele3, index3, object3) {
              if (ele === ele3.desc) {
                object3[index3].inactive = true
              }
            })
          })
        } else if (!curKey && oldKey) {
          // remove last selected - participant
          handlerOptions.value.forEach(function (ele2, index2, object2) {
            if (oldKey === ele2.desc) {
              object2[index2].inactive = true
            }
          })
          handlerDeputyOptions.value.forEach(function (ele3, index3, object3) {
            if (oldKey === ele3.desc) {
              object3[index3].inactive = true
            }
          })
        } else if (curKey.length > oldKey.length) {
          // Add - participant
          const addNewItem = curKey.filter((item) => {
            return !oldKey.includes(item)
          })

          handlerOptions.value.forEach(function (ele2, index2, object2) {
            if (addNewItem[0] === ele2.desc) {
              object2[index2].inactive = true
            }
          })

          handlerDeputyOptions.value.forEach(function (ele3, index3, object3) {
            if (addNewItem[0] === ele3.desc) {
              object3[index3].inactive = true
            }
          })
        } else if (curKey.length < oldKey.length) {
          // Remove - participant
          const removeItem = oldKey.filter((item) => {
            return !curKey.includes(item)
          })

          handlerOptions.value.forEach(function (ele2, index2, object2) {
            if (removeItem[0] === ele2.desc) {
              object2[index2].inactive = false
            }
          })

          handlerDeputyOptions.value.forEach(function (ele3, index3, object3) {
            if (removeItem[0] === ele3.desc) {
              object3[index3].inactive = false
            }
          })
        }
      }
    )

    return {
      kpiResult,
      typeOptions,
      handlerOptions,
      handlerDeputyOptions,
      ParticipantOptions,
      resetButton,
      updateButton,
      kpiResultTypeChange,
      customEditorToolBar,
      foreColor,
      backColor,
      targetRef,
      kpiEditorBtnDropDownColor,
      kpiEditorBtnDropDownBGColor,
      ConvertforeColor,
      adjustFontColor,
      proxy,
      updateKpiAtFile,
      updateKpiAtFileFailed,
      kpiSummary,
      updateKpiDataBySn,
      selfTimer,
      popupKpiFile,
      ServiceDomainLocal
    }
  }
})
</script>
