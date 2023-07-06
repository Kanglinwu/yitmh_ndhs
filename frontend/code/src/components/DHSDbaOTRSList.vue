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
        <div class="text-h6">Change YTS{{ ticketNumber }}-{{ title }} description</div>
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
        />
        <q-btn flat label="Cancel" color="primary" @click="localDescriptionCancel" />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <div
    class="row q-px-md q-pt-md q-pb-none row"
    :class="{ hidden: displayNameInclude === false }"
  >
    <q-card :id="'dbaOtrs' + sn" flat bordered class="col-12">
      <q-card-section class="row">
        <div class="row justify-start items-center text-h6 text-h6 col-md-10">
          <span class="text-blue-10">
            <q-icon
              :name="expanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
              class="q-pr-md cursor-pointer"
              @click="expanded = !expanded"
            />
            <span class="cursor-pointer" @click="openNewPageToTicket"
              >YTS{{ ticketNumber }} - {{ title }}</span
            >
          </span>
        </div>
        <div class="col-md-2 text-right">
          <q-chip
            v-if="status"
            text-color="white"
            color="green-6"
            label="OPEN"
            class="cursor-pointer"
            @click="closeTheOTRSTicket"
            clickable
          ></q-chip>
          <q-chip v-else text-color="white" color="red-6" label="CLOSE"></q-chip>
        </div>
      </q-card-section>
      <q-slide-transition>
        <div v-show="expanded">
          <q-separator />
          <section class="bg-orange-1 rounded-borders q-ma-sm q-pb-sm">
            <div class="row q-py-md q-px-sm bg-orange-1 text-bold">Contents</div>
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
            <q-separator v-if="isShowDescription" color="red-2" inset />
            <div
              v-if="isShowDescription"
              class="col-12 q-py-sm q-px-sm bg-white q-mx-sm custom-jsm-description"
            >
              <span v-html="description"></span>
            </div>
            <section @click="adjustJSMCategory">
              <div
                v-if="custom_category.length !== 0"
                class="row q-py-sm q-px-sm bg-indigo-1 q-mx-sm cursor-pointer"
              >
                <span class="col">Category DBA</span>
                <span class="col">{{ custom_category.join(', ') }}</span>
              </div>
              <div class="row q-py-sm q-px-sm bg-indigo-1 q-mx-sm cursor-pointer" v-else>
                <span class="col">Category DBA</span>
                <span class="col">None</span>
              </div>
            </section>
            <section @click="adjustJSMHandler">
              <div
                v-if="custom_handler.length !== 0"
                class="row q-py-sm q-px-sm q-mx-sm bg-white cursor-pointer"
              >
                <span class="col">Request Handler</span>
                <span class="col">{{ custom_handler.join(', ') }}</span>
              </div>
              <div class="row q-py-sm q-px-sm q-mx-sm bg-white cursor-pointer" v-else>
                <span class="col">Request Handler</span>
                <span class="col">None</span>
              </div>
            </section>
            <section @click="adjustJSMParticipant">
              <div
                v-if="custom_participant.length !== 0"
                class="row q-py-sm q-px-sm q-mx-sm bg-indigo-1 cursor-pointer"
              >
                <span class="col">Participant</span>
                <span class="col">{{ custom_participant.join(', ') }}</span>
              </div>
              <div class="row q-py-sm q-px-sm q-mx-sm bg-indigo-1 cursor-pointer" v-else>
                <span class="col">Participant</span>
                <span class="col">None</span>
              </div>
            </section>
          </section>
          <q-separator class="q-mx-none q-pt-xs" color="red-2" inset />
          <section class="bg-orange-1 rounded-borders q-ma-sm">
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
              <section class="q-px-sm q-pb-sm col-12 bg-indigo-1">
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
                    :disabled="localNewComment === ''"
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
                <div class="col-8 self-center" v-html="comment.content"></div>
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
import { scroll, useQuasar } from 'quasar'

export default defineComponent({
  name: 'DHSDBAOTRSList',
  components: {},
  emits: ['triggerByJsmList'],
  props: {
    sn: Number,
    title: String,
    description: String,
    status: Boolean,
    comments: Object,
    attachments: Object,
    customerId: String,
    ticketNumber: Number,
    createTime: String,
    custom_category: Object,
    custom_handler: Object,
    custom_participant: Object,
    displayNameInclude: Boolean,
    expandedStatus: Boolean
  },
  setup(props, context) {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex

    const expanded = ref(false)
    const isShowDescription = ref(true)
    const isShowCommentEditor = ref(false)
    const localNewComment = ref('')
    const localJSMSet = reactive({
      isShowUpdateJSMDescriptionEdit: false,
      isShowUpdateJSMTime: false,
      isClickableAdjustJSMStatus: true,
      description: props.description,
      handler: props.custom_handler,
      participant: props.custom_participant,
      category: props.custom_category
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
      const targetId = ref(0)
      if (props.ticketNumber >= 92027180) {
        targetId.value = props.ticketNumber - 92000009
      } else if (props.ticketNumber >= 92022525) {
        targetId.value = props.ticketNumber - 91999956
      } else {
        targetId.value = props.ticketNumber - 91999952
      }
      window.open(
        `http://172.23.1.44/otrs/index.pl?Action=AgentTicketZoom;TicketID=${targetId.value}`,
        '_blank'
      )
      // window.open(props.issueUrl, '_blank')
    }

    function openNewPageToAddComment() {
      isShowCommentEditor.value = true
    }

    function commentBtnUpdate() {
      const postData = {
        editor: isLogin.value,
        targetSn: props.sn,
        targetTicketNumber: props.ticketNumber,
        comment: localNewComment.value
      }
      axios
        .post(
          `https://${ServiceDomainLocal}:9487/bpCowork/otrs/update/comments`,
          postData
        )
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
            const ele = document.getElementById('dbaOtrs' + props.sn)
            const target = getScrollTarget(ele)
            const offset = ele.offsetTop - 55
            const duration = 200
            setVerticalScrollPosition(target, offset, duration)
            context.emit('triggerByJsmList', {
              target: props.sn,
              issueId: props.ticketNumber
            })
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function commentBtnCancel() {
      isShowCommentEditor.value = false
      localNewComment.value = ''
      const ele = document.getElementById('dbaOtrs' + props.sn)
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - 55
      const duration = 200
      setVerticalScrollPosition(target, offset, duration)
    }

    // open the q-dialog popup-windows
    function adjustJSMDescription() {
      localJSMSet.isShowUpdateJSMDescriptionEdit = true
    }

    // description popup-window update to backend
    function localDescriptionUpdate() {
      const postData = reactive({
        targetSn: props.sn,
        targetTicketNumber: props.ticketNumber,
        target: 'description',
        newValue: localJSMSet.description,
        editor: isLogin.value
      })
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
        title: `Change YTS${props.ticketNumber} handler`,
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
          targetSn: props.sn,
          targetTicketNumber: props.ticketNumber,
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
        title: `Change YTS${props.ticketNumber} participant`,
        options: {
          type: 'checkbox',
          model: localJSMSet.participant,
          items: itemsSortOut.value
        },
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetSn: props.sn,
          targetTicketNumber: props.ticketNumber,
          target: 'participant',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'participant')
        // need this one to update local data
        localJSMSet.participant = data
      })
    }

    async function adjustJSMCategory() {
      // get option list by backend
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/bpCowork/jsm/query/field/customfield_10289/3`
      )
      // popup windows
      $q.dialog({
        title: `Change YTS${props.ticketNumber} category`,
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
          targetSn: props.sn,
          targetTicketNumber: props.ticketNumber,
          target: 'category',
          newValue: data,
          editor: isLogin.value
        })
        updateToJSM(postData, 'category')
        // need this one to update local data
        localJSMSet.category = data
      })
    }

    // running bar and notify here
    async function updateToJSM(payload, target) {
      const barRef = axiosExecuteBar.value
      barRef.start()
      await axios
        .post(
          `https://${ServiceDomainLocal}:9487/bpCowork/otrs/query/dba/update`,
          payload
        )
        .then((res) => {
          console.log(res)
          if (res.status === 200) {
            $q.notify({
              message: `<b>YTS${props.ticketNumber} ${target} has been updated!</b>`,
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
              issueId: props.ticketNumber
            })
          }
        })
        .catch((error) => {
          console.log(error)
          $q.notify({
            message: `YTS${props.ticketNumber} <b> ${target} update failed!</b>, open the developer tool to see the detail`,
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

    function closeTheOTRSTicket() {
      $q.dialog({
        title: 'Confirm',
        message: props.status
          ? 'Would you like to <b> close </b> this ticket?'
          : 'Would you like to open this ticket?',
        cancel: true,
        persistent: true,
        html: true
      }).onOk(() => {
        const postData = reactive({
          targetSn: props.sn,
          targetTicketNumber: props.ticketNumber,
          target: 'status',
          newValue: !props.status,
          editor: isLogin.value
        })
        updateToJSM(postData, 'status')
      })
    }

    watch(
      () => props.expandedStatus,
      (curValue, oldValue) => {
        expanded.value = curValue
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
      isShowDescription,
      isShowCommentEditor,
      localNewComment,
      commentBtnUpdate,
      commentBtnCancel,
      adjustJSMDescription,
      adjustJSMHandler,
      adjustJSMParticipant,
      adjustJSMCategory,
      axiosExecuteBar,
      localJSMSet,
      localDescriptionUpdate,
      localDescriptionCancel,
      paginationSet,
      isDisplayComment,
      expanded,
      closeTheOTRSTicket
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
