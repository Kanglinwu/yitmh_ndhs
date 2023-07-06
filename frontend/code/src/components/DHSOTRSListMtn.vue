<!-- @format -->

<template>
  <q-stepper v-model="mtnObject.mtnStep" ref="stepper" color="primary" animated>
    <q-step
      :name="1"
      title="Maintenance type"
      icon="settings"
      :done="mtnObject.mtnStep > 1"
    >
      <q-option-group :options="mtnOptions" type="radio" v-model="mtnGroup" />
    </q-step>

    <q-step
      :name="2"
      title="Template generate"
      icon="assignment"
      :done="mtnObject.mtnStep > 2"
    >
      <q-card v-if="mtnGroup === 'ndd'" flat bordered>
        <q-item>
          <q-item-section class="text-h6">
            <span>No downtime deployment</span>
          </q-item-section>
        </q-item>
        <q-separator />
        <q-card-section horizontal>
          <q-card-section class="col">
            <q-input
              standout="bg-blue-3 text-bold text-dark"
              v-model="mtnObject.mtnBu"
              label="BU"
            />
            <q-input
              standout="bg-blue-3 text-bold text-dark"
              v-model="mtnObject.mtnModule"
              label="Impacted module"
            />
            <q-input
              label="Start time"
              filled
              v-model="mtnObject.mtnStartTime"
              standout="bg-blue-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-blue-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnStartTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnStartTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input
              label="End time"
              filled
              v-model="mtnObject.mtnEndTime"
              standout="bg-blue-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-blue-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnEndTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnEndTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </q-card-section>

          <q-separator vertical />
          <q-card-section class="col">
            <div class="column justify-between" style="height: 100%">
              <div>No downtime deployment</div>
              <div>
                BU: <span>{{ mtnObject.mtnBu }}</span>
              </div>
              <div>
                Impacted module: <span>{{ mtnObject.mtnModule }}</span>
              </div>
              <div>
                Date: <span>{{ mtnObject.mtnDate }}</span>
              </div>
              <div>
                Start time: <span>{{ mtnObject.mtnStartTime }}</span>
              </div>
              <div>
                End time: <span>{{ mtnObject.mtnEndTime }}</span>
              </div>
              <div>
                Duration: <span>{{ mtnObject.mtnDuration }}</span>
              </div>
              <q-btn
                color="blue-3"
                text-color="black"
                label="Update to summary"
                @click="updateSummaryButton"
                class="q-mb-xs"
              />
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
      <q-card v-if="mtnGroup === 'dd'" flat bordered>
        <q-item>
          <q-item-section class="text-h6">
            <span>Downtime deployment</span>
          </q-item-section>
        </q-item>
        <q-separator />
        <q-card-section horizontal>
          <q-card-section class="col">
            <q-input
              standout="bg-red-3 text-bold text-dark"
              v-model="mtnObject.mtnBu"
              label="BU"
            />
            <q-input
              standout="bg-red-3 text-bold text-dark"
              v-model="mtnObject.mtnModule"
              label="Impacted module"
            />
            <q-input
              label="Start time"
              filled
              v-model="mtnObject.mtnStartTime"
              standout="bg-red-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-red-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnStartTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnStartTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input
              label="End time"
              filled
              v-model="mtnObject.mtnEndTime"
              standout="bg-red-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-red-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnEndTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnEndTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </q-card-section>

          <q-separator vertical />
          <q-card-section class="col">
            <div class="column justify-between" style="height: 100%">
              <div>Downtime deployment</div>
              <div>
                BU: <span>{{ mtnObject.mtnBu }}</span>
              </div>
              <div>
                Impacted module: <span>{{ mtnObject.mtnModule }}</span>
              </div>
              <div>
                Date: <span>{{ mtnObject.mtnDate }}</span>
              </div>
              <div>
                Start time: <span>{{ mtnObject.mtnStartTime }}</span>
              </div>
              <div>
                End time: <span>{{ mtnObject.mtnEndTime }}</span>
              </div>
              <div>
                Duration: <span>{{ mtnObject.mtnDuration }}</span>
              </div>
              <q-btn
                color="red-3"
                text-color="black"
                label="Update to summary"
                @click="updateSummaryButton"
                class="q-mb-xs"
              />
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
      <q-card v-if="mtnGroup === 'cm'" flat bordered>
        <q-item>
          <q-item-section class="text-h6">
            <span>Circuit maintenance</span>
          </q-item-section>
        </q-item>
        <q-separator />
        <q-card-section horizontal>
          <q-card-section class="col">
            <q-input
              standout="bg-green-3 text-bold text-dark"
              v-model="mtnObject.mtnVendor"
              label="Vendor"
            />
            <q-input
              standout="bg-green-3 text-bold text-dark"
              v-model="mtnObject.mtnCircuit"
              label="Circuit ID"
            />
            <q-input
              standout="bg-green-3 text-bold text-dark"
              v-model="mtnObject.mtnEnvironment"
              label="Environment"
            />
            <q-input
              standout="bg-green-3 text-bold text-dark"
              v-model="mtnObject.mtnAffectedCustomer"
              label="Affected customer"
            />
            <q-input
              label="Start time"
              filled
              v-model="mtnObject.mtnStartTime"
              standout="bg-green-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-green-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnStartTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnStartTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input
              label="End time"
              filled
              v-model="mtnObject.mtnEndTime"
              standout="bg-green-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-green-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnEndTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnEndTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
          </q-card-section>

          <q-separator vertical />
          <q-card-section class="col">
            <div class="column justify-between" style="height: 100%">
              <div>Circuit maintenance</div>
              <div>
                Vendor: <span>{{ mtnObject.mtnVendor }}</span>
              </div>
              <div>
                Circuit ID: <span>{{ mtnObject.mtnCircuit }}</span>
              </div>
              <div>
                Environment: <span>{{ mtnObject.mtnEnvironment }}</span>
              </div>
              <div>
                Affected customer: <span>{{ mtnObject.mtnAffectedCustomer }}</span>
              </div>
              <div>
                Start time: <span>{{ mtnObject.mtnStartTime }}</span>
              </div>
              <div>
                End time: <span>{{ mtnObject.mtnEndTime }}</span>
              </div>
              <div>
                Duration: <span>{{ mtnObject.mtnDuration }}</span>
              </div>
              <q-btn
                color="green-3"
                text-color="black"
                label="Update to summary"
                @click="updateSummaryButton"
                class="q-mb-xs"
              />
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
      <q-card v-if="mtnGroup === 'other'" flat bordered>
        <q-item>
          <q-item-section class="text-h6">
            <span>Other</span>
          </q-item-section>
        </q-item>
        <q-separator />
        <q-card-section horizontal>
          <q-card-section class="col">
            <q-input
              standout="bg-yellow-3 text-bold text-dark"
              v-model="mtnObject.mtnOtherName"
              label="Maintenance Name"
            />
            <q-input
              label="Start time"
              filled
              v-model="mtnObject.mtnStartTime"
              standout="bg-yellow-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-yellow-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnStartTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnStartTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input
              label="End time"
              filled
              v-model="mtnObject.mtnEndTime"
              standout="bg-yellow-3 text-bold text-dark"
            >
              <template v-slot:append>
                <q-icon name="access_time" class="cursor-pointer">
                  <q-popup-proxy
                    class="row q-pa-xs bg-yellow-3"
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date
                      class="q-pa-xs"
                      v-model="mtnObject.mtnEndTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-date>
                    <q-time
                      v-model="mtnObject.mtnEndTime"
                      class="q-pa-xs"
                      mask="YYYY-MM-DD HH:mm"
                      format24h
                    >
                      <div class="row items-center justify-end">
                        <q-btn v-close-popup label="Close" color="primary" flat />
                      </div>
                    </q-time>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input>
            <q-input
              standout="bg-yellow-3 text-bold text-dark"
              v-model="mtnObject.mtnOtherRiskAnalysis"
              label="Risk analysis"
            />
          </q-card-section>

          <q-separator vertical />
          <q-card-section class="col">
            <div class="column justify-between" style="height: 100%">
              <div>
                Maintenance Name: <span>{{ mtnObject.mtnOtherName }}</span>
              </div>
              <div>
                Start time: <span>{{ mtnObject.mtnStartTime }}</span>
              </div>
              <div>
                End time: <span>{{ mtnObject.mtnEndTime }}</span>
              </div>
              <div>
                Duration: <span>{{ mtnObject.mtnDuration }}</span>
              </div>
              <div>
                Risk analysis: <span>{{ mtnObject.mtnOtherRiskAnalysis }}</span>
              </div>
              <q-btn
                color="yellow-3"
                text-color="black"
                label="Update to summary"
                @click="updateSummaryButton"
                class="q-mb-xs"
              />
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
    </q-step>

    <q-step
      :name="3"
      title="Sync to Google Calendar"
      icon="fas fa-calendar-day"
      :done="mtnObject.mtnStep > 3"
    >
      <div class="text-h6">
        Click "Continue" button to update following information to Google Calender
      </div>
      <div class="row">
        <li><span class="text-bold">Calendar Subject: </span></li>
      </div>
      <div class="row">
        <span class="q-ml-md">YTS{{ ticketJiraIssueId }} - {{ ticketSubject }}</span>
      </div>
      <div class="row">
        <li><span class="text-bold">Details: </span></li>
      </div>
      <div class="row"><span class="q-ml-md" v-html="lastSummary"></span></div>
    </q-step>

    <q-step :name="4" title="Created" icon="fas fa-calendar-check">
      Maintenace schedule has been created, detail please refer following link:
      <a :href="googleSet.link" target="__blank">Maintenace schedule</a><br />
      Schedule id: {{ googleSet.id }}
    </q-step>

    <template v-slot:navigation>
      <q-stepper-navigation>
        <span>
          <q-tooltip
            class="text-white"
            anchor="top middle"
            self="bottom middle"
            :delay="100"
            :offset="[10, 10]"
            v-if="defineNextButtonStatus"
          >
            {{ reminderString }}
          </q-tooltip>
          <q-btn
            v-if="mtnObject.mtnStep === 3"
            @click="syncGoogleCalendar"
            color="primary"
            label="Continue"
          />
          <q-btn
            v-else
            @click="stepperController"
            color="primary"
            :label="mtnObject.mtnStep === 4 ? 'Delete' : 'Continue'"
            :disable="defineNextButtonStatus"
          />
        </span>
        <q-btn
          v-if="mtnObject.mtnStep > 1 && mtnObject.mtnStep !== 4"
          flat
          color="primary"
          @click="$refs.stepper.previous()"
          label="Back"
          class="q-ml-sm"
        />
      </q-stepper-navigation>
    </template>
  </q-stepper>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted, watch } from 'vue'
import { date, useQuasar } from 'quasar'
import { useStore } from 'vuex'
import axios from 'axios'
export default defineComponent({
  name: 'JiraTicketListMtn',
  props: {
    ticketSubject: String,
    ticketNumber: Number,
    lastSummary: String,
    ticketJiraIssueId: Number,
    parentMtnFlagStatus: Boolean
  },
  emits: ['updateSummaryByMtn'],
  setup(props, context) {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    const mtnGroup = ref('')
    const mtnOptions = reactive([
      { label: 'No downtime deployment', value: 'ndd', color: 'blue' },
      { label: 'Downtime deployment', value: 'dd', color: 'red' },
      { label: 'Circuit maintenance', value: 'cm', color: 'green' },
      { label: 'Others', value: 'other', color: 'yellow' }
    ])
    const googleSet = reactive({
      link: ref(''),
      id: ref(''),
      dbSn: ref()
    })
    const mtnObject = reactive({
      mtnStep: ref(1),
      mtnBu: ref(''),
      mtnModule: ref(''),
      mtnDate: computed(() => {
        const re = /\d+-\d+-\d+/
        return re.exec(mtnObject.mtnStartTime)
      }),
      mtnStartTime: ref(''),
      mtnEndTime: ref(''),
      mtnDuration: computed(() => {
        if (date.isValid(mtnObject.mtnStartTime) && date.isValid(mtnObject.mtnEndTime)) {
          const startTimeObject = new Date(mtnObject.mtnStartTime)
          const endTimeObject = new Date(mtnObject.mtnEndTime)
          const diff = date.getDateDiff(endTimeObject, startTimeObject, 'minutes')
          if (diff > 0) {
            return `${diff} minutes`
          } else {
            return null
          }
        } else {
          return null
        }
      }),
      mtnVendor: ref(''),
      mtnCircuit: ref(''),
      mtnEnvironment: ref(''),
      mtnAffectedCustomer: ref(''),
      mtnOtherName: ref(''),
      mtnOtherRiskAnalysis: ref('')
    })

    // use this to return what is miss cause button disabled
    const reminderString = computed(() => {
      if (mtnObject.mtnStep === 1) {
        return 'Miss Maintenance Type!'
      } else if (mtnObject.mtnStep === 2) {
        if (mtnGroup.value === 'cm') {
          const timeStatus = mtnObject.mtnDuration ? 'OK' : 'Miss'
          const VendorStatus = mtnObject.mtnVendor === '' ? 'Miss' : 'OK'
          const CircuitStatus = mtnObject.mtnCircuit === '' ? 'Miss' : 'OK'
          const EnvironmentStatus = mtnObject.mtnEnvironment === '' ? 'Miss' : 'OK'
          const AffectedCustomer = mtnObject.mtnAffectedCustomer === '' ? 'Miss' : 'OK'
          const UpdateSummary =
            confirmedUpdateSummaryButtonStatus.value === true ? 'OK' : 'Miss'
          return `time: ${timeStatus}, Vendor: ${VendorStatus}, Circuit: ${CircuitStatus}, Environment: ${EnvironmentStatus}, AffectedCustomer: ${AffectedCustomer},  UpdateButton: ${UpdateSummary}`
        } else if (mtnGroup.value === 'other') {
          const timeStatus = mtnObject.mtnDuration ? 'OK' : 'Miss'
          const descriptionName = mtnObject.mtnOtherName === '' ? 'Miss' : 'OK'
          const descriptionRiskAnalysis =
            mtnObject.mtnOtherRiskAnalysis === '' ? 'Miss' : 'OK'
          const UpdateSummary =
            confirmedUpdateSummaryButtonStatus.value === true ? 'OK' : 'Miss'
          return `time: ${timeStatus}, Name: ${descriptionName}, RiskAnalysis: ${descriptionRiskAnalysis}, UpdateButton: ${UpdateSummary}`
        } else {
          const timeStatus = mtnObject.mtnDuration ? 'OK' : 'Miss'
          const BuStatus = mtnObject.mtnBu === '' ? 'Miss' : 'OK'
          const ModuleStatus = mtnObject.mtnModule === '' ? 'Miss' : 'OK'
          const UpdateSummary =
            confirmedUpdateSummaryButtonStatus.value === true ? 'OK' : 'Miss'
          return `time: ${timeStatus}, Bu: ${BuStatus}, Module: ${ModuleStatus}, UpdateButton: ${UpdateSummary}`
        }
      } else if (mtnObject.mtnStep === 3) {
        return 'Update to Google Calendar'
      } else {
        return '4 later'
      }
    })

    // when mtn step2, user click the upload summary button, will change status to true.
    const confirmedUpdateSummaryButtonStatus = ref(false)

    // const defineSyncButton = ref(true)
    const defineNextButtonStatus = computed(() => {
      // step1, check if checkbox selected already
      if (mtnObject.mtnStep === 1) {
        return mtnGroup.value === ''
      } else if (mtnObject.mtnStep === 2) {
        if (mtnGroup.value === 'cm') {
          if (
            mtnObject.mtnDuration !== null &&
            mtnObject.mtnVendor !== '' &&
            mtnObject.mtnCircuit !== '' &&
            mtnObject.mtnEnvironment !== '' &&
            mtnObject.mtnAffectedCustomer !== '' &&
            confirmedUpdateSummaryButtonStatus.value
          ) {
            return false
          } else {
            return true
          }
        } else if (mtnGroup.value === 'other') {
          if (
            mtnOptions.mtnOtherName !== '' &&
            mtnOptions.mtnOtherRiskAnalysis !== '' &&
            mtnObject.mtnDuration !== null &&
            confirmedUpdateSummaryButtonStatus.value
          ) {
            return false
          } else {
            return true
          }
        } else if (
          mtnObject.mtnDuration !== null &&
          mtnObject.mtnBu !== '' &&
          mtnObject.mtnModule !== '' &&
          confirmedUpdateSummaryButtonStatus.value
        ) {
          return false
        } else {
          return true
        }
      } else if (mtnObject.mtnStep === 3) {
        return false
      } else {
        return false
      }
    })

    function updateSummaryButton() {
      context.emit('updateSummaryByMtn', [mtnObject, mtnGroup])
      confirmedUpdateSummaryButtonStatus.value = true
    }

    function syncGoogleCalendar() {
      window.gapi.load('client:auth2', initClient)
    }

    function syncGoogleCalendarDelete() {
      window.gapi.load('client:auth2', initClientDelete)
    }

    function initClient() {
      // try to connect the google api client by .init with these informations
      window.gapi.client
        .init({
          apiKey: 'AIzaSyA_EH-gpXx9NTFHGBbcMgYOF27n2SP8hak',
          clientId:
            '720665971425-fspvrljso647ridnig69ol3j368glqsc.apps.googleusercontent.com',
          discoveryDocs: [
            'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'
          ],
          scope: 'https://www.googleapis.com/auth/calendar.readonly'
        })
        .then(function () {
          // Listen for sign-in state changes.
          window.gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus)

          // Handle the initial sign-in state.
          updateSigninStatus(window.gapi.auth2.getAuthInstance().isSignedIn.get())
        })
    }

    function initClientDelete() {
      // try to connect the google api client by .init with these informations
      window.gapi.client
        .init({
          apiKey: 'AIzaSyA_EH-gpXx9NTFHGBbcMgYOF27n2SP8hak',
          clientId:
            '720665971425-fspvrljso647ridnig69ol3j368glqsc.apps.googleusercontent.com',
          discoveryDocs: [
            'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'
          ],
          scope: 'https://www.googleapis.com/auth/calendar.readonly'
        })
        .then(function () {
          // Listen for sign-in state changes.
          window.gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus2)

          // Handle the initial sign-in state.
          updateSigninStatus2(window.gapi.auth2.getAuthInstance().isSignedIn.get())
        })
    }

    function updateSigninStatus2(isSignedIn) {
      if (isSignedIn) {
        deleteEvent()
      } else {
        // user does not login, so signin now
        window.gapi.auth2.getAuthInstance().signIn()
      }
    }

    function updateSigninStatus(isSignedIn) {
      if (isSignedIn) {
        createNewEvent()
      } else {
        // user does not login, so signin now
        window.gapi.auth2.getAuthInstance().signIn()
      }
    }

    async function removeCalenderDb() {
      const postData = reactive({
        targetIssueId: props.ticketJiraIssueId,
        source: 'otrs'
      })
      await axios
        .post(`https://${ServiceDomainLocal}:9487/mtn/delete`, postData)
        .then((res) => {
          if (res.status === 200) {
            $q.notify({
              message: '<b>GOOGLE CALENDAR DELETE SUCCESS!</b>',
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
            googleSet.link = ''
            googleSet.id = ''
            googleSet.dbSn = ''
            mtnObject.mtnStep = 1
          }
        })
        .catch((error) => {
          console.log(error)
          alert(error)
        })
    }

    function deleteEvent() {
      window.gapi.client.calendar.events
        .delete({
          calendarId: 'iogs6k5epliqpnv3vg220o29co@group.calendar.google.com',
          eventId: googleSet.id
        })
        .then(
          function (response) {
            if (response.status === 204) {
              // remove google calendar by api success
              // remove local db data by axios
              removeCalenderDb()
            } else {
              alert('something wrong, see the console log')
              console.log(response)
            }
          },
          function (error) {
            if (error.status === 410) {
              // Resource has been deleted, update local db here directly
              // remove local db data by axios
              removeCalenderDb()
            } else {
              alert('GoogleApiResponse: ' + error.body)
            }
          }
        )
    }

    function createNewEvent() {
      // let user know brower is doing the update
      const replaceFormatStringTime = mtnObject.mtnStartTime.replace(' ', 'T') + ':00'
      const replaceFormatEndTime = mtnObject.mtnEndTime.replace(' ', 'T') + ':00'
      const event = {
        summary: `YTS${props.ticketJiraIssueId} - ${props.ticketSubject}`,
        description: props.lastSummary,
        start: {
          // dateTime: '2021-11-29T10:45:00',
          dateTime: replaceFormatStringTime,
          timeZone: 'Asia/Taipei'
        },
        end: {
          // dateTime: '2021-11-29T12:00',
          dateTime: replaceFormatEndTime,
          timeZone: 'Asia/Taipei'
        },
        reminders: {
          useDefault: false,
          overrides: [
            { method: 'email', minutes: 10 },
            { method: 'popup', minutes: 10 }
          ]
        }
      }

      console.log(event)

      window.gapi.client.calendar.events
        .insert({
          calendarId: 'iogs6k5epliqpnv3vg220o29co@group.calendar.google.com',
          resource: event
        })
        .then(
          function (response) {
            $q.loading.hide()
            if (response.status === 200) {
              googleSet.link = response.result.htmlLink
              googleSet.id = response.result.id
              const postData = reactive({
                _id: googleSet.id,
                _link: googleSet.link,
                IssueId: props.ticketJiraIssueId,
                startTime: mtnObject.mtnStartTime,
                endTime: mtnObject.mtnEndTime,
                _type: mtnGroup.value,
                _source: 'otrs'
              })
              axios
                .post(`https://${ServiceDomainLocal}:9487/mtn/insert`, postData)
                .then((res) => {
                  console.log(res)
                  if (res.status === 200) {
                    $q.notify({
                      message: '<b>GOOGLE CALENDAR UPDATE SUCCESS!</b>',
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
                    mtnObject.mtnStep = 4
                  }
                })
                .catch((error) => {
                  console.log(error)
                })
            } else {
              alert('something wrong, see the console log')
              console.log(response)
            }
          },
          function (error) {
            alert('GoogleApiResponse: ' + error.body)
          }
        )
    }

    function stepperController() {
      console.log(mtnObject)
      if (mtnObject.mtnStartTime === '') {
        mtnObject.mtnStartTime = ref(date.formatDate(Date.now(), 'YYYY-MM-DD HH:mm'))
      }

      if (mtnObject.mtnStep === 4) {
        if (window.confirm('Do you want to DELETE this schedule on google calendar?')) {
          syncGoogleCalendarDelete()
        } else {
          console.log('has been canceled')
        }
      } else {
        mtnObject.mtnStep = ++mtnObject.mtnStep
      }
    }

    onMounted(() => {
      if (props.parentMtnFlagStatus) {
        // call DB to get google info for ${props.ticketDbSn}
        try {
          axios
            .get(
              `https://${ServiceDomainLocal}:9487/mtn/query/${props.ticketJiraIssueId}`
            )
            .then((res) => {
              if (Object.keys(res.data).length) {
                mtnObject.mtnStep = 4
                googleSet.id = res.data.googleCalendarId
                googleSet.link = res.data.googleCalendarLink
                googleSet.dbSn = res.data.sn
              } else {
                console.log(
                  `${props.ticketJiraIssueId} mtn button has been enabled, but user did not update the google calendar api accordingly`
                )
              }
            })
        } catch (error) {
          console.log(error)
        }
      }
    })

    watch(
      () => props.parentMtnFlagStatus,
      (state, prevState) => {
        if (state) {
          try {
            axios
              .get(
                `https://${ServiceDomainLocal}:9487/mtn/query/${props.ticketJiraIssueId}`
              )
              .then((res) => {
                if (Object.keys(res.data).length) {
                  mtnObject.mtnStep = 4
                  googleSet.id = res.data.googleCalendarId
                  googleSet.link = res.data.googleCalendarLink
                  googleSet.dbSn = res.data.sn
                } else {
                  console.log(
                    `${props.ticketJiraIssueId} mtn button has been enabled, but user did not update the google calendar api accordingly`
                  )
                }
              })
          } catch (error) {
            console.log(error)
          }
        }
      }
    )

    return {
      mtnGroup,
      mtnOptions,
      mtnObject,
      updateSummaryButton,
      syncGoogleCalendar,
      createNewEvent,
      defineNextButtonStatus,
      confirmedUpdateSummaryButtonStatus,
      reminderString,
      googleSet,
      ServiceDomainLocal,
      stepperController,
      deleteEvent,
      syncGoogleCalendarDelete,
      updateSigninStatus2,
      removeCalenderDb
    }
  }
})
</script>
