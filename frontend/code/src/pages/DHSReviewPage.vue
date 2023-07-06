<!-- @format -->
<template>
  <q-fab v-model="isShowFloatBtn" class="fixed-top-right q-mt-lg q-mr-lg" label-class="bg-grey-3 text-purple"
    color="purple" square vertical-actions-align="right" icon="keyboard_arrow_left" direction="left">
    <q-fab-action label-class="bg-grey-3 text-dark" external-label label-position="bottom" color="primary"
      @click.prevent="onClickEvent('next')" icon="skip_next" label="Next" square />
    <q-fab-action label-class="bg-grey-3 text-dark" external-label label-position="bottom" color="secondary"
      @click.prevent="onClickEvent('previous')" icon="skip_previous" label="Previous" square />
    <q-fab-action label-class="bg-grey-3 text-dark" external-label label-position="bottom" color="orange"
      @click.prevent="onClickEvent('opposite')" icon="airplay" :label="whichMode ? 'Brief' : 'Full'" square />
    <q-fab-action label-position="bottom" color="accent" :label="`${targetDate} ${targetShift}`" square />
  </q-fab>
  <q-fab v-model="isShowFileButton" class="fixed-bottom-right q-mb-lg q-mr-lg"
    :class="{ hidden: isShowFileButton !== true }" label-class="bg-grey-3 text-purple" color="teal" square
    vertical-actions-align="right" icon="keyboard_arrow_left" direction="left">
    <q-fab-action v-for="(item, index) in hyperList" :key="index" color="primary"
      @click.prevent="attachmentOpen(item[2])" :icon="defineAttachmentImage(item[1])"
      :label="'[' + item[3] + '] ' + item[0]" square />
    <q-fab-action label-position="top" color="teal" label="Attachments" square />
  </q-fab>

  <q-dialog v-model="isDisplayJsmDetail" full-width>
    <q-card>
      <div class="row" v-if="localJSMDict.defineSource[0] === 'rel'">
        <div class="col-1 q-pa-lg text-center"><q-btn size="md" icon="undo" name="undo"
            @click="popupJiraEvent(localJSMDict.defineSource, 'back')" /></div>
        <div @click="openNewPageToTicket"
          class="col-11 text-h5 text-bold self-center text-center text-blue-14 cursor-pointer ellipsis q-py-md">{{
              localJSMDict.title
          }}
        </div>
      </div>
      <div class="row" v-else>
        <div @click="openNewPageToTicket"
          class="col-12 text-h5 text-bold self-center text-center text-blue-14 cursor-pointer ellipsis q-py-md">{{
              localJSMDict.title
          }}
        </div>
      </div>

      <q-tabs v-model="tab" dense class="text-grey" active-color="primary" indicator-color="primary" align="justify"
        narrow-indicator>
        <q-tab no-caps name="mails" icon="mail" label="Original Mails Contents" />
        <q-tab no-caps name="allComments" icon="history" label="All Comments" @click.stop="callComments()" />
        <q-tab no-caps name="relations" label="Relations tickets" icon="share" @click.stop="callRelatedTicket()"
          :disable="localJSMDict.relatedTicketDefine" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="mails">
          <div v-html="localJSMDict.email_content"></div>
        </q-tab-panel>

        <q-tab-panel name="allComments">
          <DHSReviewPageComments v-if="isShowComments" :targetSn="localJSMDict.jsmSn"></DHSReviewPageComments>
        </q-tab-panel>

        <q-tab-panel name="relations">
          <div v-for="i in localJSMDict.relatedTicket" :key="i[0]">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label class="cursor-pointer text-blue-10" @click="popupJiraEvent(i, 'rel')">{{ i[1]
                  }}</q-item-label>
                </q-item-section>
                <q-item-section side top>
                  <q-item-label v-if="i[2] == 1" caption>Internal</q-item-label>
                  <q-item-label v-else caption>Mail</q-item-label>
                  <q-item-label>
                    <q-btn no-caps size="xs" class="q-mr-xs" v-if="i[2] == 2" outline color="orange-6"
                      label="Email Content">
                      <q-tooltip v-html="i[4]" anchor="top middle" self="bottom middle" :offset="[10, 10]">
                      </q-tooltip>
                    </q-btn>
                    <q-btn no-caps size="xs" outline color="orange-6" label="Description">
                      <q-tooltip v-html="i[3]" anchor="top middle" self="bottom middle" :offset="[10, 10]">
                      </q-tooltip>
                    </q-btn>
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-dialog>

  <section v-if="whichMode">
    <div class="row no-wrap items-center">
      <div id="reviewTitle" class="hidden">Full</div>
    </div>
    <div class="q-pa-md q-ma-md" v-html="wholeHtmlString"></div>
  </section>
  <section v-else>
    <h3 id="reviewTitle" class="q-mx-md">
      [{{ targetDate }} {{ targetShift }}] YiTMH Operation Handover
    </h3>
    <!-- NOTE CARD Start -->
    <div v-for="(item, index) in wholeHtmlString[0]" :key="index">
      <!-- New Note, Created by, Start -->
      <q-card v-if="item.update_summary === 'New'" flat bordered class="q-ma-md noteCustBorder">
        <q-card-section class="bg-grey-2">
          <div class="row items-center" v-if="item.check_image !== 0">
            <div class="col-6">
              <span class="text-subtitle1 text-bold bg-yellow-6 q-pa-xs">Created by {{ item.update_by }}</span>
              <span class="text-subtitle1 text-bold text-red-6">
                Note {{ item.sequence }} - {{ item.customer }}</span>
            </div>
            <div class="col-6 text-right q-gutter-x-sm">
              <span v-for="(buttonItem, buttonIndex) in wholeHtmlString[2]" :key="buttonIndex">
                <q-btn :label="buttonItem[0]" :icon="defineAttachmentImage(buttonItem[1])"
                  @click="attachmentOpen(buttonItem[2])" v-if="buttonItem[3] === item.sn" no-caps></q-btn>
              </span>
            </div>
          </div>
          <div v-else class="row">
            <div class="col-12">
              <span class="text-subtitle1 text-bold bg-yellow-6 q-pa-xs">Created by {{ item.update_by }}</span>
              <span class="text-h6 text-red-6">Note {{ item.sequence }} - {{ item.customer }}</span>
            </div>
          </div>
        </q-card-section>
        <q-separator dark inset />
        <q-card-section>
          <div v-html="item.summary"></div>
        </q-card-section>
      </q-card>
      <!-- New Note, Created by, End -->
      <!-- Update Note, Start -->
      <q-card v-else-if="item.update_summary && item.update_by" flat bordered class="q-ma-md">
        <q-card-section class="bg-grey-2">
          <div class="row items-center" v-if="item.check_image !== 0">
            <div class="col-6">
              <span class="text-subtitle1 text-bold text-red-6">Note {{ item.sequence }} - {{ item.customer }}</span>
            </div>
            <div class="col-6 text-right q-gutter-x-sm">
              <span v-for="(buttonItem, buttonIndex) in wholeHtmlString[2]" :key="buttonIndex">
                <q-btn :label="buttonItem[0]" :icon="defineAttachmentImage(buttonItem[1])"
                  @click="attachmentOpen(buttonItem[2])" v-if="buttonItem[3] === item.sn" no-caps></q-btn>
              </span>
            </div>
          </div>
          <div v-else class="row">
            <div class="col-12">
              <span class="text-subtitle1 text-bold text-red-6">Note {{ item.sequence }} - {{ item.customer }}</span>
            </div>
          </div>
        </q-card-section>
        <section class="q-py-md">
          <q-card-section v-if="item.summary" class="q-py-none">
            <div v-html="item.summary"></div>
          </q-card-section>
          <q-card-section class="q-py-none">
            <span class="text-subtitle1 text-bold bg-yellow-6 q-pa-xs q-mr-xs">Update by {{ item.update_by }}</span>
            <span v-html="item.update_summary"></span>
          </q-card-section>
        </section>
      </q-card>
      <!-- Update Note, End -->
    </div>
    <!-- NOTE CARD End -->
    <!-- OTRS CARD START -->
    <div v-for="(item, index) in wholeHtmlString[1]" :key="index">
      <!-- New Ticket, Handled by, Start -->
      <q-card v-if="item.update_summary === 'New'" flat bordered class="q-ma-md">
        <q-card-section class="bg-grey-2">
          <div class="row">
            <div class="col-12">
              <span class="text-subtitle1 text-bold bg-yellow-6 q-pa-xs">Handle by {{ item.update_by }}</span>
              <span class="text-subtitle1 text-bold text-red q-pl-xs">{{ item.customer }} -
              </span>
              <span class="text-subtitle1 text-bold text-blue-14 cursor-pointer"
                @click="otrsOpenToNewPage(item.number)">YTS{{ item.number }} - {{ item.subject }}</span>
            </div>
          </div>
        </q-card-section>
        <q-separator dark inset />
        <q-card-section>
          <div v-html="item.summary"></div>
        </q-card-section>
      </q-card>
      <!-- New Ticket, Handled by, End -->
      <q-card v-else-if="item.update_summary && item.update_by" flat bordered class="q-ma-md">
        <q-card-section class="bg-grey-2">
          <div class="row">
            <div class="col-12">
              <span class="text-subtitle1 text-bold text-red">{{ item.customer }} -
              </span>
              <span class="text-subtitle1 text-bold text-blue-14 cursor-pointer"
                @click="otrsOpenToNewPage(item.number)">YTS{{ item.number }} - {{ item.subject }}</span>
            </div>
          </div>
        </q-card-section>
        <section class="q-py-md">
          <q-card-section v-if="item.summary" class="q-py-none">
            <div v-html="item.summary"></div>
          </q-card-section>
          <q-card-section class="q-py-none">
            <span class="text-subtitle1 text-bold bg-yellow-6 q-pa-xs q-mr-xs">Update by {{ item.update_by }}</span>
            <span v-html="item.update_summary"></span>
          </q-card-section>
        </section>
      </q-card>
    </div>
    <!-- OTRS CARD End -->
    <!-- JIRA CARD Start -->
    <div v-for="(item, index) in wholeHtmlString[4]" :key="index">
      <q-card flat bordered class="q-ma-md">
        <q-card-section class="bg-grey-2">
          <div class="row justify-between items-center">
            <span @click="popupJiraEvent(item, 'main')" class="text-subtitle1 text-bold text-blue-14 cursor-pointer">{{
                item[0]
            }}</span>
            <span>
              <q-chip square v-if="item[5]">
                {{ item[5] }}
              </q-chip>
              <q-chip :color="returnJiraContext('color', item[2])" text-color="dark" square class="text-right">
                {{ returnJiraContext('str', item[2]) }}
              </q-chip>
            </span>
          </div>
        </q-card-section>
        <q-separator dark inset />
        <q-card-section>
          <div v-html="item[1]"></div>
        </q-card-section>
        <q-separator class="q-mx-none" inset />
        <div class="q-py-sm">
          <q-list class="q-pa-none" v-for="(commentValue, commentIndex) in item[3]" :key="commentIndex">
            <q-item v-if="commentValue.commentType === 2">
              <q-item-section>
                <q-item-label caption>Update by {{ commentValue.handler }}</q-item-label>
                <q-item-label v-html="commentValue.content"></q-item-label>
              </q-item-section>

              <q-item-section side top>
                <q-item-label caption>{{ commentValue.timestamp }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </div>
      </q-card>
    </div>
    <!-- JIRA CARD End -->
    <div v-for="(item, index) in wholeHtmlString[3]" :key="index">
      <q-list flat bordered class="rounded-borders q-ma-md">
        <q-expansion-item expand-separator icon="compare" :label="`${item.source}${item.target}`"
          :caption="item.lastEditor">
          <q-card class="row q-pa-md custWordBreak">
            <q-card-section class="col-4 column">
              <div class="text-center bg-blue-grey-2 text-bold q-mx-xs">
                {{ item.oldDateShift }}
              </div>
              <div class="q-mx-md" v-html="item.oldContent"></div>
            </q-card-section>
            <q-card-section class="col-4 column">
              <div class="text-center bg-blue-grey-2 text-bold q-mx-xs">
                {{ item.curDateShift }}
              </div>
              <div class="q-mx-md" v-html="item.curContent"></div>
            </q-card-section>
            <q-card-section class="col-4 column">
              <div class="text-center bg-blue-grey-2 text-bold">Show the diff</div>
              <div class="q-mx-md" v-html="item.diffHtml"></div>
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </q-list>
    </div>
  </section>
</template>
<script>
import DHSReviewPageComments from 'components/DHSReviewPageComments.vue'

import { defineComponent, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'
import { date, scroll, useMeta } from 'quasar'
// import _ from 'lodash'

const metaData = {
  // sets document title
  title: 'NDHS - Review Page',
  titleTemplate: (title) => `${title}`
}

export default defineComponent({
  name: 'DHSReviewPage',
  components: { DHSReviewPageComments },
  setup() {
    useMeta(metaData)
    // store the result here
    const wholeHtmlString = ref('')
    // control float button display or not
    const isShowFloatBtn = ref(true)
    // change the mode for full(true) or Brief(false)
    const whichMode = ref(false)
    // store attachment hyperlink
    const hyperList = ref()
    // display attachment or not
    const isShowFileButton = ref(false)
    // popup vodel for JSM popup windows
    const isDisplayJsmDetail = ref(false)
    const tab = ref('mails')
    // control the component for comments
    const isShowComments = ref(false)
    // get router path data
    const router = useRouter()
    const targetDate = ref(router.currentRoute.value.params._date)
    const targetShift = ref(router.currentRoute.value.params._shift)
    // dynamic domain
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain
    // popup jsm detail dict
    const localJSMDict = reactive({
      title: '',
      email_content: '',
      jsmSn: '',
      issueUrl: '',
      relatedTicket: [],
      relatedTicketDefine: true,
      defineSource: 'main'
    })
    // scroll
    const { getScrollTarget, setVerticalScrollPosition } = scroll
    // get data from backend by axios
    axios
      .get(
        `https://${ServiceDomainLocal}:9487/bpEmail/exportword/${targetDate.value}/${targetShift.value}/reviewB`
      )
      .then((response) => {
        wholeHtmlString.value = response.data
      })
      .catch((error) => {
        console.log(error)
      })

    function onClickEvent(action) {
      const splitTimeArray = ref()
      const timeObject = ref()
      if (action === '?') {
        alert('what do you want?')
      } else if (action === 'previous') {
        if (targetShift.value === 'M') {
          // split by "-"
          splitTimeArray.value = targetDate.value.split('-')
          // string to TimeObject
          timeObject.value = date.buildDate({
            year: splitTimeArray.value[0],
            month: splitTimeArray.value[1],
            date: splitTimeArray.value[2]
          })
          // TimeObject subtract 1 Day
          timeObject.value = date.subtractFromDate(timeObject.value, { days: 1 })
          // TimeObject to String
          targetDate.value = date.formatDate(timeObject.value, 'YYYY-MM-DD')
          targetShift.value = 'N'
        } else if (targetShift.value === 'A') {
          targetShift.value = 'M'
        } else if (targetShift.value === 'N') {
          targetShift.value = 'A'
        }
      } else if (action === 'next') {
        if (targetShift.value === 'N') {
          // split by "-"
          splitTimeArray.value = targetDate.value.split('-')
          // string to TimeObject
          timeObject.value = date.buildDate({
            year: splitTimeArray.value[0],
            month: splitTimeArray.value[1],
            date: splitTimeArray.value[2]
          })
          // TimeObject add 1 Day
          timeObject.value = date.addToDate(timeObject.value, { days: 1 })
          // TimeObject to String
          targetDate.value = date.formatDate(timeObject.value, 'YYYY-MM-DD')
          targetShift.value = 'M'
        } else if (targetShift.value === 'M') {
          targetShift.value = 'A'
        } else if (targetShift.value === 'A') {
          targetShift.value = 'N'
        }
      } else if (action === 'opposite') {
        whichMode.value = !whichMode.value
      }
      callHistory()
    }

    // click attachment button and open new page to see the attachment
    function attachmentOpen(attachmentSn) {
      window.open(
        `https://${ServiceDomainLocal}:9487/bpNote/attachment/get/${attachmentSn}`,
        '_blank'
      )
      isShowFileButton.value = true
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

    async function callHistory() {
      const tmpUrl = ref('')
      if (whichMode.value) {
        tmpUrl.value = `https://${ServiceDomainLocal}:9487/bpEmail/exportword/${targetDate.value}/${targetShift.value}/reviewF`
      } else {
        tmpUrl.value = `https://${ServiceDomainLocal}:9487/bpEmail/exportword/${targetDate.value}/${targetShift.value}/reviewB`
      }
      await axios
        .get(tmpUrl.value)
        .then((response) => {
          if (whichMode.value) {
            wholeHtmlString.value = response.data[0]
            isShowFloatBtn.value = true
            if (response.data[1]) {
              alert('this shift has attachment log')
              isShowFileButton.value = true
              hyperList.value = response.data[2]
              console.log(response.data[2])
            } else {
              isShowFileButton.value = false
            }
          } else {
            isShowFileButton.value = false
            isShowFloatBtn.value = true // popup the button
            wholeHtmlString.value = response.data
          }
        })
        .catch((error) => {
          console.log(error)
        })
      // scroll
      const ele = document.getElementById('reviewTitle')
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - ele.scrollHeight
      const duration = 350
      setVerticalScrollPosition(target, offset, duration)
    }

    async function callRelatedTicket() {
      // clear the value
      localJSMDict.relatedTicket = []
      const res = await axios.get(`https://${ServiceDomainLocal}:9487/bpOTRS/jsm/get/related/${localJSMDict.jsmSn}`)
      localJSMDict.relatedTicket = res.data
    }

    function defineAttachmentImage(fileType) {
      switch (fileType) {
        case 'docx':
          return 'far fa-file-word'
        case 'xlsx':
        case 'csv':
          return 'far fa-file-excel'
        case 'pptx':
          return 'far fa-file-powerpoint'
        case 'txt':
          return 'text_snippet'
        case 'pdf':
          return 'far fa-file-pdf'
        case 'rar':
        case 'zip':
          return 'far fa-file-archive'
        default:
          return 'image'
      }
    }

    function returnJiraContext(currentType, ticketStatus) {
      switch (ticketStatus) {
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

    async function popupJiraEvent(cObject, source) {
      console.log(source)
      // get current target sn
      const targetTicketUrl = ref('')
      if (source === 'main') {
        tab.value = 'mails'
        localJSMDict.defineSource = ['main', cObject[4], cObject[0]]
        localJSMDict.title = cObject[0]
        targetTicketUrl.value = `https://${ServiceDomainLocal}:9487/bpCowork/query/opsdb/${cObject[4]}`
      } else if (source === 'rel') {
        tab.value = 'mails'
        localJSMDict.defineSource[0] = 'rel'
        localJSMDict.title = cObject[1]
        targetTicketUrl.value = `https://${ServiceDomainLocal}:9487/bpCowork/query/opsdb/${cObject[0]}`
      } else {
        // let user keep see the relate ticket sub page
        tab.value = 'relations'
        localJSMDict.defineSource[0] = 'main'
        localJSMDict.title = cObject[2]
        targetTicketUrl.value = `https://${ServiceDomainLocal}:9487/bpCowork/query/opsdb/${cObject[1]}`
      }
      await axios
        .get(targetTicketUrl.value)
        .then((response) => {
          // display popup window
          isDisplayJsmDetail.value = true
          localJSMDict.issueUrl = response.data.issueUrl

          localJSMDict.jsmSn = response.data.sn
          if (response.data.content_html) {
            localJSMDict.email_content = response.data.content_html
          }
          if (source !== 'rel') {
            console.log(response.data.relations)
            if (response.data.relations) {
              localJSMDict.relatedTicketDefine = false
            } else {
              localJSMDict.relatedTicketDefine = true
            }
          } else {
            localJSMDict.relatedTicketDefine = true
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function callComments() {
      isShowComments.value = true
    }

    function openNewPageToTicket() {
      window.open(localJSMDict.issueUrl, '_blank')
    }

    watch(
      () => isShowFileButton.value,
      (curValue, oldValue) => {
        console.log('isShowFileButton change')
        console.log(curValue)
        console.log(oldValue)
      }
    )

    return {
      targetDate,
      targetShift,
      wholeHtmlString,
      isShowFloatBtn,
      onClickEvent,
      whichMode,
      isShowFileButton,
      hyperList,
      attachmentOpen,
      otrsOpenToNewPage,
      defineAttachmentImage,
      returnJiraContext,
      popupJiraEvent,
      isDisplayJsmDetail,
      tab,
      splitterModel: ref(10),
      localJSMDict,
      callComments,
      isShowComments,
      openNewPageToTicket,
      callRelatedTicket
    }
  }
})
</script>

<style lang="scss" scoped>
div.q-card.q-card--bordered {
  border-color: black !important;
}
</style>
