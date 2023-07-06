<!-- @format -->
<template>
  <q-dialog
    v-model="dialogUnderEditing"
    persistent
    transition-show="scale"
    transition-hide="scale"
  >
    <q-card class="bg-teal text-white" style="width: 300px">
      <q-card-section>
        <div class="text-h6">
          Under editing by
          {{ localResSet.update_by }}
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        YTS{{ localResSet.number }}-{{ localResSet.subject }}
      </q-card-section>
      <q-card-actions align="right" class="bg-white text-teal">
        <q-btn flat label="Close" v-close-popup />
        <q-btn @click="robOTRSeditor(sn)" flat label="Take Over" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <div v-if="sequence !== 99" class="row q-px-md q-pt-md q-pb-none row q-gutter-sm">
    <!-- {{ status }} {{ update_by }} -->
    <q-card
      :id="'otrs' + number"
      flat
      bordered
      class="col-12"
      :class="localEditorStatus ? 'bg-teal-1' : ''"
    >
      <q-card-section class="row">
        <div class="row justify-start items-center text-h6 text-h6 col-md-10">
          <q-icon
            class="q-pr-xs cursor-pointer"
            color="blue-10"
            size="md"
            @click="expanded = !expanded"
            :name="expanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
          />
          <span class="text-blue-10 cursor-pointer" @click="openNewPageToTicket"
            >YTS{{ number }} - {{ subject }}</span
          >
        </div>
        <div class="col-md-2 text-right">
          <q-chip
            :color="returnCorrectColor(customer)"
            text-color="white"
            square
            class="text-right"
          >
            {{ customer }}
          </q-chip>
          <q-chip
            v-if="maintenance === 1"
            color="light-blue-3"
            text-color="dark"
            square
            class="text-right"
          >
            MTN
          </q-chip>
          <q-chip
            v-if="flagCloseTicket"
            color="red-6"
            text-color="white"
            square
            class="text-right"
          >
            Close
          </q-chip>
        </div>
      </q-card-section>
      <q-slide-transition>
        <div v-show="expanded">
          <q-tabs align="left" v-model="tabofCard" class="text-teal">
            <q-tab label="Handover" name="one" />
            <q-tab label="Log" name="three" @click.stop="callLog()" />
            <q-tab label="KPI" name="four" @click.stop="callKpi(kpi_result)">
              <q-badge v-if="kpi_result !== 0" floating rounded color="red" />
            </q-tab>
          </q-tabs>
          <q-separator inset />
          <q-tab-panels v-model="tabofCard" animated>
            <q-tab-panel name="one">
              <section v-show="localEditorStatus">
                <div class="row items-center">
                  <div class="col-1 text-left">Current Status:</div>
                  <q-editor
                    class="col-11"
                    v-model="localResSet.summary"
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
                </div>
                <div v-if="localResSet.update_summary != 'New'">
                  <div class="row items-center">
                    <div class="col-1 text-left">Update Status:</div>
                    <q-editor
                      class="col-11"
                      v-model="localResSet.update_summary"
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
                            foreColor
                              ? ConvertforeColor('fore')
                              : ConvertforeColor('fore')
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
                            backColor
                              ? ConvertforeColor('back')
                              : ConvertforeColor('back')
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
                      <!--  -->
                      <q-tooltip
                        class="bg-pink-2 text-black"
                        anchor="top middle"
                        self="bottom middle"
                        :delay="100"
                        :offset="[10, 10]"
                        v-if="kpi_result === 0"
                      >
                        Miss KPI Update!
                      </q-tooltip>
                      <!-- :disable="kpi_result === 0" -->
                      <q-btn
                        class="q-mt-xs q-ml-xs"
                        color="white"
                        text-color="primary"
                        label="Update"
                        @click="hiddenAndUpdateEditor(sn)"
                        :disable="kpi_result === 0"
                      >
                      </q-btn>
                    </span>
                    <q-btn
                      color="white"
                      text-color="primary"
                      label="Cancel"
                      @click="hiddenAndCancelEditor('button')"
                    />
                  </div>
                </div>
                <div
                  v-show="options[0]['status']"
                  class="column bg-pink-1 q-px-md q-pb-md q-mt-md"
                >
                  <div class="col-12 text-center q-pa-md text-bold">KPI zone</div>
                  <DHSOTRSListKpi
                    @adjustOTRSKpiOnly="kpiUpdate"
                    :targetKpiSn="kpi_result"
                    :targetOTRSSn="sn"
                    :targetOTRSNumber="number"
                  />
                </div>
                <div
                  v-show="options[1]['status']"
                  class="column bg-light-blue-1 q-px-md q-pb-md"
                >
                  <div class="col-12 text-center q-pa-md text-bold">MTN zone</div>
                  <DHSOTRSListMtn
                    :lastSummary="localResSet.summary"
                    :ticketSubject="localResSet.subject"
                    :ticketNumber="sn"
                    :ticketJiraIssueId="localResSet.number"
                    :parentMtnFlagStatus="options[1].status"
                    @updateSummaryByMtn="summaryUpdateByMtn"
                  />
                </div>
              </section>
              <section v-show="!localEditorStatus">
                <!-- check if this is new note -->
                <section v-if="localResSet.update_summary === 'New'">
                  <div class="custom-border-display otrs q-py-md rounded-borders">
                    <div class="bg-yellow-3 q-px-md text-bold">
                      Created by {{ localResSet.update_by }}
                    </div>
                    <div class="q-px-md" v-html="localResSet.summary"></div>
                  </div>
                </section>
                <!-- check if new update for this note -->
                <section
                  v-else-if="localResSet.update_by && localResSet.update_summary !== null"
                >
                  <div class="custom-border-display otrs q-py-md rounded-borders">
                    <div class="bg-yellow-1 q-px-md text-bold">Current status:</div>
                    <div class="q-px-md" v-html="localResSet.summary"></div>
                    <section v-if="localResSet.update_summary">
                      <div class="bg-yellow-3 q-px-md text-bold">
                        Update by {{ localResSet.update_by }}
                      </div>
                      <div class="q-px-md" v-html="localResSet.update_summary"></div>
                    </section>
                  </div>
                </section>
                <!-- nothing change, display current -->
                <section v-else>
                  <div class="custom-border-display otrs q-py-md rounded-borders">
                    <div class="bg-yellow-1 q-px-md text-bold">Current status:</div>
                    <div class="q-px-md" v-html="localResSet.summary"></div>
                  </div>
                </section>
                <div class="row q-pt-sm q-gutter-sm text-right">
                  <q-btn
                    color="white"
                    text-color="primary"
                    label="Edit"
                    @click="reverseRefreshLockStatus"
                  />
                  <q-btn
                    :color="flagCloseTicket ? 'grey-4' : 'white'"
                    text-color="primary"
                    label="close"
                    @click="closeOTRS"
                  />
                  <q-btn
                    color="white"
                    text-color="primary"
                    label="Move"
                    @click="queryOTRSSeqList"
                  />
                </div>
              </section>
            </q-tab-panel>
            <q-tab-panel name="three">
              <DHSOTRSListLog
                v-if="containerOfLog"
                :ticketNumber="number"
                source="fromOrigin"
              ></DHSOTRSListLog>
            </q-tab-panel>
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
                          <div>
                            Handler(deputy): {{ localKpiTemplate.handler_second }}
                          </div>
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
                          <div>
                            Handler(deputy): {{ localKpiTemplate.handler_second }}
                          </div>
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
                              '/ticket/' +
                              localKpiTemplate.related_sn +
                              '/' +
                              localKpiTemplate.file_path +
                              '?v=' +
                              Math.random()
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
                    @click="callKpiHistory(number)"
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
                                '/ticket/' +
                                item.related_sn +
                                '/' +
                                item.file_path +
                                '?v=' +
                                Math.random()
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
                    @click="callKpiHistory(number)"
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
                                '/ticket/' +
                                item.related_sn +
                                '/' +
                                item.file_path +
                                '?v=' +
                                Math.random()
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
          </q-tab-panels>
        </div>
      </q-slide-transition>
    </q-card>
  </div>
  <div v-else class="row q-px-md q-pt-md q-pb-none row q-gutter-sm">
    <q-card flat bordered class="col-12">
      <q-card-section>
        <div class="row justify-between items-center text-italic text-h6">
          <div style="opacity: 0.5">
            <span class="text-italic text-dark">
              <a @click="openNewPageToTicket">YTS{{ number }}</a>
              -{{ subject }}</span
            >
            has been <span class="text-italic text-red-8 text-bold">deleted</span>
          </div>
          <q-btn label="rollback" @click="rollbackTicket"></q-btn>
        </div>
      </q-card-section>
      <q-card-section style="opacity: 0.5" class="q-pt-none">
        <span v-html="summary"></span>
      </q-card-section>
    </q-card>
  </div>
</template>

<script>
import {
  defineComponent,
  ref,
  reactive,
  getCurrentInstance,
  watch,
  inject
  // computed
} from 'vue'
import axios from 'axios'
import { useStore } from 'vuex'
import { scroll, useQuasar } from 'quasar'

import DHSOTRSListKpi from './DHSOTRSListKpi.vue'
import DHSOTRSListLog from './DHSOTRSListLog.vue'
import DHSOTRSListMtn from './DHSOTRSListMtn.vue'

export default defineComponent({
  name: 'DHSOTRSList',
  components: {
    DHSOTRSListLog,
    DHSOTRSListKpi,
    DHSOTRSListMtn
  },
  emits: ['adjustOTRSKpiOnlyListToPage'],
  props: {
    customer: String,
    date: String,
    kpi_result: Number,
    maintenance: Number,
    number: Number,
    sequence: Number,
    subject: String,
    shift: String,
    sn: Number,
    status: Number,
    summary: String,
    update_by: String,
    update_summary: String,
    flagCloseTicket: Boolean
  },
  setup(props, context) {
    const $q = useQuasar()
    const $store = useStore()
    const { proxy } = getCurrentInstance()
    const isLogin = inject('isLogin') // get the root isLogin dict
    const tabofCard = ref('one') // check the note card tab need to display which one
    const dialogUnderEditing = ref(false) // display alert popup window when note is under editing
    const localEditorStatus = ref(false) // display note raw data or rich text
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const summaryToolBar = ref([]) // default will not show the toolbar
    const updateSummaryToolBar = ref([]) // default will not show the toolbar for update_summary
    const q1BtnDropDownColor = ref(null) // summary font color button
    const q1BtnDropDownBGColor = ref(null) // summary background button
    const q2BtnDropDownColor = ref(null) // update summary font color button
    const q2BtnDropDownBGColor = ref(null) // update summary background button
    const foreColor = ref('#000000') // default font color
    const backColor = ref('#ffff00') // default font bg color
    const targetRef = ref(null) // q-editor summary ref
    const targetRef2 = ref(null) // q-editor update summary ref
    const { getScrollTarget, setVerticalScrollPosition } = scroll // scroll function
    const localKpiTemplate = reactive({})
    // const scriptContainer = ref()
    const localKpiHistoryTemplate = ref([])
    const localResSet = reactive({
      subject: props.subject,
      number: props.number,
      summary: props.summary,
      update_summary: props.update_summary ? props.update_summary : '',
      update_by: props.update_by
    })
    const containerOfLog = ref(false)
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

    const group = ref([
      props.kpi_result !== 0 ? 'op1' : 'fakeop1',
      props.maintenance ? 'op2' : 'fakeop2'
    ])

    const options = reactive([
      {
        label: 'KPI',
        value: 'op1',
        status: Boolean(props.kpi_result),
        color: 'pink-2'
      },
      {
        label: 'MTN',
        value: 'op2',
        status: Boolean(props.maintenance),
        color: 'light-blue-2'
      }
    ])

    const expanded = ref(true)

    // const avatarSize = computed(() =>
    //   attachments.value.map(function (ele, index, object) {
    //     return 'max-width: 75px'
    //   })
    // )

    function reverseRefreshLockStatus() {
      // # db status
      axios
        .get(`https://${ServiceDomainLocal}:9487/bpOTRS/query/${props.sn}`)
        .then((res) => {
          if (res.data[0].status !== 0) {
            localResSet.update_by = res.data[0].update_by
            if (isLogin.value !== res.data[0].update_by) {
              dialogUnderEditing.value = true
            } else {
              robOTRSeditor(props.sn)
            }
          } else {
            robOTRSeditor(props.sn)
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function robOTRSeditor(targetSn) {
      const postData = {
        newEditor: isLogin.value,
        targetSn: props.sn,
        action: 'edit'
      }
      axios
        .post(`https://${ServiceDomainLocal}:9487/bpOTRS/update/status`, postData)
        .then((res) => {
          console.log(res)
          // update local status to display rich text edit
          localEditorStatus.value = true
          if (!isLogin.refreshOTRSUnderEditingList.includes(props.sn)) {
            isLogin.refreshOTRSUnderEditingList.push(props.sn)
          }
          const ele = document.getElementById('otrs' + props.number)
          const target = getScrollTarget(ele)
          const offset = ele.offsetTop - 55
          const duration = 200
          setVerticalScrollPosition(target, offset, duration)
        })
        .catch((error) => {
          console.log(error)
        })
    }

    // // when user click the summary zone, will display the toolbar, and hide another one
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

    // when user click the summary zone, will display the toolbar, and hide another one
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

    function updateValueToSummary(target) {
      localResSet.summary = localResSet.summary + target.value
    }

    function updateValueToUpdateSummary(target) {
      localResSet.update_summary = localResSet.update_summary + target.value
    }

    // note editor - when kpi without data, will open the kpi zone
    function notifyKpiAlert() {
      if (props.kpi_result === 0) {
        if (!group.value.includes('op1')) {
          group.value.push('op1')
        }
        options.forEach((ele, idx, object) => {
          if (ele.value === 'op1') {
            object[idx].status = true
          }
        })
      } else {
        console.log('kpi has data')
      }
    }

    // adjust q-chip color - customer name
    function returnCorrectColor(targetName) {
      switch (targetName) {
        case '188A':
          return 'orange-6'
        case 'Internal':
          return 'dark'
        default:
          return 'light-green-6'
      }
    }

    // TextEditor update button
    function hiddenAndUpdateEditor(oSn) {
      // check if the value is change, summary and updateSummary
      if (localResSet.summary !== props.summary) {
        autoAdjustFontSize('curStatus')
      }

      if (localResSet.update_summary !== 'New') {
        if (localResSet.update_summary === '<br>') {
          localResSet.update_summary = ''
        } else if (localResSet.update_summary === '<div><br></div>') {
          localResSet.update_summary = ''
        } else {
          console.log('hit autoAdjustFontSize UpdateStatus')
          autoAdjustFontSize('UpdateStatus')
        }
      }

      // hidden TextEditor Toolbar
      summaryToolBar.value = []
      updateSummaryToolBar.value = []

      // hidde TextEditor
      localEditorStatus.value = false

      // release sn from refreshOTRSUnderEditingList
      const indexOfSn = isLogin.refreshOTRSUnderEditingList.indexOf(props.sn)
      if (indexOfSn > -1) {
        isLogin.refreshOTRSUnderEditingList.splice(indexOfSn, 1)
      }

      // update the summary and updateSummary, unlock flagUnderEdit to db by axios
      const postData = reactive({
        newEditor: isLogin.value,
        targetSn: props.sn,
        action: 'update',
        summary: localResSet.summary,
        updateSummary: localResSet.update_summary
      })

      console.log(postData)

      axios
        .post(`https://${ServiceDomainLocal}:9487/bpOTRS/update/status`, postData)
        .then((res) => {
          console.log(res)
          // update to parent
          isLogin.refreshOTRSStep += 1
        })
        .catch((error) => {
          console.log(error)
        })
    }

    // TextEditor cancel button
    function hiddenAndCancelEditor(source) {
      if (source === 'button') {
        // hidden TextEditor Toolbar
        summaryToolBar.value = []
        updateSummaryToolBar.value = []

        // hidde TextEditor, this one is diff with ticket, reverse the default value
        localEditorStatus.value = false

        // release sn from refreshOTRSUnderEditingList
        const indexOfSn = isLogin.refreshOTRSUnderEditingList.indexOf(props.sn)
        if (indexOfSn > -1) {
          isLogin.refreshOTRSUnderEditingList.splice(indexOfSn, 1)
        }

        // replace localResSet by props
        for (const [key, value] of Object.entries(props)) {
          if (Object.keys(localResSet).includes(key)) {
            if (key === 'update_summary') {
              if (value === null) {
                localResSet[key] = ''
              } else {
                localResSet[key] = value
              }
            } else {
              localResSet[key] = value
            }
          }
        }
      }
      // adjust ticket status
      const postData = reactive({
        targetSn: props.sn,
        action: 'cancel'
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/bpOTRS/update/status`, postData)
        .then((res) => {
          console.log(res)
          // // reload the note
          isLogin.refreshOTRSStep += 1
        })
        .catch((error) => {
          console.log(error)
        })
      const ele = document.getElementById('otrs' + props.number)
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - 55
      const duration = 200
      setVerticalScrollPosition(target, offset, duration)
    }

    // before ticket update, adjust the font size per target ( summary or update summary )
    function autoAdjustFontSize(target) {
      if (target === 'curStatus') {
        console.log('autoAdjustFontSize hit curStatus')
        proxy.targetRef.runCmd('selectAll')
        proxy.targetRef.runCmd('fontsize', 2)
        console.log('done for adjust')
      } else if (target === 'UpdateStatus') {
        proxy.targetRef2.runCmd('selectAll')
        proxy.targetRef2.runCmd('fontsize', 2)
        console.log('autoAdjustFontSize hit UpdateStatus')
      }
    }

    function closeOTRS() {
      switch (props.flagCloseTicket) {
        case true:
          $q.dialog({
            title: 'Confirm',
            message: `Would you like to remove close flag for YTS${props.number}?`,
            cancel: true,
            persistent: true
          }).onOk(() => {
            const postData = reactive({
              targetSn: props.sn,
              action: 'rmClose'
            })
            axios
              .post(`https://${ServiceDomainLocal}:9487/bpOTRS/update/status`, postData)
              .then((res) => {
                if (res.status === 200) {
                  $q.notify({
                    message: res.data,
                    color: 'green-12',
                    textColor: 'dark',
                    progress: true,
                    actions: [
                      {
                        icon: 'cancel',
                        color: 'white',
                        handler: () => {}
                      }
                    ]
                  })
                  isLogin.refreshOTRSStep += 1
                }
              })
              .catch((error) => {
                console.log(error)
              })
          })
          break
        case false:
          $q.dialog({
            title: 'Confirm',
            message: `Would you like to close YTS${props.number} on next shift?`,
            options: {
              type: 'radio',
              model: false,
              items: [
                {
                  label: 'No further response in 24 hours, ticket closed.',
                  value:
                    '<div>No further response in 24 hours, <span class="text-bold text-red-6">ticket closed.</span></div>',
                  color: 'secondary'
                },
                {
                  label: 'Ticket closed, no action for OPS',
                  value:
                    '<div><span class="text-bold text-red-6">Ticket closed</span> no action for OPS.</div>',
                  color: 'secondary'
                }
              ]
            },
            cancel: true,
            persistent: true
          }).onOk((data) => {
            const postData = reactive({
              targetSn: props.sn,
              action: 'close',
              option: data,
              editor: isLogin.value
            })
            axios
              .post(`https://${ServiceDomainLocal}:9487/bpOTRS/update/status`, postData)
              .then((res) => {
                if (res.status === 200) {
                  $q.notify({
                    message: res.data,
                    color: 'red-12',
                    textColor: 'white',
                    progress: true,
                    actions: [
                      {
                        icon: 'cancel',
                        color: 'white',
                        handler: () => {}
                      }
                    ]
                  })
                  isLogin.refreshOTRSStep += 1
                }
              })
              .catch((error) => {
                console.log(error)
              })
          })
          break
      }
    }

    function rollbackTicket() {
      const postData = reactive({
        targetSn: props.sn,
        targetZone: props.customer,
        action: 'rollback'
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/bpOTRS/update/status`, postData)
        .then((res) => {
          console.log(res)
          if (res.status === 200) {
            $q.notify({
              message: res.data,
              color: 'green-12',
              textColor: 'dark',
              progress: true,
              actions: [
                {
                  icon: 'cancel',
                  color: 'white',
                  handler: () => {}
                }
              ]
            })
            isLogin.refreshOTRSStep += 1
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    async function queryOTRSSeqList() {
      // due to diff customer zone will have diff order, so need to pass customer let backend know it
      await axios
        .get(`https://${ServiceDomainLocal}:9487/bpOTRS/query/list/${props.customer}`)
        .then((res) => {
          console.log(res.data)
          radio(res.data)
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function radio(targetItems) {
      $q.dialog({
        title: `Adjust the order for ${props.customer}`,
        message: 'Choose an option:',
        options: {
          type: 'radio',
          model: 'opt1',
          items: targetItems
        },
        cancel: true,
        persistent: true
      }).onOk((newPosition) => {
        const postData = {
          targetSn: props.sn,
          action: 'moveSequence',
          newPosition: newPosition,
          targetZone: props.customer
        }
        axios
          .post(`https://${ServiceDomainLocal}:9487/bpOTRS/update/status`, postData)
          .then((res) => {
            console.log(res)
            isLogin.refreshOTRSStep += 1
          })
          .catch((error) => {
            console.log(error)
          })
      })
    }

    function openNewPageToTicket() {
      const targetId = ref(0)
      if (props.number >= 92027180) {
        targetId.value = props.number - 92000009
      } else if (props.number >= 92022525) {
        targetId.value = props.number - 91999956
      } else {
        targetId.value = props.number - 91999952
      }
      window.open(
        `http://172.23.1.44/otrs/index.pl?Action=AgentTicketZoom;TicketID=${targetId.value}`,
        '_blank'
      )
    }

    function kpiUpdate(newKpiSn) {
      console.log('hit kpiupdate function on DHSOTRSList')
      const newKpiDict = { otrsSn: props.sn, newKpiSn: newKpiSn }
      context.emit('adjustOTRSKpiOnlyListToPage', newKpiDict)
    }

    async function callKpi(curFlagKpiSn) {
      try {
        if (curFlagKpiSn !== 0) {
          // if curFlagKpiSn !== null, means this shift someone already udpate the KPI, so display it
          await axios
            .get(`https://${ServiceDomainLocal}:9487/kpi/view/${curFlagKpiSn}`)
            .then((res) => {
              console.log(res)
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

    async function callKpiHistory(targetTicketNumber) {
      try {
        if (targetTicketNumber) {
          await axios
            .get(`https://${ServiceDomainLocal}:9487/kpi/ticket/${targetTicketNumber}`)
            .then((res) => {
              if (res.data.length !== 0) {
                localKpiHistoryTemplate.value = res.data
              } else {
                $q.notify({
                  message: `<b>No KPI record for OTRS Ticket YTS${props.number} !</b>`,
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
        } else {
          await $q.notify({
            message: `<b>No KPI record for Note ${props.sequence} !</b>`,
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
      } catch (error) {
        await console.log(error)
      }
    }

    function popupKpiFile(date, shift, sn, path) {
      window.open(
        `https://${ServiceDomainLocal}:9487/query/kpi/${date}/${shift}/ticket/${sn}/${path}`,
        '_blank'
      )
    }

    function sortOutKpiResult() {
      axios
        .get(`https://${ServiceDomainLocal}:9487/sortout/kpi/otrs/${props.number}`)
        .then(async (res) => {
          const resultRequestHandler = res.data.fields.handler
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const resultTroubleShootHandler = res.data.fields.tsHandler
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const requestTHandlerSecond = res.data.fields.tsHandlerD
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const requestTParticipant = res.data.fields.tsParticipant
            .map(function (item) {
              return item.value
            })
            .join(', ')
          const kpiRequestType = res.data.fields.kpiType.value
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

    function callLog() {
      containerOfLog.value = true
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
        localResSet.summary = `
        <div><b>${mtnTitle}</b></div>
        <div><b>Vendor:</b> <span>${mtnObject[0].mtnVendor}</span></div>
        <div><b>Circuit ID:</b> <span>${mtnObject[0].mtnCircuit}</span></div>
        <div><b>Environment:</b> <span><font color="#0000FF">${mtnObject[0].mtnEnvironment}</font></span></div>
        <div><b>Affected customer:</b> <span><font color="#0000FF">${mtnObject[0].mtnAffectedCustomer}</font></span></div>
        <div><b>Start time:</b> <span><font color="#ff0000">${mtnObject[0].mtnStartTime}</font></span></div>
        <div><b>End time:</b> <span><font color="#ff0000">${mtnObject[0].mtnEndTime}</font></span></div>
        <div><b>Duration:</b> <span>${mtnObject[0].mtnDuration}</span></div>
      `
      } else if (mtnTitle === 'Other') {
        localResSet.summary = `
        <div><b>Maintenance Name:</b> <span>${mtnObject[0].mtnOtherName}</span></div>
        <div><b>Start time:</b> <span><font color="#ff0000">${mtnObject[0].mtnStartTime}</font></span></div>
        <div><b>End time:</b> <span><font color="#ff0000">${mtnObject[0].mtnEndTime}</font></span></div>
        <div><b>Duration:</b> <span>${mtnObject[0].mtnDuration}</span></div>
        <div><b>Risk analysis:</b> <span>${mtnObject[0].mtnOtherRiskAnalysis}</span></div>
      `
      } else {
        localResSet.summary = `
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

    async function adjustTicketMaintenanceStatus(isEnable) {
      const postData = reactive({
        curStatus: isEnable,
        targeOTRSTicketSn: props.sn
      })
      await axios
        .post(`https://${ServiceDomainLocal}:9487/bpOTRS/mtn/update`, postData)
        .then((res) => {
          console.log(res)
        })
        .catch((error) => {
          console.log(error)
        })
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
            adjustTicketMaintenanceStatus(true)
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
            adjustTicketMaintenanceStatus(false)
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
      () => [props.flagCloseTicket, props.summary, props.update_summary, props.update_by],
      (curValue, oldValue) => {
        curValue.forEach((num1, index) => {
          const num2 = oldValue[index]
          if (num1 !== num2) {
            if (index === 0) {
              localResSet.flagCloseTicket = num1
            } else if (index === 1) {
              localResSet.summary = num1
            } else if (index === 2) {
              localResSet.update_summary = num1
            } else if (index === 3) {
              localResSet.update_by = num1
            }
          }
        })
      },
      { deep: true }
    )

    watch(
      () => isLogin.isExtendedOTRS,
      (curValue, oldValue) => {
        expanded.value = curValue
      }
    )

    return {
      isLogin,
      ServiceDomainLocal,
      tabofCard,
      localEditorStatus,
      localResSet,
      reverseRefreshLockStatus,
      dialogUnderEditing,
      robOTRSeditor,
      closeOTRS,
      queryOTRSSeqList,
      summaryToolBar,
      updateSummaryToolBar,
      checkSummaryZone,
      checkUpdateSummaryZone,
      ConvertforeColor,
      adjustSummaryColor,
      adjustUpdateSummaryColor,
      foreColor,
      backColor,
      templatesSet,
      updateValueToSummary,
      updateValueToUpdateSummary,
      q1BtnDropDownColor,
      q1BtnDropDownBGColor,
      q2BtnDropDownColor,
      q2BtnDropDownBGColor,
      targetRef,
      targetRef2,
      group,
      options,
      notifyKpiAlert,
      hiddenAndUpdateEditor,
      hiddenAndCancelEditor,
      autoAdjustFontSize,
      returnCorrectColor,
      rollbackTicket,
      openNewPageToTicket,
      containerOfLog,
      kpiUpdate,
      localKpiTemplate,
      localKpiHistoryTemplate,
      callLog,
      callKpiHistory,
      callKpi,
      sortOutKpiResult,
      popupKpiFile,
      summaryUpdateByMtn,
      adjustTicketMaintenanceStatus,
      expanded
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

@keyframes scaleDraw {
  /*定義關鍵幀、scaleDrew是需要繫結到選擇器的關鍵幀名稱*/
  0% {
    transform: scale(1); /*開始為原始大小*/
  }
  25% {
    transform: scale(1.01); /*放大1.1倍*/
  }
  50% {
    transform: scale(1);
  }
  75% {
    transform: scale(1.01);
  }
}
.ballon {
  width: 150px;
  height: 200px;
  -webkit-animation-name: scaleDraw; /*關鍵幀名稱*/
  -webkit-animation-timing-function: ease-in-out; /*動畫的速度曲線*/
  -webkit-animation-iteration-count: 2; /*動畫播放的次數*/
  -webkit-animation-duration: 5s; /*動畫所花費的時間*/
}
</style>
