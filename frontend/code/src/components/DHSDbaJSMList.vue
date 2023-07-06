<!-- @format -->
<template>
  <q-ajax-bar
    ref="axiosExecuteBar"
    position="bottom"
    color="positive"
    size="10px"
    skip-hijack
  />

  <q-dialog full-width persistent v-model="localJSMSet.isShowUpdateJSMDescriptionEdit">
    <q-card>
      <q-card-section>
        <div class="text-h6">Change {{ issueKey }} description</div>
      </q-card-section>

      <q-card-section class="q-py-none">
        <q-editor
          class="col-12"
          v-model="localJSMSet.description"
          ref="targetRef"
          :toolbar="summaryToolBar"
        >
          <template v-slot:token>
            <q-btn-dropdown
              dense
              split
              unelevated
              padding="xs"
              fab-mini
              flat
              ref="q1BtnDropDownColor"
              icon="format_color_text"
              v-bind:text-color="
                foreColor ? ConvertforeColor('fore') : ConvertforeColor('fore')
              "
              @click="adjustSummaryColor('foreColor', foreColor)"
            >
              <q-list dense>
                <q-item
                  tag="label"
                  clickable
                  @click="adjustSummaryColor('foreColor', foreColor)"
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
              ref="q1BtnDropDownBGColor"
              icon="font_download"
              v-bind:text-color="
                backColor ? ConvertforeColor('back') : ConvertforeColor('back')
              "
              @click="adjustSummaryColor('backColor', backColor)"
              push
            >
              <q-list dense>
                <q-item
                  tag="label"
                  clickable
                  @click="adjustSummaryColor('backColor', backColor)"
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
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          flat
          label="Update"
          class="bg-primary"
          color="white"
          @click="localDescriptionUpdate"
          :disabled="localDescriptionLimit"
        />
        <q-btn flat label="Cancel" color="primary" @click="localDescriptionCancel" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog full-width persistent v-model="localJSMSet.isShowUpdateJSMTime">
    <q-card>
      <q-card-section>
        <div class="text-h6">Change {{ issueKey }} start time & end time</div>
      </q-card-section>
      <q-card-section>
        <div class="col q-pa-sm bg-grey-2">
          <div class="text-caption text-italic text-grey-9">* Start Time</div>
          <q-input class="" filled v-model="localJSMSet.sTime">
            <template v-slot:prepend>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-date v-model="localJSMSet.sTime" mask="YYYY-MM-DD HH:mm">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>

            <template v-slot:append>
              <q-icon name="access_time" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-time v-model="localJSMSet.sTime" mask="YYYY-MM-DD HH:mm" format24h>
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-time>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </div>
        <q-separator vertical inset />
        <div class="col q-pa-sm bg-grey-2">
          <div class="text-caption text-italic text-grey-9">* End Time</div>
          <q-input class="" filled v-model="localJSMSet.eTime">
            <template v-slot:prepend>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-date v-model="localJSMSet.eTime" mask="YYYY-MM-DD HH:mm">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>

            <template v-slot:append>
              <q-icon name="access_time" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-time v-model="localJSMSet.eTime" mask="YYYY-MM-DD HH:mm" format24h>
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-time>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          flat
          label="Update"
          class="bg-primary"
          color="white"
          @click="localTimeUpdate"
          :disable="localJSMSet.duration === null"
        />
        <q-btn flat label="Cancel" color="primary" @click="localTimeCancel" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <div
    v-if="(isShow === 99) | (jiraStatus === isShow)"
    class="row q-px-md q-pt-md q-pb-none row"
    :class="{ hidden: displayNameInclude === false }"
  >
    <q-card :id="'jsm' + sn" flat bordered class="col-12">
      <q-card-section class="row">
        <q-badge outline color="primary" floating>{{ adjustDisplayLink() }}</q-badge>
        <div class="row justify-start items-center text-h6 text-h6 col-md-9">
          <span class="text-blue-10" @click="expanded = !expanded">
            <q-icon
              :name="expanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
              class="q-pr-md"
            />{{ title }}</span
          >
        </div>
        <div class="col-md-3 text-right">
          <q-chip
            icon="open_in_new"
            color="primary"
            text-color="white"
            square
            class="text-right"
            clickable
            @click="openNewPageToTicket"
          >
            {{ issueKey }}
          </q-chip>
          <q-chip
            v-if="jiraStatus !== 71 && jiraStatus !== 121 && jiraStatus !== 6"
            :color="returnJiraContext('color')"
            text-color="dark"
            square
            class="text-right"
            @click="adjustJSMStatus"
            :clickable="localJSMSet.isClickableAdjustJSMStatus"
          >
            {{ returnJiraContext('str') }}
          </q-chip>
          <q-chip
            v-else
            :color="returnJiraContext('color')"
            text-color="dark"
            square
            class="text-right"
          >
            {{ returnJiraContext('str') }}
          </q-chip>
        </div>
      </q-card-section>
      <q-slide-transition>
        <div v-show="expanded">
          <q-separator />
          <section class="bg-cyan-1 rounded-borders q-ma-sm">
            <div
              class="row q-py-sm q-px-sm bg-cyan-1 text-bold justify-between items-center"
            >
              <div class="q-py-xs">Contents</div>

              <q-btn-group push>
                <q-btn
                  push
                  label="Change Queue to OPS"
                  icon="account_circle"
                  @click="changeQueueClick('ops_request')"
                />
                <q-btn
                  v-if="ticketStatus == 2 && content_html"
                  push
                  label="Email Content"
                  icon="description"
                  @click="displayEmailContent"
                />
              </q-btn-group>
            </div>
            <!-- <div v-if="ticketStatus === 2" class="row q-py-sm q-px-sm bg-cyan-1">
              <span class="col text-center">
                <q-chip
                  icon="sync"
                  color="primary"
                  text-color="white"
                  square
                  class="text-right"
                  clickable
                  @click="pullJSMTicket"
                >
                  Pull
                </q-chip></span
              >
            </div>
            <q-separator v-if="ticketStatus === 2" class="q-mx-none q-my-xs" inset /> -->
            <div
              @click="adjustJSMTitle"
              class="row q-py-sm q-px-sm q-mx-sm bg-teal-1 cursor-pointer"
            >
              <span class="col">Title</span>
              <span class="col">{{ all.title }}</span>
            </div>
            <div
              @click="adjustJSMDescription"
              class="row q-px-sm bg-white q-mx-sm cursor-pointer"
            >
              <span class="col-6 self-center">Description</span>
              <span class="col-6 text-right">
                <q-toggle
                  v-model="isShowDescription"
                  checked-icon="check"
                  color="green"
                  unchecked-icon="clear"
                />
              </span>
            </div>
            <div
              v-if="isShowDescription"
              class="col-12 q-py-sm q-px-sm bg-white q-mx-sm custom-jsm-description"
            >
              <span v-html="all.description"></span>
            </div>
            <section @click="adjustJSMHandler">
              <div
                v-if="all.custom_handler.length !== 0"
                class="row q-py-sm q-px-sm q-mx-sm bg-teal-1 cursor-pointer"
              >
                <span class="col">Request Handler</span>
                <span class="col">{{ all.custom_handler.join(', ') }}</span>
              </div>
              <div
                class="row q-py-sm q-px-sm q-mx-sm bg-teal-1 cursor-pointer text-red-6 text-italic"
                v-else
              >
                <span class="col">* Request Handler</span>
                <span class="col">None</span>
              </div>
            </section>
            <div
              @click="adjustJSMParticipant"
              class="row q-py-sm q-px-sm q-mx-sm bg-white cursor-pointer"
            >
              <span class="col">Participant(s)</span>
              <span v-if="all.custom_participant" class="col">{{
                all.custom_participant.join(', ')
              }}</span>
              <span v-else class="col">None</span>
            </div>
            <section @click="adjustJSMBizUnit">
              <div
                v-if="all.custom_bizUnit.length !== 0"
                class="row q-py-sm q-px-sm bg-teal-1 q-mx-sm cursor-pointer"
              >
                <span class="col">BizUnit</span>
                <span class="col">{{ all.custom_bizUnit.join(', ') }}</span>
              </div>
              <div
                class="row q-py-sm q-px-sm bg-teal-1 q-mx-sm cursor-pointer text-red-6 text-italic"
                v-else
              >
                <span class="col">* BizUnit</span>
                <span class="col">None</span>
              </div>
            </section>
            <section @click="adjustJSMCategory">
              <div
                v-if="all.custom_category.length !== 0"
                class="row q-py-sm q-px-sm bg-white q-mx-sm cursor-pointer"
              >
                <span class="col">Category DBA</span>
                <span class="col">{{ all.custom_category.join(', ') }}</span>
              </div>
              <div
                class="row q-py-sm q-px-sm bg-white q-mx-sm cursor-pointer text-red-6 text-italic"
                v-else
              >
                <span class="col">* Category DBA</span>
                <span class="col">None</span>
              </div>
            </section>
            <section @click="adjustJSMPriority">
              <div
                v-if="all.custom_priority"
                class="row q-py-sm q-px-sm bg-teal-1 q-mx-sm cursor-pointer"
              >
                <span class="col">Priority</span>
                <span class="col">{{ all.custom_priority }}</span>
              </div>
              <div
                class="row q-py-sm q-px-sm bg-teal-1 q-mx-sm cursor-pointer text-red-6 text-italic"
                v-else
              >
                <span class="col">* Priority</span>
                <span class="col">None</span>
              </div>
            </section>
            <section @click="adjustJSMStartTime">
              <div
                class="row q-py-sm q-px-sm bg-white q-mx-sm cursor-pointer"
                v-if="all.startTime !== '1989-11-09 08:00'"
              >
                <span class="col">Start Time</span>
                <span class="col">{{ all.startTime }}</span>
              </div>
              <div
                class="row q-py-sm q-px-sm bg-white q-mx-sm cursor-pointer text-red-6 text-italic"
                v-else
              >
                <span class="col">* Start Time</span>
                <span class="col">None</span>
              </div>
            </section>
            <section @click="adjustJSMEndTime">
              <div
                v-if="all.endTime !== '1989-11-09 08:00'"
                class="row q-py-sm q-px-sm bg-teal-1 q-mx-sm cursor-pointer"
              >
                <span class="col">End Time</span>
                <span class="col">{{ all.endTime }}</span>
              </div>
              <div
                class="row q-py-sm q-px-sm bg-teal-1 q-mx-sm cursor-pointer text-red-6 text-italic"
                v-else
              >
                <span class="col">* End Time</span>
                <span class="col">None</span>
              </div>
            </section>
            <section @click="adjustJSMWorkHours">
              <div
                v-if="all.custom_workLogValue / 60 !== 0"
                class="row q-py-sm q-px-sm bg-white q-mx-sm cursor-pointer"
              >
                <span class="col">Working Minutes</span>
                <span class="col">{{ all.custom_workLogValue / 60 }}</span>
              </div>
              <div
                class="row q-py-sm q-px-sm bg-white q-mx-sm cursor-pointer text-red-6 text-italic"
                v-else
              >
                <span class="col">* Working Minutes</span>
                <span class="col">None</span>
              </div>
            </section>
            <div
              @click="adjustJSMServiceImpact"
              class="row q-py-sm q-px-sm bg-teal-1 q-mx-sm cursor-pointer"
            >
              <span class="col">Service Impact</span>
              <span class="col" v-if="all.custom_isImpact">Yes</span>
              <span class="col" v-else>No</span>
            </div>
          </section>
          <q-separator class="q-mx-none q-pt-xs" color="red-2" inset />
          <section class="bg-cyan-1 rounded-borders q-ma-sm">
            <div class="row text-bold q-py-sm">
              <span class="col self-center q-pl-sm"> Comments </span>
              <span class="col text-right">
                <q-btn
                  class="q-ma-sm"
                  color="green"
                  icon="add"
                  size="xs"
                  @click="openNewPageToAddComment"
                  :disabled="isShowCommentEditor"
                />
              </span>
            </div>
            <div class="row" v-if="isShowCommentEditor">
              <section class="q-px-sm q-pb-sm col-12 bg-teal-1">
                <q-editor
                  class="col-12"
                  v-model="localNewComment"
                  ref="targetRef"
                  :toolbar="summaryToolBar"
                >
                  <template v-slot:token>
                    <q-btn-dropdown
                      dense
                      split
                      unelevated
                      padding="xs"
                      fab-mini
                      flat
                      ref="q1BtnDropDownColor"
                      icon="format_color_text"
                      v-bind:text-color="
                        foreColor ? ConvertforeColor('fore') : ConvertforeColor('fore')
                      "
                      @click="adjustSummaryColor('foreColor', foreColor)"
                    >
                      <q-list dense>
                        <q-item
                          tag="label"
                          clickable
                          @click="adjustSummaryColor('foreColor', foreColor)"
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
                      ref="q1BtnDropDownBGColor"
                      icon="font_download"
                      v-bind:text-color="
                        backColor ? ConvertforeColor('back') : ConvertforeColor('back')
                      "
                      @click="adjustSummaryColor('backColor', backColor)"
                      push
                    >
                      <q-list dense>
                        <q-item
                          tag="label"
                          clickable
                          @click="adjustSummaryColor('backColor', backColor)"
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
                  <template v-slot:token3>
                    <q-btn
                      class="q-px-sm"
                      no-caps
                      color="white"
                      text-color="black"
                      label="Template"
                      dense
                    >
                      <q-menu>
                        <q-list dense style="min-width: 100px">
                          <q-item v-for="i in templatesSet" :key="i.name" clickable>
                            <q-item-section>{{ i.name }}</q-item-section>
                            <q-item-section side>
                              <q-icon name="keyboard_arrow_right" />
                            </q-item-section>

                            <q-menu anchor="top end" self="top start">
                              <q-list>
                                <q-item
                                  v-for="n in i.value"
                                  :key="n.name"
                                  dense
                                  clickable
                                >
                                  <q-item-section
                                    @click="updateValueToSummary(n)"
                                    v-html="n.value"
                                  ></q-item-section>
                                </q-item>
                              </q-list>
                            </q-menu>
                          </q-item>
                          <q-separator />
                          <q-item clickable v-close-popup>
                            <q-item-section>Quit</q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </template>
                </q-editor>
                <section class="col-12 text-right">
                  <q-btn
                    class="q-mt-xs q-ml-xs"
                    color="primary"
                    text-color="white"
                    label="Update"
                    @click="commentBtnUpdate"
                    :disabled="localCommentLimit"
                  >
                  </q-btn>
                  <q-btn
                    class="q-mt-xs q-ml-xs"
                    color="white"
                    text-color="primary"
                    label="Cancel"
                    @click="commentBtnCancel"
                  >
                  </q-btn>
                </section>
              </section>
            </div>
            <div class="row" v-for="(comment, index) in comments" :key="comment.sn">
              <div
                v-if="isDisplayComment(index)"
                class="col-12 row q-pa-sm bg-white custom-border-display jsmNet"
              >
                <div class="col-9 self-center" v-html="comment.content"></div>
                <div class="col self-center row text-italic">
                  <div class="col">Update by {{ comment.handler }}</div>
                  <div class="col text-right">( at {{ comment.timestamp }} )</div>
                </div>
              </div>
            </div>
            <div v-if="comments" class="row q-py-sm justify-center">
              <q-pagination
                color="green"
                v-model="paginationSet.curPage"
                :max="paginationSet.maxPage"
              />
            </div>
          </section>
        </div>
      </q-slide-transition>
    </q-card>
  </div>
</template>
<script>
import {
  defineComponent,
  ref,
  reactive,
  inject,
  getCurrentInstance,
  computed,
  watch
} from 'vue'
import axios from 'axios'
import { useStore } from 'vuex'
import { scroll, useQuasar, date } from 'quasar'

export default defineComponent({
  name: 'DHSSysJSMList',
  components: {},
  emits: ['triggerByJsmList', 'triggerByChangeQ'],
  props: {
    custom_handler: Object,
    custom_participant: Object,
    custom_bizUnit: Object,
    custom_category: Object,
    custom_isImpact: Boolean,
    custom_workLogId: Number,
    custom_workLogValue: Number,
    custom_priority: String,
    attachments: Object,
    comments: Object,
    sn: Number,
    mapping: Number,
    title: String,
    description: String,
    content_html: String,
    createdTime: String,
    startTime: String,
    endTime: String,
    issueId: String,
    issueKey: String,
    issueUrl: String,
    jiraStatus: Number,
    ticketStatus: Number,
    all: Object,
    isShow: Number,
    displayNameInclude: Boolean,
    expandedStatus: Boolean
  },
  setup(props, context) {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex

    const expanded = ref(false)
    const isShowDescription = ref(true)
    const isShowContentHtml = ref(false)
    const isShowCommentEditor = ref(false)
    const localDescriptionLimit = ref(false)
    const localCommentLimit = ref(true)
    const localNewComment = ref('')
    const localJSMSet = reactive({
      isShowUpdateJSMDescriptionEdit: false,
      isShowUpdateJSMTime: false,
      isClickableAdjustJSMStatus: true,
      description: props.description,
      handler: props.custom_handler,
      participant: props.custom_participant ? props.custom_participant : [],
      bizUnit: props.custom_bizUnit,
      category: props.custom_category,
      priority: props.custom_priority,
      sTime: props.startTime,
      eTime: props.endTime,
      duration: computed(() => {
        if (date.isValid(localJSMSet.sTime) && date.isValid(localJSMSet.eTime)) {
          const startTimeObject = new Date(localJSMSet.sTime)
          const endTimeObject = new Date(localJSMSet.eTime)
          const diff = date.getDateDiff(endTimeObject, startTimeObject, 'minutes')
          if (diff > 0) {
            return [`${diff} minutes`, diff]
          } else {
            return null
          }
        } else {
          return null
        }
      })
    })

    const paginationSet = reactive({
      maxPage: props.comments ? Math.ceil(props.comments.length / 5) : 1,
      curPage: 1,
      curArray: computed(() => {
        const conditionList = ref([])
        const startNum = ref(paginationSet.curPage * 5 - 1)
        while (conditionList.value.length < 5) {
          conditionList.value.push(startNum.value)
          --startNum.value
        }
        return conditionList.value
      })
    })

    const axiosExecuteBar = ref(null)

    const { proxy } = getCurrentInstance()
    const isLogin = inject('isLogin') // get the root isLogin dict
    const tabofCard = ref('two') // check the note card tab need to display which one
    const dialogUnderEditing = ref(false) // display alert popup window when note is under editing
    const localEditorStatus = ref(false) // display note raw data or rich text
    const summaryToolBar = ref([
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
      ['token3'],
      ['fullscreen']
    ]) // default will not show the toolbar
    const q1BtnDropDownColor = ref(null) // summary font color button
    const q1BtnDropDownBGColor = ref(null) // summary background button
    const foreColor = ref('#000000') // default font color
    const backColor = ref('#ffff00') // default font bg color
    const targetRef = ref(null) // q-editor summary ref
    const { getScrollTarget, setVerticalScrollPosition } = scroll // scroll function

    // Templates reacitve object
    const templatesSet = reactive([
      {
        name: 'Event example',
        value: [
          {
            name: 'Example1',
            value: `
            <div><b>Event</b>:</div>
            <div><b>Finding</b>:</div>
            <div><b>Action</b>:</div>
            <div><b>Current Status</b>:</div>
            <div><b>Follow up</b>:</div>
        `
          }
        ]
      },
      {
        name: 'Incident example',
        value: [
          {
            name: 'Example1',
            value: `
          <div><b>Conclusion</b>:</div>
          <div><b>Event</b>:</div>
          <div><b>Action</b>:</div>
          <div><i>Affected BU</i>:</div>
          <div><i>Affected Module</i>:</div>
          <div><b>Current status</b>:</div>
          <div><b>Timestamp</b>:</div>
          <div><i>Reference chatroom</i>:</div>
        `
          }
        ]
      }
    ])

    // use this one to change the text-color
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

    function adjustSummaryColor(cmd, name) {
      proxy.q1BtnDropDownColor.hide()
      proxy.q1BtnDropDownBGColor.hide()
      proxy.targetRef.runCmd(cmd, name)
      proxy.targetRef.focus()
    }

    function openNewPageToTicket() {
      window.open(props.issueUrl, '_blank')
    }

    function openNewPageToAddComment() {
      console.log('hit openNewPageToAddComment')
      isShowCommentEditor.value = true
    }

    function returnJiraContext(currentType) {
      switch (props.jiraStatus) {
        case 1:
        case 10132:
          if (currentType === 'color') {
            return 'grey-4'
          } else {
            return 'Open'
          }
        case 4:
          if (currentType === 'color') {
            return 'grey-4'
          } else {
            return 'Reopened'
          }
        case 3:
        case 101:
        case 241:
          if (currentType === 'color') {
            return 'blue-3'
          } else {
            return 'In Progress'
          }
        case 61:
        case 10011:
        case 10129:
          if (currentType === 'color') {
            return 'green-3'
          } else {
            return 'Completed'
          }
        case 191:
        case 211:
        case 251:
        case 10004:
        case 10114:
          if (currentType === 'color') {
            return 'green-3'
          } else {
            return 'Canceled'
          }
        case 6:
        case 71:
        case 121:
          if (currentType === 'color') {
            return 'red-3'
          } else {
            return 'Closed'
          }
        default:
          if (currentType === 'color') {
            return 'yellow-4'
          } else {
            return 'Unknown'
          }
      }
    }

    function commentBtnUpdate() {
      const postData = {
        newEditor: isLogin.value,
        targetJsmSn: props.sn,
        targetJsmIssueKey: props.issueKey,
        comment: localNewComment.value,
        group: 'DBA'
      }
      axios
        .post(`https://${ServiceDomainLocal}:9487/bpCowork/update/comment`, postData)
        .then((res) => {
          console.log(res)
          if (res.status === 200) {
            $q.notify({
              message: '<b>Add comment successful!</b>',
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
            isShowCommentEditor.value = false
            localNewComment.value = ''
            const ele = document.getElementById('jsm' + props.sn)
            const target = getScrollTarget(ele)
            const offset = ele.offsetTop - 55
            const duration = 200
            setVerticalScrollPosition(target, offset, duration)
            context.emit('triggerByJsmList', { target: props.sn, issueId: props.issueId })
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function commentBtnCancel() {
      isShowCommentEditor.value = false
      localNewComment.value = ''
      const ele = document.getElementById('jsm' + props.sn)
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - 55
      const duration = 200
      setVerticalScrollPosition(target, offset, duration)
    }

    async function adjustJSMStatus() {
      localJSMSet.isClickableAdjustJSMStatus = false
      const itemOption = ref()
      // const res = ref()
      const postData = reactive({
        issueId: props.issueId,
        issueKey: props.issueKey,
        localDbSn: props.sn,
        whichTeam: 'DBA'
      })
      try {
        const res = await axios.post(
          `https://${ServiceDomainLocal}:9487/bpRoutine/jsm/statusOption`,
          postData
        )
        itemOption.value = res.data
        $q.dialog({
          title: `Change ${props.issueKey} status`,
          message: 'Assign to which status?',
          options: {
            type: 'radio',
            model: false,
            items: itemOption.value,
            isValid: (val) => val !== false
          },
          cancel: true,
          persistent: true
        }).onOk((data) => {
          const barRef = axiosExecuteBar.value
          barRef.start()
          const postData = reactive({
            targetJSMSn: props.sn,
            jsmIssueId: props.issueId,
            jsmIssueKey: props.issueKey,
            toWhichStatus: data,
            editor: isLogin.value
          })
          axios
            .post(
              `https://${ServiceDomainLocal}:9487/bpCowork/jsm/dba/update/status`,
              postData
            )
            .then((res) => {
              $q.notify({
                message: `Change ${props.issueKey} status successful!`,
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
              barRef.stop()
              localJSMSet.isClickableAdjustJSMStatus = true
              context.emit('triggerByJsmList', {
                target: props.sn,
                issueId: props.issueId
              })
            })
            .catch((error) => {
              $q.notify({
                message: `Update JSM Status failed, reason - ${error.response.data}`,
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
              localJSMSet.isClickableAdjustJSMStatus = true
              barRef.stop()
            })
        })
        localJSMSet.isClickableAdjustJSMStatus = true
      } catch (e) {
        $q.notify({
          message: `Load JSM Status Option failed, reason - ${e.response.data}`,
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
        localJSMSet.isClickableAdjustJSMStatus = true
      }
    }

    function adjustJSMTitle() {
      $q.dialog({
        title: `Change ${props.issueKey} Title`,
        prompt: {
          model: props.title,
          isValid: (val) => val !== props.title && val !== '', // << here is the magic
          type: 'text' // optional
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'title',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'title')
      })
    }

    // open the q-dialog popup-windows
    function adjustJSMDescription() {
      localJSMSet.isShowUpdateJSMDescriptionEdit = true
    }

    // description popup-window update to backend
    function localDescriptionUpdate() {
      const postData = reactive({
        targetJSMSn: props.sn,
        jsmIssueId: props.issueId,
        jsmIssueKey: props.issueKey,
        target: 'description',
        newValue: localJSMSet.description,
        editor: isLogin.value
      })
      console.log(postData)
      updateToJSM(postData, 'description')
    }

    // description popup-window close
    function localDescriptionCancel() {
      localJSMSet.description = props.description
      localJSMSet.isShowUpdateJSMDescriptionEdit = false
    }

    function adjustJSMHandler() {
      const itemsSortOut = ref([
        {
          label: 'David Tung',
          value: 'David Tung',
          disable: false
        },
        {
          label: 'Tony Wu',
          value: 'Tony Wu',
          disable: false
        },
        {
          label: 'Albert Huang',
          value: 'Albert Huang',
          disable: false
        },
        {
          label: 'Robert Lin',
          value: 'Robert Lin',
          disable: false
        },
        {
          label: 'Stanley Chen',
          value: 'Stanley Chen',
          disable: false
        },
        {
          label: 'Demon Wu',
          value: 'Demon Wu',
          disable: false
        },
        {
          label: 'Carny Chou',
          value: 'Carny Chou',
          disable: false
        },
        {
          label: 'Austin Chang',
          value: 'Austin Chang',
          disable: false
        },
        {
          label: 'William Liu',
          value: 'William Liu',
          disable: false
        }
      ])

      // check if need to disable the option
      if (props.custom_participant) {
        props.custom_participant.forEach(function (ele, index, object) {
          itemsSortOut.value.forEach((ele2) => {
            if (ele2.label === ele) {
              ele2.disable = true
              ele2.label = `${ele2.label} - assigned to participant`
            }
          })
        })
      }

      $q.dialog({
        title: `Change ${props.issueKey} handler`,
        options: {
          type: 'checkbox',
          model: localJSMSet.handler,
          items: itemsSortOut.value,
          isValid: (val) => val.length !== 0
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'handler',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'handler')
        // need this one to update local data
        localJSMSet.handler = data
      })
    }

    function adjustJSMParticipant() {
      const itemsSortOut = ref([
        {
          label: 'David Tung',
          value: 'David Tung',
          disable: false
        },
        {
          label: 'Tony Wu',
          value: 'Tony Wu',
          disable: false
        },
        {
          label: 'Albert Huang',
          value: 'Albert Huang',
          disable: false
        },
        {
          label: 'Robert Lin',
          value: 'Robert Lin',
          disable: false
        },
        {
          label: 'Stanley Chen',
          value: 'Stanley Chen',
          disable: false
        },
        {
          label: 'Demon Wu',
          value: 'Demon Wu',
          disable: false
        },
        {
          label: 'Carny Chou',
          value: 'Carny Chou',
          disable: false
        },
        {
          label: 'Austin Chang',
          value: 'Austin Chang',
          disable: false
        },
        {
          label: 'William Liu',
          value: 'William Liu',
          disable: false
        }
      ])

      // check if need to disable the option
      if (props.custom_handler) {
        props.custom_handler.forEach(function (ele, index, object) {
          itemsSortOut.value.forEach((ele2) => {
            if (ele2.label === ele) {
              ele2.disable = true
              ele2.label = `${ele2.label} - assigned to handler`
            }
          })
        })
      }

      $q.dialog({
        title: `Change ${props.issueKey} participant`,
        options: {
          type: 'checkbox',
          model: localJSMSet.participant,
          items: itemsSortOut.value
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'participant',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'participant')
        // need this one to update local data
        localJSMSet.participant = data
      })
    }

    async function adjustJSMBizUnit() {
      // get option list by backend
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/bpCowork/jsm/query/field/customfield_10281/3`
      )
      // popup windows
      $q.dialog({
        title: `Change ${props.issueKey} bizUnit`,
        options: {
          type: 'checkbox',
          model: localJSMSet.bizUnit,
          items: res.data,
          isValid: (val) => val.length !== 0
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'bizUnit',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'bizUnit')
        // need this one to update local data
        localJSMSet.bizUnit = data
      })
    }

    async function adjustJSMCategory() {
      // get option list by backend
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/bpCowork/jsm/query/field/customfield_10289/3`
      )
      // popup windows
      $q.dialog({
        title: `Change ${props.issueKey} category`,
        options: {
          type: 'checkbox',
          model: localJSMSet.category,
          items: res.data,
          isValid: (val) => val.length !== 0
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'category',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'category')
        // need this one to update local data
        localJSMSet.category = data
      })
    }

    function adjustJSMPriority() {
      $q.dialog({
        title: `Change ${props.issueKey} priority`,
        options: {
          type: 'radio',
          model: localJSMSet.priority,
          items: [
            {
              label: 'Highest',
              value: 'Highest'
            },
            {
              label: 'High',
              value: 'High'
            },
            {
              label: 'Medium',
              value: 'Medium'
            },
            {
              label: 'Low',
              value: 'Low'
            },
            {
              label: 'Lowest',
              value: 'Lowest'
            }
          ],
          isValid: (val) => val !== localJSMSet.priority
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'priority',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'priority')
        // need this one to update local data
        localJSMSet.priority = data
      })
    }

    function adjustJSMStartTime() {
      localJSMSet.isShowUpdateJSMTime = true
      console.log('adjustJSMStartTime')
    }

    function adjustJSMEndTime() {
      localJSMSet.isShowUpdateJSMTime = true
      console.log('adjustJSMEndTime')
    }

    function localTimeUpdate() {
      localJSMSet.isShowUpdateJSMTime = false
      const postData = reactive({
        targetJSMSn: props.sn,
        jsmIssueId: props.issueId,
        jsmIssueKey: props.issueKey,
        target: 'time',
        newValue: [localJSMSet.sTime, localJSMSet.eTime],
        editor: isLogin.value
      })
      updateToJSM(postData, 'time')
    }

    function localTimeCancel() {
      localJSMSet.isShowUpdateJSMTime = false
      // rollback
      localJSMSet.sTime = props.startTime
      localJSMSet.eTime = props.endTime
    }

    function adjustJSMWorkHours() {
      $q.dialog({
        title: `Change ${props.issueKey} working minutes`,
        message:
          '<b>Unit: </b><span style="color:red;">minutes</span><li>1 hour = 60 minutes;</li><li>8 hours = 480 minutes;</li><li>1 day = 1440 minutes;</li><li>7 day = 10080 minutes;</li>',
        prompt: {
          model: props.custom_workLogValue / 60,
          type: 'number', // optional
          isValid: (val) => parseInt(val, 10) > 0 && Number.isInteger(parseInt(val, 10))
        },
        cancel: true,
        persistent: true,
        html: true
      }).onOk((data) => {
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'title',
          targetWorkLogId: props.custom_workLogId,
          newValue: data,
          editor: isLogin.value
        })
        updateJSMWorkLog(postData, 'title')
      })
    }

    function adjustJSMServiceImpact() {
      $q.dialog({
        title: `Change ${props.issueKey} Service impact`,
        options: {
          type: 'radio',
          model: props.custom_isImpact,
          items: [
            {
              label: 'Yes',
              value: true,
              color: 'red-6'
            },
            {
              label: 'No',
              value: false,
              color: 'green-6'
            }
          ],
          isValid: (val) => val !== props.custom_isImpact
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        console.log(data)
        const postData = reactive({
          targetJSMSn: props.sn,
          jsmIssueId: props.issueId,
          jsmIssueKey: props.issueKey,
          target: 'impact',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'impact')
      })
    }

    async function updateJSMWorkLog(payload, target) {
      const barRef = axiosExecuteBar.value
      barRef.start()
      await axios
        .post(
          `https://${ServiceDomainLocal}:9487/bpCowork/jsm/dba/update/worklog`,
          payload
        )
        .then((res) => {
          if (res.status === 200) {
            $q.notify({
              message: `<b>JSM ${props.issueKey} ${target} has been updated!</b>`,
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
            context.emit('triggerByJsmList', {
              target: props.sn,
              issueId: props.issueId
            })
          }
        })
        .catch((error) => {
          console.log(error)
          $q.notify({
            message: `JSM ${props.issueKey} <b> ${target} update failed!</b>, open the developer tool to see the detail`,
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
      barRef.stop()
      localJSMSet.isShowUpdateJSMDescriptionEdit = false
    }

    // running bar and notify here
    async function updateToJSM(payload, target) {
      const barRef = axiosExecuteBar.value
      barRef.start()
      await axios
        .post(
          `https://${ServiceDomainLocal}:9487/bpCowork/jsm/dba/update/option`,
          payload
        )
        .then((res) => {
          if (res.status === 200) {
            $q.notify({
              message: `<b>JSM ${props.issueKey} ${target} has been updated!</b>`,
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
            context.emit('triggerByJsmList', {
              target: props.sn,
              issueId: props.issueId
            })
          }
        })
        .catch((error) => {
          console.log(error)
          $q.notify({
            message: `JSM ${props.issueKey} <b> ${target} update failed!</b>, open the developer tool to see the detail`,
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
      barRef.stop()
      localJSMSet.isShowUpdateJSMDescriptionEdit = false
    }

    function isDisplayComment(index) {
      return paginationSet.curArray.includes(index)
    }

    // async function pullJSMTicket() {
    //   const postData = reactive({
    //     LocalSn: props.sn,
    //     issueId: props.issueId,
    //     issueKey: props.issueKey,
    //     editor: isLogin.value
    //   })
    //   const barRef = axiosExecuteBar.value
    //   barRef.start()
    //   await axios
    //     .post(`https://${ServiceDomainLocal}:9487/bpCowork/jsm/pull/dba`, postData)
    //     .then((res) => {
    //       if (res.status === 200) {
    //         $q.notify({
    //           message: `JSM <b>${props.issueKey}</b> all options (except Description) have been <b>synced</b>!`,
    //           color: 'green-6',
    //           progress: true,
    //           html: true,
    //           actions: [
    //             {
    //               icon: 'cancel',
    //               color: 'white',
    //               handler: () => {}
    //             }
    //           ]
    //         })
    //         context.emit('triggerByJsmList', {
    //           target: props.sn,
    //           issueId: props.issueId
    //         })
    //       }
    //     })
    //     .catch((error) => {
    //       $q.notify({
    //         message: `JSM <b>${props.issueKey}</b> sync action failed, detail please refer console.log`,
    //         color: 'red-6',
    //         progress: true,
    //         html: true,
    //         actions: [
    //           {
    //             icon: 'cancel',
    //             color: 'white',
    //             handler: () => {}
    //           }
    //         ]
    //       })
    //       console.log(error)
    //     })
    //   barRef.stop()
    // }

    function changeQueueClick(targetTeam) {
      $q.dialog({
        title: 'Confirm',
        message: `Would you like to change <b>${props.issueKey}</b> queue to OPS?`,
        cancel: true,
        persistent: true,
        html: true
      }).onOk(async () => {
        const postData = {
          editor: isLogin.value,
          newGroup: targetTeam,
          ticketSn: props.sn,
          ticketMapping: props.mapping,
          ticketIssueId: props.issueId,
          ticketIssueKey: props.issueKey
        }
        console.log(postData)
        const barRef = axiosExecuteBar.value
        barRef.start()
        axios
          .post(`https://${ServiceDomainLocal}:9487/bpCowork/change/queue`, postData)
          .then((res) => {
            // console.log(res)
            if (res.status === 200) {
              $q.notify({
                message: `Change ${props.issueKey} - ${props.title} to <b>OPS</b> successful!`,
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
              barRef.stop()
              // reset all jira ticket
              context.emit('triggerByChangeQ')
            } else {
              console.log(res.status)
              barRef.stop()
            }
          })
          .catch((error) => {
            console.log(error)
            barRef.stop()
          })
      })
    }

    function displayEmailContent() {
      $q.dialog({
        title: `${props.issueKey}: Email content`,
        html: true,
        fullWidth: true,
        message: props.content_html
      })
        .onOk(() => {
          // console.log('OK')
        })
        .onCancel(() => {
          // console.log('Cancel')
        })
        .onDismiss(() => {
          // console.log('I am triggered on both OK and Cancel')
        })
    }

    function adjustDisplayLink() {
      if (props.ticketStatus === 1) {
        return 'WORKLOG'
      } else {
        return 'JSM'
      }
    }

    watch(
      () => props.expandedStatus,
      (curValue, oldValue) => {
        expanded.value = curValue
      }
    )

    watch(
      () => localJSMSet.description,
      (curValue, oldValue) => {
        const checker = ref([false, false])
        // size limit
        if (curValue.length > 30000 && oldValue.length < 30000) {
          $q.notify({
            message: `<b>Word restriction!</b> ( limit: 30000, current: ${curValue.length})`,
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
          checker.value[0] = true
        } else if (curValue.length < 30000 && oldValue.length > 30000) {
          $q.notify({
            message: `Remove <b>Word restriction</b> limit. (current: ${curValue.length})`,
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
          checker.value[0] = false
        }

        if (checker.value.includes(true)) {
          localDescriptionLimit.value = true
        } else {
          localDescriptionLimit.value = false
        }
      }
    )

    watch(
      () => localNewComment.value,
      (curValue, oldValue) => {
        const checker = ref([false, false])
        // size limit
        if (curValue.length > 10000 && oldValue.length < 10000) {
          $q.notify({
            message: `<b>Word restriction!</b> ( limit: 10000, current: ${curValue.length})`,
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
          checker.value[0] = true
        } else if (curValue.length < 10000 && oldValue.length > 10000) {
          $q.notify({
            message: `Remove <b>Word restriction</b> limit. (current: ${curValue.length})`,
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
          checker.value[0] = false
        }

        // image checker
        if (curValue.includes('<img src=')) {
          $q.notify({
            message: 'Not allow <b>IMG</b>',
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
          checker.value[1] = true
        }

        if (checker.value.includes(true)) {
          localCommentLimit.value = true
        } else {
          localCommentLimit.value = false
        }
      }
    )

    return {
      isLogin,
      tabofCard,
      ServiceDomainLocal,
      dialogUnderEditing,
      localEditorStatus,
      summaryToolBar,
      ConvertforeColor,
      adjustSummaryColor,
      foreColor,
      backColor,
      templatesSet,
      q1BtnDropDownColor,
      q1BtnDropDownBGColor,
      targetRef,
      openNewPageToTicket,
      openNewPageToAddComment,
      returnJiraContext,
      isShowDescription,
      isShowContentHtml,
      isShowCommentEditor,
      localNewComment,
      commentBtnUpdate,
      commentBtnCancel,
      adjustJSMStatus,
      adjustJSMTitle,
      adjustJSMDescription,
      adjustJSMHandler,
      adjustJSMParticipant,
      adjustJSMBizUnit,
      adjustJSMCategory,
      adjustJSMPriority,
      adjustJSMStartTime,
      adjustJSMEndTime,
      adjustJSMWorkHours,
      adjustJSMServiceImpact,
      axiosExecuteBar,
      localJSMSet,
      localDescriptionUpdate,
      localDescriptionCancel,
      localTimeUpdate,
      localTimeCancel,
      paginationSet,
      isDisplayComment,
      // pullJSMTicket,
      expanded,
      changeQueueClick,
      displayEmailContent,
      adjustDisplayLink,
      localDescriptionLimit,
      localCommentLimit
    }
  }
})
</script>

<style lang="scss">
.q-editor__toolbar-group {
  a {
    font-size: 16px !important;
  }
}

.my-picker {
  .q-color-picker__cube {
    width: 14.165% !important;
    padding-bottom: 14.165% !important;
  }
}

.q-editor__toolbar {
  align-items: center !important;
}

.wrapper {
  white-space: pre-wrap;
}

.custom-based-on-child {
  width: fit-content;
}

span.custom-jsm-description {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

font[size='1'] {
  font-size: 10px;
}
font[size='2'] {
  font-size: 14px;
}
font[size='3'] {
  font-size: 16px;
}
font[size='4'] {
  font-size: 18px;
}
font[size='5'] {
  font-size: 24px;
}
font[size='6'] {
  font-size: 32px;
}
font[size='7'] {
  font-size: 99px;
}
</style>
