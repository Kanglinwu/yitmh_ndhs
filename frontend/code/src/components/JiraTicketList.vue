<!-- @format -->

<template>
  <div v-show="isDisplay" class="q-px-md q-pt-md q-pb-none row q-gutter-sm">
    <!-- ticket under editing -->
    <q-dialog
      v-model="dialogUnderEditing"
      persistent
      transition-show="scale"
      transition-hide="scale"
    >
      <q-card class="bg-teal text-white" style="width: 300px">
        <q-card-section>
          <div class="text-h6">
            Ticket is under editing by {{ localResSet.localLockedBy }}
          </div>
        </q-card-section>
        <!-- <q-card-section class="q-pt-none"> Click/Tap on the backdrop. </q-card-section> -->
        <q-card-actions align="right" class="bg-white text-teal">
          <q-btn flat label="Close" v-close-popup />
          <q-btn @click="robTheTicket(ticketSn)" flat label="Rob" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <!-- Ticket card start -->
    <q-card :id="issueId" flat bordered class="my-card col-12">
      <q-card-section>
        <div
          class="row justify-between items-center"
          :class="[flagUnderEdit ? 'text-italic text-grey-6' : 'text-bold']"
        >
          <div v-if="flagUnderEdit" class="text-h6 col-md-10">
            <span class="text-bold text-red-8">(Lock by {{ editorBy }})</span>{{ name }}
          </div>
          <div v-else class="text-h6 col-md-10 row">
            <q-icon
              v-if="flagTicketStatus === 0 && localResSet.localSummary === 'New ticket'"
              name="new_releases"
              class="text-red-3"
            />{{ name }}
          </div>
          <div class="col-md-2 column items-end">
            <q-chip
              clickable
              icon="open_in_new"
              color="primary"
              text-color="white"
              square
              class="text-right"
              @click="gotoJiraTicket(url)"
            >
              {{ sn }}
            </q-chip>
            <q-chip
              :color="returnCorrectColor(flagJiraTicketStatus)"
              text-color="dark"
              square
              class="text-right"
              clickable
              @click="jiraStatusSelector(flagJiraTicketStatus)"
            >
              {{ flagJiraTicketStatus }}
              <q-tooltip transition-show="rotate" transition-hide="rotate">
                issueId = {{ issueId }}, DBSN = {{ ticketSn }}
              </q-tooltip>
            </q-chip>
          </div>
        </div>
      </q-card-section>
      <q-tabs align="left" v-model="tab" class="text-teal">
        <q-tab label="Handover" name="one">
          <q-badge v-if="attachmentList.length !== 0" color="red" floating>{{
            attachmentList.length
          }}</q-badge>
        </q-tab>
        <q-tab @click.stop="callJiraComment(issueId)" label="Jira comment" name="two" />

        <q-tab
          @click.stop="callJiraAttachment(issueId)"
          label="Jira attachment"
          name="three"
        />
        <q-tab label="KPI" name="four" @click.stop="callKpi(flagKpiSn)">
          <q-badge v-if="flagKpiSn" floating rounded color="red" />
        </q-tab>
      </q-tabs>
      <q-separator inset />
      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="four">
          <div v-if="Object.keys(localKpiTemplate).length !== 0">
            <q-card bordered class="bg-pink-2">
              <!-- 1 -->
              <span v-if="localKpiTemplate.type === '1'">
                <q-item>
                  <q-item-section>
                    <q-item-label>Regular Operation</q-item-label>
                    <q-item-label caption lines="2">
                      <div>Handler: {{ localKpiTemplate.handler }}</div>
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side top>
                    <q-item-label class="text-red-5 text-bold" caption>
                      {{ localKpiTemplate.related_date }}
                      {{ localKpiTemplate.related_shift }}</q-item-label
                    >
                  </q-item-section>
                </q-item>
                <q-separator dark inset />
              </span>
              <!-- 2 -->
              <span v-if="localKpiTemplate.type === '2'">
                <q-item>
                  <q-item-section>
                    <q-item-label>Troubleshooting</q-item-label>
                    <q-item-label caption lines="5">
                      <div>Handler: {{ localKpiTemplate.handler }}</div>
                      <div>Handler(deputy): {{ localKpiTemplate.handler_second }}</div>
                      <div>Participant(s): {{ localKpiTemplate.participant }}</div>
                      <div>Solved?: {{ localKpiTemplate.resolve_status }}</div>
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side top>
                    <q-item-label class="text-red-5 text-bold" caption>
                      {{ localKpiTemplate.related_date }}
                      {{ localKpiTemplate.related_shift }}</q-item-label
                    >
                  </q-item-section>
                </q-item>
                <q-separator dark inset />
              </span>
              <!-- 3 -->
              <span v-if="localKpiTemplate.type === '3'">
                <q-item>
                  <q-item-section>
                    <q-item-label>Advanced Troubleshooting</q-item-label>
                    <q-item-label caption lines="10">
                      <div>Handler: {{ localKpiTemplate.handler }}</div>
                      <div>Handler(deputy): {{ localKpiTemplate.handler_second }}</div>
                      <div>Participant(s): {{ localKpiTemplate.participant }}</div>
                      <div>Solved?: {{ localKpiTemplate.resolve_status }}</div>
                      <div>Post-mortem:</div>
                      <img
                        @click="
                          popupKpiFile(
                            localKpiTemplate.related_date,
                            localKpiTemplate.related_shift,
                            localKpiTemplate.related_sn,
                            localKpiTemplate.file_path
                          )
                        "
                        class="rounded-borders cursor-pointer"
                        :src="
                          'https://' +
                          ServiceDomainLocal +
                          ':9487/review/kpi/' +
                          localKpiTemplate.related_date +
                          '/' +
                          localKpiTemplate.related_shift +
                          '/jira/' +
                          localKpiTemplate.related_sn +
                          '/' +
                          localKpiTemplate.file_path
                        "
                        style="height: 50px; max-width: 50px"
                      />
                      <div>
                        Description:
                        <div v-html="localKpiTemplate.description"></div>
                      </div>
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side top>
                    <q-item-label class="text-red-5 text-bold" caption>
                      {{ localKpiTemplate.related_date }}
                      {{ localKpiTemplate.related_shift }}</q-item-label
                    >
                  </q-item-section>
                </q-item>
                <q-separator dark inset />
              </span>
            </q-card>
            <q-separator spaced inset />
            <div class="row q-gutter-sm">
              <q-btn
                color="white"
                text-color="primary"
                label="history record"
                @click="callKpiHistory(issueId)"
              />
              <q-btn
                color="white"
                text-color="primary"
                label="Current points"
                @click="sortOutKpiResult"
              />
            </div>
            <div v-for="(item, index) in localKpiHistoryTemplate" :key="index">
              <q-separator spaced inset />
              <q-card bordered class="bg-pink-2">
                <!-- 1 -->
                <span v-if="item.type === '1'">
                  <q-item>
                    <q-item-section>
                      <q-item-label>Regular Operation</q-item-label>
                      <q-item-label caption lines="2">
                        <div>Handler: {{ item.handler }}</div>
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side top>
                      <q-item-label class="text-red-5 text-bold" caption>
                        {{ item.related_date }}
                        {{ item.related_shift }}</q-item-label
                      >
                    </q-item-section>
                  </q-item>
                  <q-separator dark inset />
                </span>
                <!-- 2 -->
                <span v-if="item.type === '2'">
                  <q-item>
                    <q-item-section>
                      <q-item-label>Troubleshooting</q-item-label>
                      <q-item-label caption lines="5">
                        <div>Handler: {{ item.handler }}</div>
                        <div>Handler(deputy): {{ item.handler_second }}</div>
                        <div>Participant(s): {{ item.participant }}</div>
                        <div>Solved?: {{ item.resolve_status }}</div>
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side top>
                      <q-item-label class="text-red-5 text-bold" caption>
                        {{ item.related_date }}
                        {{ item.related_shift }}</q-item-label
                      >
                    </q-item-section>
                  </q-item>
                  <q-separator dark inset />
                </span>
                <!-- 3 -->
                <span v-if="item.type === '3'">
                  <q-item>
                    <q-item-section>
                      <q-item-label>Advanced Troubleshooting</q-item-label>
                      <q-item-label caption lines="10">
                        <div>Handler: {{ item.handler }}</div>
                        <div>Handler(deputy): {{ item.handler_second }}</div>
                        <div>Participant(s): {{ item.participant }}</div>
                        <div>Solved?: {{ item.resolve_status }}</div>
                        <div>Post-mortem:</div>
                        <img
                          @click="
                            popupKpiFile(
                              item.related_date,
                              item.related_shift,
                              item.related_sn,
                              item.file_path
                            )
                          "
                          class="rounded-borders cursor-pointer"
                          :src="
                            'https://' +
                            ServiceDomainLocal +
                            ':9487/review/kpi/' +
                            item.related_date +
                            '/' +
                            item.related_shift +
                            '/jira/' +
                            item.related_sn +
                            '/' +
                            item.file_path
                          "
                          style="height: 50px; max-width: 50px"
                        />
                        <div>
                          Description:
                          <div v-html="item.description"></div>
                        </div>
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side top>
                      <q-item-label class="text-red-5 text-bold" caption>
                        {{ item.related_date }}
                        {{ item.related_shift }}</q-item-label
                      >
                    </q-item-section>
                  </q-item>
                  <q-separator dark inset />
                </span>
              </q-card>
            </div>
          </div>
          <div v-else>
            <q-card bordered class="bg-pink-2">
              <q-item>
                <q-item-section>
                  <q-item-label>No KPI record today</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-icon name="fas fa-skull" color="dark" />
                </q-item-section>
              </q-item>
              <q-separator dark inset />
            </q-card>
            <q-separator spaced inset />
            <div class="row q-gutter-sm">
              <q-btn
                color="white"
                text-color="primary"
                label="history record"
                @click="callKpiHistory(issueId)"
              />
              <q-btn
                color="white"
                text-color="primary"
                label="Current points"
                @click="sortOutKpiResult"
              />
            </div>
            <div v-for="(item, index) in localKpiHistoryTemplate" :key="index">
              <q-separator spaced inset />
              <q-card bordered class="bg-pink-2">
                <!-- 1 -->
                <span v-if="item.type === '1'">
                  <q-item>
                    <q-item-section>
                      <q-item-label>Regular Operation</q-item-label>
                      <q-item-label caption lines="2">
                        <div>Handler: {{ item.handler }}</div>
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side top>
                      <q-item-label class="text-red-5 text-bold" caption>
                        {{ item.related_date }}
                        {{ item.related_shift }}</q-item-label
                      >
                    </q-item-section>
                  </q-item>
                  <q-separator dark inset />
                </span>
                <!-- 2 -->
                <span v-if="item.type === '2'">
                  <q-item>
                    <q-item-section>
                      <q-item-label>Troubleshooting</q-item-label>
                      <q-item-label caption lines="5">
                        <div>Handler: {{ item.handler }}</div>
                        <div>Handler(deputy): {{ item.handler_second }}</div>
                        <div>Participant(s): {{ item.participant }}</div>
                        <div>Solved?: {{ item.resolve_status }}</div>
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side top>
                      <q-item-label class="text-red-5 text-bold" caption>
                        {{ item.related_date }}
                        {{ item.related_shift }}</q-item-label
                      >
                    </q-item-section>
                  </q-item>
                  <q-separator dark inset />
                </span>
                <!-- 3 -->
                <span v-if="item.type === '3'">
                  <q-item>
                    <q-item-section>
                      <q-item-label>Advanced Troubleshooting</q-item-label>
                      <q-item-label caption lines="10">
                        <div>Handler: {{ item.handler }}</div>
                        <div>Handler(deputy): {{ item.handler_second }}</div>
                        <div>Participant(s): {{ item.participant }}</div>
                        <div>Solved?: {{ item.resolve_status }}</div>
                        <div>Post-mortem:</div>
                        <img
                          @click="
                            popupKpiFile(
                              item.related_date,
                              item.related_shift,
                              item.related_sn,
                              item.file_path
                            )
                          "
                          class="rounded-borders cursor-pointer"
                          :src="
                            'https://' +
                            ServiceDomainLocal +
                            ':9487/review/kpi/' +
                            item.related_date +
                            '/' +
                            item.related_shift +
                            '/jira/' +
                            item.related_sn +
                            '/' +
                            item.file_path
                          "
                          style="height: 50px; max-width: 50px"
                        />
                        <div>
                          Description:
                          <div v-html="item.description"></div>
                        </div>
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side top>
                      <q-item-label class="text-red-5 text-bold" caption>
                        {{ item.related_date }}
                        {{ item.related_shift }}</q-item-label
                      >
                    </q-item-section>
                  </q-item>
                  <q-separator dark inset />
                </span>
              </q-card>
            </div>
          </div>
        </q-tab-panel>
        <q-tab-panel name="three">
          <div v-if="defaultJiraTicketAttachment.length != 0">
            <div
              v-for="(item, index) in defaultJiraTicketAttachment.slice().reverse()"
              :key="index"
            >
              <div class="bg-purple-1">
                <div class="bg-red-3 q-pa-xs">
                  <span class="text-white">Comment-{{ index + 1 }}</span> |
                  <span class="text-white">Created by {{ item.who }}</span> |
                  <span class="text-white">Created at {{ item.when }}</span>
                </div>
                <img
                  v-if="item._type.includes('jpg') || item._type.includes('png')"
                  class="q-pa-md"
                  :src="item.attchmentBody"
                  alt=""
                />
                <div v-else class="q-pa-md">
                  <span class="material-icons"> file_download </span>
                  <a :href="item.attchmentBody">{{ item.attchmentName }}</a>
                </div>
              </div>
            </div>
          </div>
          <div v-else>
            <div v-if="!loadingIcon">
              <q-spinner-pie size="xl" color="red-3" />
            </div>
            <div v-else>
              <div v-html="loadingIcon"></div>
            </div>
          </div>
        </q-tab-panel>
        <q-tab-panel name="two">
          <div v-if="defaultJiraTicketComment.length != 0">
            <div
              v-for="(item, index) in defaultJiraTicketComment.slice().reverse()"
              :key="index"
            >
              <div class="bg-purple-1">
                <div class="bg-red-3 q-pa-xs">
                  <span class="text-white">Comment-{{ index + 1 }}</span> |
                  <span class="text-white">Created by {{ item.who }}</span> |
                  <span class="text-white">Created at {{ item.when }}</span>
                </div>
                <div class="q-pa-xs" v-html="item.commentBody"></div>
                <!-- <div class="q-pa-xs">{{ item.commentBody }}</div> -->
              </div>
            </div>
          </div>
          <div v-else>
            <div v-if="!loadingIcon">
              <q-spinner-pie size="xl" color="red-3" />
            </div>
            <div v-else>
              <div v-html="loadingIcon"></div>
            </div>
          </div>
        </q-tab-panel>
        <q-tab-panel name="one">
          <div v-show="localResSet.localEditorStatus">
            <div class="custom-border-display jira q-py-md rounded-borders">
              <div
                v-if="
                  flagTicketStatus === 0 &&
                  editorBy &&
                  localResSet.localSummary != 'New ticket'
                "
              >
                <div class="bg-yellow-3 q-px-md text-bold">Update by {{ editorBy }}</div>
                <div class="q-px-md" v-html="localResSet.localSummary"></div>
              </div>
              <div v-else>
                <div class="bg-yellow-1 q-px-md text-bold">Current status</div>
                <div class="q-px-md" v-html="localResSet.localSummary"></div>
              </div>
              <div
                v-if="flagTicketStatus != 0 && editorBy && localResSet.localUpdateSummary"
              >
                <div class="bg-yellow-3 q-px-md text-bold">Update by {{ editorBy }}</div>
                <div class="q-px-md" v-html="localResSet.localUpdateSummary"></div>
              </div>
              <div v-if="attachmentList.length !== 0">
                <div class="bg-yellow-3 q-px-md q-mt-md q-mb-sm text-italic">
                  Following attachment(s) will be sent on this shift
                </div>
                <div class="flex q-px-md q-gutter-xs">
                  <div
                    v-for="(value, idx) in attachmentList"
                    :key="idx"
                    :class="
                      value._type !== 'png' && value._type !== 'jpg'
                        ? 'order-last'
                        : 'order-first'
                    "
                  >
                    <div
                      v-if="value._type !== 'png' && value._type !== 'jpg'"
                      class="cursor-pointer text-subtitle2 bg-blue-grey-2 q-pa-xs rounded-borders"
                      @click.self="popuptheattachment(value.name, ticketSn)"
                    >
                      <q-avatar rounded>
                        <img
                          :src="
                            'https://' +
                            ServiceDomainLocal +
                            ':9487/document/' +
                            value._type +
                            '/' +
                            ticketSn +
                            '/' +
                            value.name
                          "
                        />
                      </q-avatar>
                      {{ value.name }}
                    </div>
                    <div v-else>
                      <img
                        v-on:mouseleave="adjustTheAvatarSize('out', idx, $event)"
                        v-on:mouseenter="adjustTheAvatarSize('in', idx, $event)"
                        @click.self="popuptheattachment(value.name, ticketSn)"
                        class="cursor-pointer"
                        :style="avatarSize[idx]"
                        :src="
                          'https://' +
                          ServiceDomainLocal +
                          ':9487/document/' +
                          value._type +
                          '/' +
                          ticketSn +
                          '/' +
                          value.name
                        "
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="row q-pt-sm q-gutter-sm text-right">
              <q-btn
                color="white"
                text-color="primary"
                label="Edit"
                @click="reverseStatus(ticketSn, 'edit')"
              />
              <q-btn
                color="white"
                text-color="primary"
                label="Delete"
                @click="reverseStatus(ticketSn, 'delete')"
                :disabled="flagJiraTicketStatus !== 'Closed'"
              />
            </div>
          </div>
          <div v-show="!localResSet.localEditorStatus">
            <div class="row items-center">
              <div class="col-1 text-left">Current Status:</div>
              <q-editor
                class="col-11"
                v-model="localResSet.localSummary"
                ref="targetRef"
                :toolbar="summaryToolBar"
                @click="checkSummaryZone"
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
                              <q-item v-for="n in i.value" :key="n.name" dense clickable>
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
            </div>
            <div v-if="flagTicketStatus != 0">
              <div class="row items-center">
                <div class="col-1 text-left">Update Status:</div>
                <q-editor
                  class="col-11"
                  v-model="localResSet.localUpdateSummary"
                  ref="targetRef2"
                  :toolbar="updateSummaryToolBar"
                  @click="checkUpdateSummaryZone"
                >
                  <template v-slot:token>
                    <q-btn-dropdown
                      dense
                      split
                      unelevated
                      padding="xs"
                      fab-mini
                      flat
                      ref="q2BtnDropDownColor"
                      icon="format_color_text"
                      v-bind:text-color="
                        foreColor ? ConvertforeColor('fore') : ConvertforeColor('fore')
                      "
                      @click="adjustUpdateSummaryColor('foreColor', foreColor)"
                    >
                      <q-list dense>
                        <q-item
                          tag="label"
                          clickable
                          @click="adjustUpdateSummaryColor('foreColor', foreColor)"
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
                      ref="q2BtnDropDownBGColor"
                      icon="font_download"
                      v-bind:text-color="
                        backColor ? ConvertforeColor('back') : ConvertforeColor('back')
                      "
                      @click="adjustUpdateSummaryColor('backColor', backColor)"
                      push
                    >
                      <q-list dense>
                        <q-item
                          tag="label"
                          clickable
                          @click="adjustUpdateSummaryColor('backColor', backColor)"
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
                                    @click="updateValueToUpdateSummary(n)"
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
              </div>
            </div>
            <div class="row">
              <div class="col">
                <q-option-group
                  class="q-pt-md"
                  v-model="group"
                  :options="options"
                  inline
                  :color="options.color"
                  type="toggle"
                />
              </div>
              <div class="col q-gutter-xs q-pt-md text-right">
                <span @mouseover.stop="notifyKpiAlert">
                  <q-tooltip
                    class="bg-pink-2 text-black"
                    anchor="top middle"
                    self="bottom middle"
                    :delay="100"
                    :offset="[10, 10]"
                    v-if="flagKpiSn === null"
                  >
                    Miss KPI Update!
                  </q-tooltip>
                  <q-btn
                    class="q-mt-xs q-ml-xs"
                    color="white"
                    text-color="primary"
                    label="Update"
                    :disable="flagKpiSn === null"
                    @click="hiddenAndUpdateEditor(ticketSn)"
                  >
                  </q-btn>
                </span>
                <q-btn
                  color="white"
                  text-color="primary"
                  label="Cancel"
                  @click="hiddenAndCancelEditor(ticketSn)"
                />
              </div>
            </div>
            <div class="q-mt-md">
              <div v-show="options[0]['status']" class="column bg-pink-1 q-px-md q-pb-md">
                <div class="col-12 text-center q-pa-md text-bold">KPI zone</div>
                <JiraTicketListKpi
                  :jiraIssueId="ticketSn"
                  :kpiSn="flagKpiSn"
                  @adjustTicketKpiOnly="kpiUpdate"
                />
              </div>
              <div
                v-show="options[2]['status']"
                class="column bg-orange-1 q-px-md q-pb-md"
              >
                <div class="col-12 text-center q-pa-md text-bold">MTN zone</div>
                <JiraTicketListMtn
                  :lastSummary="localResSet.localSummary"
                  :ticketSubject="name"
                  :ticketNumber="sn"
                  :ticketJiraIssueId="issueId"
                  :parentMtnFlagStatus="options[2].status"
                  @updateSummaryByMtn="summaryUpdateByMtn"
                />
              </div>
              <div
                v-if="options[1]['status']"
                class="column bg-light-blue-1 q-px-md q-pb-md"
              >
                <div class="col-12 text-center q-pa-md text-bold">Attachment zone</div>
                <!-- display -->
                <div class="col-12 row justify-start q-gutter-xs q-mb-md">
                  <div
                    class="bg-light-blue-3 q-pa-xs"
                    v-for="(value, idx) in attachmentList"
                    :key="idx"
                  >
                    <div class="row">
                      <img
                        class="rounded-borders"
                        :src="
                          'https://' +
                          ServiceDomainLocal +
                          ':9487/document/' +
                          value._type +
                          '/' +
                          ticketSn +
                          '/' +
                          value.name
                        "
                        style="height: 170px; max-width: 240px"
                      />
                    </div>
                    <div style="max-width: 240px" class="row justify-center text-wrap">
                      {{ value.name }}
                    </div>
                    <div class="row">
                      <q-btn
                        dense
                        flat
                        no-caps
                        icon="info"
                        class="col-6"
                        color="white"
                        text-color="primary"
                        type="a"
                        :href="
                          'https://' +
                          ServiceDomainLocal +
                          ':9487/view/document/' +
                          ticketSn +
                          '/' +
                          value.name
                        "
                        target="__blank"
                        label="Detail"
                      />
                      <q-btn
                        dense
                        flat
                        no-caps
                        icon="delete"
                        class="col-6"
                        color="white"
                        text-color="primary"
                        label="Delete"
                        @click="deleteAttachment(ticketSn, value.name)"
                      />
                    </div>
                  </div>
                </div>
                <!-- uploader -->
                <q-uploader
                  :url="'https://' + ServiceDomainLocal + ':9487/update/jira/attachment'"
                  label="attachment upload"
                  multiple
                  batch
                  @rejected="onRejected"
                  class="col-12"
                  accept=".jpg, .docx, .xlsx, .pptx, .txt, .jpg, .pdf, .csv, .rar, .zip, .png"
                  @uploaded="updateAttachmentList(seq, $event)"
                  @failed="updateAttachmentListFailed(seq, $event)"
                  :headers="[
                    { name: 'updater', value: isLogin.value },
                    { name: 'localDbSn', value: ticketSn },
                    { name: 'issueId', value: issueId }
                  ]"
                />
              </div>
            </div>
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, getCurrentInstance, inject, watch } from 'vue'
import { scroll, useQuasar } from 'quasar'
import { useStore } from 'vuex'
import axios from 'axios'

import JiraTicketListKpi from './JiraTicketListKpi.vue'
import JiraTicketListMtn from './JiraTicketListMtn.vue'

export default defineComponent({
  name: 'JiraTicketList',
  components: {
    JiraTicketListKpi,
    JiraTicketListMtn
  },
  props: {
    sn: String,
    seq: Number,
    ticketSn: Number,
    name: String,
    url: String,
    issueId: String,
    editorBy: String,
    editorStatus: Boolean,
    flagMtn: Boolean,
    flagTicketStatus: Number,
    flagUnderEdit: Boolean,
    flagJiraTicketStatus: String,
    flagKpiSn: Number,
    summary: String,
    updateSummary: String,
    isDisplay: Boolean,
    attachmentList: Array
  },
  emits: ['adjustJIRAKpiOnlyListToPage'],
  setup(props, context) {
    const $q = useQuasar()
    const $store = useStore()
    const tab = ref('one')
    const foreColor = ref('#000000')
    const backColor = ref('#ffff00')
    const targetRef = ref(null)
    const targetRef2 = ref(null)
    const q1BtnDropDownColor = ref(null)
    const q1BtnDropDownBGColor = ref(null)
    const q2BtnDropDownColor = ref(null)
    const q2BtnDropDownBGColor = ref(null)
    const { proxy } = getCurrentInstance()
    const localResSet = reactive({
      localEditorStatus: props.editorStatus,
      localSummary: props.summary,
      localUpdateSummary: props.updateSummary ? props.updateSummary : '',
      localIsLock: false, // check if the ticket has been edited
      localLockedBy: ''
    })
    const dialogUnderEditing = ref(false)
    const summaryToolBar = ref([])
    const updateSummaryToolBar = ref([])
    const defaultJiraTicketComment = ref([])
    const defaultJiraTicketAttachment = ref([])
    const loadingIcon = ref('')
    const isLogin = inject('isLogin')
    const CurShift = inject('CurShift')
    const CurDate = inject('CurData')
    const localKpiTemplate = reactive({})
    const localKpiHistoryTemplate = ref([])

    // Templates reacitve object
    const templatesSet = reactive([
      {
        name: 'Ticket close',
        value: [
          {
            name: 'Example1',
            value:
              '<div>No further response in 24 hours, <b><font color="#ff0000">ticket closed.</font></b></div>'
          },
          {
            name: 'Example2',
            value:
              '<div><b><font color="#ff0000">Ticket closed</font></b> no action for OPS.</div>'
          }
        ]
      },
      {
        name: 'Completion email',
        value: [
          {
            name: 'Example1',
            value:
              'Request done, already sent completion email to customer for verification and ticket closure.'
          },
          {
            name: 'Example2',
            value:
              'Completion email sent, please close the ticket after 24 hours without any feedback.'
          },
          {
            name: 'Example3',
            value: 'YT-NET completed the request. Please close the ticket after 24 hours.'
          }
        ]
      },
      {
        name: 'Ticket merge',
        value: [
          {
            name: 'Example1',
            value:
              '<div><b><font color="#ff0000">Ticket merged</font></b> to YTS________</div>'
          }
        ]
      },
      {
        name: 'ISP Maintenance example',
        value: [
          {
            name: 'Example1',
            value: `
          <div><i>Description</i>:</div>
          <div><b>Circuit ID</b>:</div>
          <div><b>Date</b>:</div>
          <div><b>Start time</b>:</div>
          <div><b>End time</b>:</div>
          <div><b>Duration</b>:</div>
          <div><b>Maintenance details</b>:</div>
          `
          }
        ]
      },
      {
        name: 'Deployment Maintenance example',
        value: [
          {
            name: 'Example1',
            value: `
          <div><i>Description</i>:</div>
          <div><i>Affected BU</i>:</div>
          <div><i>Affected Module</i>:</div>
          <div><i>Chat</i>:</div>
          <div><b>Date</b>:</div>
          <div><b>Start time</b>:</div>
          <div><b>End time</b>:</div>
          <div><b>Duration</b>:</div>
          <div><b>Action for OPS</b>:</div>
        `
          }
        ]
      },
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

    // Vuex
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain

    // check the flagKpiSn to see, if this ticket sn column flagKpiSn have value, then open the select bar, and show the jiraTicketListKpi
    const group = ref([
      props.attachmentList.length !== 0 ? 'op3' : 'fakeop3',
      props.flagKpiSn ? 'op1' : 'fakeop1',
      props.flagMtn ? 'op2' : 'fakeop2'
    ])

    const options = reactive([
      {
        label: 'KPI',
        value: 'op1',
        status: Boolean(props.flagKpiSn),
        color: 'pink-2'
      },
      {
        label: 'ATT',
        value: 'op3',
        status: Boolean(props.attachmentList.length !== 0),
        color: 'light-blue-2'
      },
      {
        label: 'MTN',
        value: 'op2',
        status: Boolean(props.flagMtn),
        color: 'orange-2'
      }
    ])

    const { getScrollTarget, setVerticalScrollPosition } = scroll
    // const { height, width } = dom

    const avatarSize = ref(
      props.attachmentList.map(function (ele, index, object) {
        return 'max-width: 75px'
      })
    )

    async function callJiraComment(targetIssueId) {
      try {
        await axios
          .get(
            `https://${ServiceDomainLocal}:9487/query/jira/issue/${targetIssueId}/comment`
          )
          .then((res) => {
            if (res.data.length !== 0) {
              defaultJiraTicketComment.value = res.data
            } else {
              loadingIcon.value =
                '<div class="bg-yellow-1 q-pa-md"><q-icon name="error_outline" size="md" /><span class="text-bold">no comment log on JIRA</span></div>'
            }
          })
      } catch (error) {
        console.log(error)
      }
    }

    async function callJiraAttachment(targetIssueId) {
      try {
        await axios
          .get(
            `https://${ServiceDomainLocal}:9487/query/jira/issue/${targetIssueId}/attachment`
          )
          .then((res) => {
            if (res.data.length !== 0) {
              console.log(res.data)
              defaultJiraTicketAttachment.value = res.data
            } else {
              loadingIcon.value =
                '<div class="bg-yellow-1 q-pa-md"><q-icon name="error_outline" size="md" /><span class="text-bold">no attachment on this ticket</span></div>'
            }
          })
      } catch (error) {
        console.log(error)
      }
    }

    function adjustSummaryColor(cmd, name) {
      proxy.q1BtnDropDownColor.hide()
      proxy.q1BtnDropDownBGColor.hide()
      proxy.targetRef.runCmd(cmd, name)
      proxy.targetRef.focus()
    }

    function adjustUpdateSummaryColor(cmd, name) {
      proxy.q2BtnDropDownColor.hide()
      proxy.q2BtnDropDownBGColor.hide()
      proxy.targetRef2.runCmd(cmd, name)
      proxy.targetRef2.focus()
    }

    // for check ticket status and do "edit", "delete" action
    async function reverseStatus(targetTicketSn, action) {
      const ele = document.getElementById(props.issueId)
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - 55
      const duration = 200
      setVerticalScrollPosition(target, offset, duration)

      // check the ticket status first
      if (action === 'edit') {
        const isBreak = ref(false)
        try {
          await axios
            .get(
              `https://${ServiceDomainLocal}:9487/query/db/jiraTicket/status/${targetTicketSn}`
            )
            .then((response) => {
              console.log(response)
              localResSet.localIsLock = response.data.isUnderEdit
              localResSet.localLockedBy = response.data.editor
            })
        } catch (error) {
          console.log(error.response.data)
          // when get this error, 99% is cause by local data is old one, so post to parent to reload the page
          proxy.$emit('forceUpdateCom', 'edit')
          isBreak.value = true
        }
        if (isBreak.value) {
          console.log('localData is not match, page will reload soon')
        } else if (
          // DB editor is same with login account
          localResSet.localIsLock &&
          isLogin.value === localResSet.localLockedBy
        ) {
          robTheTicket(targetTicketSn)
        } else if (localResSet.localIsLock) {
          // popup window for underEditing reminder
          dialogUnderEditing.value = true
        } else {
          // update the ticket flagUnderEdit and enable the text editor
          robTheTicket(targetTicketSn)
        }
      } else if (action === 'delete') {
        console.log('hit delete')
        const postData = reactive({
          newEditor: isLogin.value,
          targetTicketSn: targetTicketSn,
          action: 'delete'
        })
        axios
          .post(
            `https://${ServiceDomainLocal}:9487/update/db/jiraTicket/status`,
            postData
          )
          .then((res) => {
            console.log(res)
            isLogin.refreshKey += 1 // handover.vue watch use it to determine if need to reload the commonent
            isLogin.targetDbSn = props.seq // above reload axios target
          })
          .catch((error) => {
            console.log(error)
          })
      }
      return localResSet.localEditorStatus
    }

    function robTheTicket(targetTicketSn) {
      // enable the text editor
      localResSet.localEditorStatus = false
      // build the json data then post to backend
      const postData = reactive({
        newEditor: isLogin.value,
        targetTicketSn: targetTicketSn,
        action: 'edit'
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/update/db/jiraTicket/status`, postData)
        .then((res) => {
          console.log(res)
          if (!isLogin.refreshJIRAUnderEditingList.includes(props.ticketSn)) {
            isLogin.refreshJIRAUnderEditingList.push(props.ticketSn)
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    // TextEditor update button
    function hiddenAndUpdateEditor(targetTicketSn) {
      const updateChecker = ref(false)
      // check if the value is change
      if (props.flagTicketStatus === 0) {
        if (localResSet.localSummary !== props.summary) {
          autoAdjustFontSize('curStatus')
          updateChecker.value = true
        }
      } else if (props.flagTicketStatus === 1) {
        console.log('hit 1')
        if (localResSet.localSummary !== props.summary) {
          autoAdjustFontSize('curStatus')
          updateChecker.value = true
        }
        if (localResSet.localUpdateSummary !== props.updateSummary) {
          // sometime, even if user don't update any news on updateSummary, but system still submit the string to backend, so replace these html tag to avoid get the kind of bug.
          const replaceLocalUpdateSummary = localResSet.localUpdateSummary
            .replace('<br>', '')
            .replace('<div>', '')
            .replace('</div>', '')
          if (replaceLocalUpdateSummary !== '') {
            console.log('replaceLocalUpdateSummary is not ""')
            autoAdjustFontSize('UpdateStatus')
            updateChecker.value = true
          }
        }
      }

      // hidden TextEditor Toolbar
      summaryToolBar.value = []
      updateSummaryToolBar.value = []
      // hidde TextEditor
      localResSet.localEditorStatus = true

      // release sn from refreshJIRAUnderEditingList
      const indexOfSn = isLogin.refreshJIRAUnderEditingList.indexOf(props.ticketSn)
      if (indexOfSn > -1) {
        isLogin.refreshJIRAUnderEditingList.splice(indexOfSn, 1)
      }

      // update the summary and updateSummary, unlock flagUnderEdit to db by axios
      if (updateChecker.value) {
        const postData = reactive({
          newEditor: isLogin.value,
          targetTicketSn: targetTicketSn,
          action: 'update',
          summary: localResSet.localSummary,
          updateSummary: localResSet.localUpdateSummary
        })
        axios
          .post(
            `https://${ServiceDomainLocal}:9487/update/db/jiraTicket/status`,
            postData
          )
          .then((res) => {
            console.log(res.data)
            if (res.status === 202) {
              console.log('abnormal update')
              proxy.$emit('forceUpdateCom', 'update')
            } else {
              console.log('normal update')
              isLogin.refreshKey += 1 // handover.vue watch use it to determine if need to reload the commonent
              isLogin.targetDbSn = props.seq // above reload axios target
            }
          })
          .catch((error) => {
            console.log(error)
          })
      } else {
        console.log(
          'nothing change, so system will not update the comment, but call the cancel to unlock the ticket'
        )
        hiddenAndCancelEditor(targetTicketSn)
      }
    }

    // TextEditor cancel button
    function hiddenAndCancelEditor(targetTicketSn) {
      // hidden TextEditor Toolbar
      summaryToolBar.value = []
      updateSummaryToolBar.value = []
      // hidde TextEditor
      localResSet.localEditorStatus = true

      // release sn from refreshJIRAUnderEditingList
      const indexOfSn = isLogin.refreshJIRAUnderEditingList.indexOf(props.ticketSn)
      if (indexOfSn > -1) {
        isLogin.refreshJIRAUnderEditingList.splice(indexOfSn, 1)
      }
      // adjust ticket status
      const postData = reactive({
        newEditor: null,
        targetTicketSn: targetTicketSn,
        action: 'cancel'
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/update/db/jiraTicket/status`, postData)
        .then((res) => {
          console.log(res)
          isLogin.refreshKey += 1 // handover.vue watch use it to determine if need to reload the commonent
          isLogin.targetDbSn = props.seq // above reload axios target
        })
        .catch((error) => {
          console.log(error)
        })
      const ele = document.getElementById(props.issueId)
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - 55
      const duration = 200
      setVerticalScrollPosition(target, offset, duration)
    }

    function checkSummaryZone() {
      updateSummaryToolBar.value = []
      summaryToolBar.value = [
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
      ]
    }

    function checkUpdateSummaryZone() {
      summaryToolBar.value = []
      updateSummaryToolBar.value = [
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
      ]
    }

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

    // before ticket update, adjust the font size per target ( summary or update summary )
    function autoAdjustFontSize(target) {
      if (target === 'curStatus') {
        console.log('autoAdjustFontSize hit curStatus')
        proxy.targetRef.runCmd('selectAll')
        proxy.targetRef.runCmd('fontsize', 2)
      } else if (target === 'UpdateStatus') {
        proxy.targetRef2.runCmd('selectAll')
        proxy.targetRef2.runCmd('fontsize', 2)
        console.log('autoAdjustFontSize hit UpdateStatus')
      }
    }

    function gotoJiraTicket(targetURL) {
      window.open(`${targetURL}`, '_blank')
    }

    function returnCorrectColor(currentStatus) {
      switch (currentStatus) {
        case 'In Progress':
          return 'blue-3'
        case 'Under investigation':
          return 'light-blue-3'
        case 'Completed':
          return 'cyan-3'
        case 'Resolved':
          return 'teal-3'
        case 'Canceled':
          return 'green-3'
        default:
          return 'red-5'
      }
    }

    function jiraStatusSelector(currentStatus) {
      console.log(currentStatus)
      const ele = document.getElementById('10323')
      console.log(ele)
    }

    function deleteAttachment(localDbSn, fileName) {
      const postData = reactive({
        targetTicketSn: localDbSn,
        targetFileName: fileName
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/delete/attachment`, postData)
        .then((res) => {
          console.log(res)
          isLogin.refreshKey += 1 // handover.vue watch use it to determine if need to reload the commonent
          isLogin.targetDbSn = props.seq // above reload axios target
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function updateAttachmentList(targetSeq, event) {
      console.log(targetSeq)
      console.log(event)
      $q.notify({
        message: '<b>UPLOAD SUCCESS!</b>',
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
      isLogin.targetDbSn = targetSeq
      isLogin.refreshKey += 1
    }

    function updateAttachmentListFailed(targetSeq, event) {
      console.log('hit updateAttachmentListFailed')
      console.log(targetSeq)
      console.log(event.xhr.status)
      console.log(event.xhr.response)
      $q.notify({
        message: `<B>UPLOAD FAILED</B><br> backend response: <br>ERROR_CODE: <b>${event.xhr.status}</b>; <br>ERROR_FILENAME: <b>${event.xhr.response}</b><br>Please re-try later.`,
        color: 'red-6',
        progress: true,
        position: 'center',
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

    function checkFileType(files) {
      return files.filter(
        (file) =>
          file.type ===
          ('image/png' |
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
            'application/vnd.openxmlformats-officedocument.presentationml.presentation' ||
            'text/plain' ||
            'image/jpeg' ||
            'application/pdf' ||
            'application/vnd.ms-excel' ||
            'application/octet-stream' ||
            'application/x-zip-compressed')
      )
    }

    function onRejected(rejectedEntries) {
      // Notify plugin needs to be installed
      // https://quasar.dev/quasar-plugins/notify#Installation
      $q.notify({
        type: 'negative',
        message: `${rejectedEntries.length} file(s) did not pass validation constraints`
      })
    }

    function popuptheattachment(fileName, ticketSn) {
      const custUrl = `https://${ServiceDomainLocal}:9487/view/document/${ticketSn}/${fileName}`
      window.open(`${custUrl}`, '_blank')
    }

    function adjustTheAvatarSize(direction, targetAttachment, event) {
      const ele = document.getElementById(props.issueId)
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - 55
      const duration = 200
      switch (direction) {
        case 'in':
          avatarSize.value[targetAttachment] = 'max-width: 100%'
          break
        case 'out':
          avatarSize.value[targetAttachment] = 'max-width: 75px'
          setVerticalScrollPosition(target, offset, duration)
          break
      }
    }

    // ticket editor - when kpi without data, will open the kpi zone
    function notifyKpiAlert() {
      if (props.flagKpiSn === null) {
        if (!group.value.includes('op1')) {
          group.value.push('op1')
          console.log('group value without op1 option, add it')
        } else {
          console.log('group value with op1 option already, ignore it')
        }
        options.forEach((ele, idx, object) => {
          if (ele.value === 'op1') {
            console.log('hit change option status action')
            object[idx].status = true
          }
        })
      } else {
        console.log('kpi has data')
      }
    }

    function kpiUpdate(kpiSn) {
      context.emit('adjustJIRAKpiOnlyListToPage', [props.ticketSn, kpiSn])
      // isLogin.refreshKey += 1 // handover.vue watch use it to determine if need to reload the commonent
      // isLogin.targetDbSn = props.seq // above reload axios target
    }

    async function callKpi(curFlagKpiSn) {
      try {
        if (curFlagKpiSn) {
          // if curFlagKpiSn !== null, means this shift someone already udpate the KPI, so display it
          await axios
            .get(`https://${ServiceDomainLocal}:9487/kpi/view/${curFlagKpiSn}`)
            .then((res) => {
              localKpiTemplate.sn = res.data.sn
              localKpiTemplate.type = res.data.type
              localKpiTemplate.resolve_status = res.data.resolve_status
              localKpiTemplate.handler = res.data.handler
              localKpiTemplate.handler_second = res.data.handler_second
              localKpiTemplate.participant = res.data.participant
              localKpiTemplate.origin_source = res.data.origin_source
              localKpiTemplate.origin_source_subject = res.data.origin_source_subject
              localKpiTemplate.related_sn = res.data.related_sn
              localKpiTemplate.related_date = res.data.related_date
              localKpiTemplate.related_shift = res.data.related_shift
              localKpiTemplate.related_group = res.data.related_group
              localKpiTemplate.description = res.data.description
              localKpiTemplate.file_path = res.data.file_path
              // and display the button to query the history
            })
        } else {
          // show system can't see the KPI record on this shift, and button with query the history
          await console.log(
            'show system can not see the KPI record on this shift, and button with query the history'
          )
        }
      } catch (error) {
        await console.log(error)
      }
    }

    async function callKpiHistory(targetJiraIssueId) {
      try {
        await axios
          .get(`https://${ServiceDomainLocal}:9487/kpi/jira/${targetJiraIssueId}`)
          .then((res) => {
            if (res.data.length !== 0) {
              console.log(res.data)
              localKpiHistoryTemplate.value = res.data
            } else {
              $q.notify({
                message: `<b>No KPI record for ${props.sn}!</b>`,
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
      } catch (error) {
        await console.log(error)
      }
    }

    function popupKpiFile(date, shift, sn, path) {
      window.open(
        `https://${ServiceDomainLocal}:9487/query/kpi/${date}/${shift}/jira/${sn}/${path}`,
        '_blank'
      )
    }

    function sortOutKpiResult() {
      axios
        .get(
          `https://${ServiceDomainLocal}:9487/sortout/kpi/tojira/${props.issueId}/sortout`
        )
        .then(async (res) => {
          console.log(res.data)
          const resultRequestHandler = res.data.fields.customfield_10075
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const resultTroubleShootHandler = res.data.fields.customfield_10079
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const requestTHandlerSecond = res.data.fields.customfield_10076
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const requestTParticipant = res.data.fields.customfield_10077
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const kpiRequestType = res.data.fields.customfield_10078
            ? res.data.fields.customfield_10078.value
            : res.data.fields.customfield_10078
          const qMessageTemplate = `
                                    <div class="row q-mb-xs">
                                        <div class="col-6 text-white text-center rounded-borders bg-dark">Final KPI type</div>
                                        <div class="col-6 text-center">${kpiRequestType}</div>
                                    </div>
                                    <div class="row q-mb-xs">
                                        <div class="col-6 text-center rounded-borders bg-green-5">Request Handler</div>
                                        <div class="col-6 q-pl-xs">${resultRequestHandler}</div>
                                    </div>
                                    <div class="row q-mb-xs">
                                        <div class="col-6 text-white text-center rounded-borders bg-red-5">Troubleshooting Handler</div>
                                        <div class="col-6 q-pl-xs">${resultTroubleShootHandler}</div>
                                    </div>
                                    <div class="row q-mb-xs">
                                        <div class="col-6 text-center rounded-borders bg-yellow-5">Handler(Deputy)</div>
                                        <div class="col-6 q-pl-xs">${requestTHandlerSecond}</div>
                                    </div>
                                    <div class="row q-mb-xs">
                                        <div class="col-6 text-center rounded-borders bg-yellow-5">Participant(s)</div>
                                        <div class="col-6 q-pl-xs">${requestTParticipant}</div>
                                    </div>
                                    `
          await $q.dialog({
            title: 'KPI Summary',
            message: qMessageTemplate,
            html: true
          })
        })
        .catch((error) => {
          console.log(error)
        })
    }

    async function adjustTicketFlagMtnStatus(isEnable) {
      const postData = reactive({
        curStatus: isEnable,
        targetJiraTicketSn: props.ticketSn
      })
      await axios
        .post(`https://${ServiceDomainLocal}:9487/mtn/update`, postData)
        .then((res) => {
          console.log(res)
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function updateValueToSummary(target) {
      if (localResSet.localSummary === 'New ticket') {
        localResSet.localSummary = target.value
      } else {
        localResSet.localSummary = localResSet.localSummary + target.value
      }
    }

    function updateValueToUpdateSummary(target) {
      if (localResSet.localUpdateSummary === '') {
        localResSet.localUpdateSummary = target.value
      } else {
        localResSet.localUpdateSummary = localResSet.localUpdateSummary + target.value
      }
    }

    // mtn update
    function summaryUpdateByMtn(mtnObject) {
      function getSwitchResult(target) {
        switch (target) {
          case 'ndd':
            return 'No downtime deployment'
          case 'dd':
            return 'Downtime deployment'
          case 'cm':
            return 'Circuit maintenance'
          case 'other':
            return 'Other'
        }
      }
      const mtnTitle = getSwitchResult(mtnObject[1].value)
      if (mtnTitle === 'Circuit maintenance') {
        localResSet.localSummary = `
        <div><b>${mtnTitle}</b></div>
        <div><b>Vendor:</b> <span>${mtnObject[0].mtnVendor}</span></div>
        <div><b>Circuit ID:</b> <span>${mtnObject[0].mtnCircuit}</span></div>
        <div><b>Environment:</b> <span><font color="#0000FF">${mtnObject[0].mtnEnvironment}</font></span></div>
        <div><b>Affected customer:</b> <span><font color="#0000FF">${mtnObject[0].mtnAffectedCustomer}</font></span></div>
        <div><b>Start time:</b> <span><font color="#ff0000">${mtnObject[0].mtnStartTime}</font></span></div>
        <div><b>End time:</b> <span><font color="#ff0000">${mtnObject[0].mtnEndTime}</font></span></div>
        <div><b>Duration:</b> <span>${mtnObject[0].mtnDuration}</span></div>
      `
      } else {
        localResSet.localSummary = `
        <div><b>${mtnTitle}</b></div>
        <div><b>BU:</b> <span>${mtnObject[0].mtnBu}</span></div>
        <div><b>Impacted module:</b> <span>${mtnObject[0].mtnModule}</span></div>
        <div><b>Date:</b> <span><font color="#ff0000">${mtnObject[0].mtnDate}</font></span></div>
        <div><b>Start time:</b> <span><font color="#ff0000">${mtnObject[0].mtnStartTime}</font></span></div>
        <div><b>End time:</b> <span><font color="#ff0000">${mtnObject[0].mtnEndTime}</font></span></div>
        <div><b>Duration:</b> <span>${mtnObject[0].mtnDuration}</span></div>
      `
      }
    }

    watch(
      () => group.value,
      (curKey, oldKey) => {
        // add
        if (curKey.length > oldKey.length) {
          // find the new
          const newItem = curKey.filter((ele) => {
            return !oldKey.includes(ele)
          })

          // if new item is op2 (mtn), trigger mtn function
          if (newItem[0] === 'op2') {
            adjustTicketFlagMtnStatus(true)
          }

          options.forEach((optionItem) => {
            if (newItem[0] === optionItem.value) {
              optionItem.status = true
            }
          })
        } else {
          // remove
          const removeItem = oldKey.filter((ele) => {
            return !curKey.includes(ele)
          })

          // if remove item is op2 (mtn), trigger mtn function
          if (removeItem[0] === 'op2') {
            adjustTicketFlagMtnStatus(false)
          }

          options.forEach((optionItem) => {
            if (removeItem[0] === optionItem.value) {
              optionItem.status = false
            }
          })
        }
      }
    )

    watch(
      () => [props.editorStatus, props.summary, props.updateSummary],
      (curValue, oldValue) => {
        console.log('hit DHSNoteList Watch 4 targets')
        curValue.forEach((num1, index) => {
          const num2 = oldValue[index]
          if (num1 !== num2) {
            if (index === 0) {
              localResSet.localEditorStatus = num1
            } else if (index === 1) {
              localResSet.localSummary = num1
            } else if (index === 2) {
              localResSet.localUpdateSummary = num1
            }
          }
        })
      },
      { deep: true }
    )

    // A user create the KPI, B user will use this watch to open the KPI group and option zone
    watch(
      () => props.flagKpiSn,
      (curValue, oldValue) => {
        if (curValue) {
          // console.log('hit JiraTicketList watch props.flagKpiSn')
          if (!group.value.includes('op1')) {
            group.value.push('op1')
            options.forEach((optionItem) => {
              if (optionItem.value === 'op1') {
                optionItem.status = true
              }
            })
          } // else - console.log('group.value has op1 value, ignore this watch')
        }
      }
    )

    watch(
      () => props.flagMtn,
      (curValue, oldValue) => {
        console.log(`curValue = ${curValue}`)
        console.log(`oldValue = ${oldValue}`)
      }
    )

    return {
      tab,
      callJiraComment,
      callJiraAttachment,
      foreColor,
      backColor,
      ConvertforeColor,
      adjustSummaryColor,
      adjustUpdateSummaryColor,
      targetRef,
      targetRef2,
      q1BtnDropDownColor,
      q1BtnDropDownBGColor,
      q2BtnDropDownColor,
      q2BtnDropDownBGColor,
      proxy,
      reverseStatus,
      localResSet,
      hiddenAndUpdateEditor,
      hiddenAndCancelEditor,
      dialogUnderEditing,
      robTheTicket,
      summaryToolBar,
      updateSummaryToolBar,
      checkSummaryZone,
      checkUpdateSummaryZone,
      defaultJiraTicketComment,
      defaultJiraTicketAttachment,
      loadingIcon,
      autoAdjustFontSize,
      isLogin,
      CurDate,
      CurShift,
      gotoJiraTicket,
      returnCorrectColor,
      jiraStatusSelector,
      group,
      options,
      deleteAttachment,
      updateAttachmentList,
      updateAttachmentListFailed,
      checkFileType,
      onRejected,
      popuptheattachment,
      adjustTheAvatarSize,
      avatarSize,
      notifyKpiAlert,
      kpiUpdate,
      callKpi,
      callKpiHistory,
      localKpiTemplate,
      localKpiHistoryTemplate,
      popupKpiFile,
      sortOutKpiResult,
      adjustTicketFlagMtnStatus,
      summaryUpdateByMtn,
      templatesSet,
      updateValueToSummary,
      updateValueToUpdateSummary,
      ServiceDomainLocal
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
