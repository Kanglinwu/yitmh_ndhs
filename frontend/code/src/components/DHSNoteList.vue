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
        <div class="text-h6">Note is under editing by {{ localResSet.update_by }}</div>
      </q-card-section>
      <!-- <q-card-section class="q-pt-none"> Click/Tap on the backdrop. </q-card-section> -->
      <q-card-actions align="right" class="bg-white text-teal">
        <q-btn flat label="Close" v-close-popup />
        <q-btn @click="robTheNote(sn)" flat label="Take Over" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <div v-if="sequence !== 99" class="row q-px-md q-pt-md q-pb-none row q-gutter-sm">
    <!-- {{ status }} {{ update_by }} -->
    <q-card :id="'note' + sn" flat bordered class="col-12">
      <q-card-section>
        <div class="row justify-start items-center text-h6" @click="expanded = !expanded">
          <q-icon
            color="red-8"
            :name="expanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
            class="q-pr-md cursor-pointer"
          />
          <span class="text-red-8 q-pr-xs">{{ sequence }}.</span>
          <span class="text-red-8">{{ customer }}</span>
        </div>
      </q-card-section>
      <q-slide-transition>
        <div v-show="expanded">
          <q-tabs align="left" v-model="tabofCard" class="text-teal">
            <q-tab label="Handover" name="one">
              <q-badge v-if="attachments.length !== 0" color="red" floating>{{
                attachments.length
              }}</q-badge>
            </q-tab>
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
                        v-if="kpi_result === 0"
                      >
                        Miss KPI Update!
                      </q-tooltip>
                      <q-btn
                        class="q-mt-xs q-ml-xs"
                        color="white"
                        text-color="primary"
                        label="Update"
                        :disable="kpi_result === 0"
                        @click="hiddenAndUpdateEditor(sn)"
                      >
                      </q-btn>
                    </span>
                    <q-btn
                      color="white"
                      text-color="primary"
                      label="Cancel"
                      @click="hiddenAndCancelEditor(sn)"
                    />
                  </div>
                </div>
                <div
                  v-show="options[0]['status']"
                  class="column bg-pink-1 q-px-md q-pb-md"
                >
                  <div class="col-12 text-center q-pa-md text-bold">KPI zone</div>
                  <DHSNoteListKpi
                    @adjustNoteKpiOnly="kpiUpdate"
                    :targetKpiSn="kpi_result"
                    :targetNoteSn="sn"
                    :targetKpiGroup="kpi_group"
                  />
                </div>
                <div
                  v-show="options[1]['status']"
                  class="column bg-light-blue-1 q-px-md q-pb-md"
                >
                  <div class="col-12 text-center q-pa-md text-bold">Attachment zone</div>
                  <!-- display -->
                  <div class="col-12 row justify-start q-gutter-xs q-mb-md">
                    <div
                      class="bg-light-blue-3 q-pa-xs"
                      v-for="(value, idx) in attachments"
                      :key="idx"
                    >
                      <!-- {{ value.fileName }} -->
                      <div class="row justify-center">
                        <img
                          class="rounded-borders"
                          :src="
                            'https://' +
                            ServiceDomainLocal +
                            ':9487/bpNote/attachment/review/' +
                            value.sn
                          "
                          style="height: 170px; max-width: 240px"
                        />
                      </div>
                      <div style="max-width: 240px" class="row justify-center text-wrap">
                        {{ value.fileName }}
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
                          target="__blank"
                          label="Detail"
                          :href="
                            'https://' +
                            ServiceDomainLocal +
                            ':9487/bpNote/attachment/get/' +
                            value.sn
                          "
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
                          @click="deleteAttachment(value.sn)"
                        />
                      </div>
                    </div>
                  </div>
                  <!-- uploader -->
                  <q-uploader
                    :url="
                      'https://' + ServiceDomainLocal + ':9487/bpNote/attachment/update'
                    "
                    label="attachment upload"
                    multiple
                    batch
                    @rejected="onRejected"
                    @uploaded="updateAttachmentList($event)"
                    class="col-12"
                    accept=".jpg, .docx, .xlsx, .pptx, .txt, .jpg, .pdf, .csv, .rar, .zip, .png"
                    :headers="[
                      { name: 'noteDbSn', value: sn },
                      { name: 'updater', value: isLogin.value }
                    ]"
                  />
                </div>
              </section>
              <section v-show="!localEditorStatus">
                <!-- check if this is new note -->
                <section v-if="localResSet.update_summary === 'New'">
                  <div class="custom-border-display note q-py-md rounded-borders">
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
                  <div class="custom-border-display note q-py-md rounded-borders">
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
                  <div class="custom-border-display note q-py-md rounded-borders">
                    <div class="bg-yellow-1 q-px-md text-bold">Current status:</div>
                    <div class="q-px-md" v-html="localResSet.summary"></div>
                  </div>
                </section>
                <div v-if="attachments.length !== 0">
                  <div class="bg-yellow-3 q-px-md q-mt-md q-mb-sm text-italic">
                    Following attachment(s) will be sent on this shift
                  </div>
                  <div class="flex q-px-md q-gutter-xs">
                    <div
                      v-for="(value, idx) in attachments"
                      :key="idx"
                      :class="
                        value.fileType !== 'png' && value.fileType !== 'jpg'
                          ? 'order-last'
                          : 'order-first'
                      "
                    >
                      <div
                        v-if="value.fileType !== 'png' && value.fileType !== 'jpg'"
                        class="cursor-pointer text-subtitle2 bg-blue-grey-2 q-pa-xs rounded-borders"
                        @click.self="popuptheattachment(value.sn)"
                      >
                        <q-avatar rounded>
                          <img
                            :src="
                              'https://' +
                              ServiceDomainLocal +
                              ':9487/bpNote/attachment/review/' +
                              value.sn
                            "
                          />
                        </q-avatar>
                        {{ value.fileName }}
                      </div>
                      <div v-else>
                        <img
                          @click.self="popuptheattachment(value.sn)"
                          class="cursor-pointer"
                          style="max-width: 75px"
                          :src="
                            'https://' +
                            ServiceDomainLocal +
                            ':9487/bpNote/attachment/review/' +
                            value.sn
                          "
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div class="row q-pt-sm q-gutter-sm text-right">
                  <q-btn
                    color="white"
                    text-color="primary"
                    label="Edit"
                    @click="reverseRefreshLockStatus"
                  />
                  <q-btn
                    color="white"
                    text-color="primary"
                    label="Delete"
                    @click="deleteNote"
                  />
                  <q-btn
                    color="white"
                    text-color="primary"
                    label="Move"
                    @click="queryNoteSeqList"
                  />
                </div>
              </section>
            </q-tab-panel>
            <q-tab-panel name="three">
              <DHSNoteListLog
                v-if="containerOfLog"
                :title="customer"
                source="fromOrigin"
              ></DHSNoteListLog>
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
                              '/note/' +
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
                    @click="callKpiHistory(kpi_group)"
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
                                '/note/' +
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
                    @click="callKpiHistory(kpi_group)"
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
                                '/note/' +
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
  <div v-else-if="isHidden" class="row q-pa-md row q-gutter-sm">
    <q-card flat bordered class="col-12">
      <q-card-section>
        <div class="row justify-between items-center text-italic text-h6">
          <span class="text-italic text-red-8"
            >note - <b>{{ customer }} </b> has been deleted on this shift.</span
          >
          <q-btn label="rollback" @click="rollbackNote"></q-btn>
          <!-- <span class="text-red-8 text-strike"></span> -->
        </div>
      </q-card-section>
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
  watch,
  onMounted,
  computed
} from 'vue'
import axios from 'axios'
import { useStore } from 'vuex'
import { scroll, useQuasar } from 'quasar'

import DHSNoteListKpi from './DHSNoteListKpi.vue'
import DHSNoteListLog from './DHSNoteListLog.vue'

export default defineComponent({
  name: 'DHSNoteList',
  components: {
    DHSNoteListKpi,
    DHSNoteListLog
  },
  emits: ['adjustNoteKpiOnlyListToPage'],
  props: {
    sn: Number,
    date: String,
    shift: String,
    sequence: Number,
    status: Number,
    customer: String,
    summary: String,
    update_summary: String,
    update_by: String,
    check_image: Number,
    kpi_group: Number,
    kpi_result: Number,
    isHidden: Boolean
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
    const localKpiHistoryTemplate = ref([])
    const localResSet = reactive({
      customer: props.customer,
      summary: props.summary,
      update_summary: props.update_summary ? props.update_summary : '',
      update_by: props.update_by
    })
    const containerOfLog = ref(false)
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

    const group = ref([
      props.kpi_result !== 0 ? 'op1' : 'fakeop1',
      props.check_image ? 'op2' : 'fakeop2'
    ])

    const options = reactive([
      {
        label: 'KPI',
        value: 'op1',
        status: Boolean(props.kpi_result),
        color: 'pink-2'
      },
      {
        label: 'ADD Attachment(s)',
        value: 'op2',
        status: Boolean(props.check_image),
        color: 'light-blue-2'
      }
    ])

    const attachments = ref([])

    const avatarSize = computed(() =>
      attachments.value.map(function (ele, index, object) {
        return 'max-width: 75px'
      })
    )

    const expanded = ref(false)

    function reverseRefreshLockStatus() {
      // final
      // isLogin.refreshNoteLocked = !isLogin.refreshNoteLocked
      // check component status -
      // # db status
      axios
        .get(`https://${ServiceDomainLocal}:9487/notes/query/${props.sn}`)
        .then((res) => {
          console.log(res.data)
          if (res.data[0].status !== 0) {
            localResSet.update_by = res.data[0].update_by
            if (isLogin.value !== res.data[0].update_by) {
              dialogUnderEditing.value = true
            } else {
              robTheNote(props.sn)
            }
          } else {
            robTheNote(props.sn)
          }
        })
        .catch((error) => {
          console.log(error)
        })
      // # local
      // const findItemByValueInList = isLogin.refreshNoteUnderEditingList.indexOf(props.sn)
    }

    function robTheNote(targetSn) {
      const postData = {
        newEditor: isLogin.value,
        targetNoteSn: props.sn,
        action: 'edit'
      }
      axios
        .post(`https://${ServiceDomainLocal}:9487/notes/update/status`, postData)
        .then((res) => {
          // update local status to display rich text edit
          localEditorStatus.value = true
          if (!isLogin.refreshNoteUnderEditingList.includes(props.sn)) {
            isLogin.refreshNoteUnderEditingList.push(props.sn)
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    // when user click the summary zone, will display the toolbar, and hide another one
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

    // TextEditor update button
    function hiddenAndUpdateEditor(noteSn) {
      // console.log('hit hiddenAndUpdateEditor')
      // console.log(`summary on local = ${localResSet.summary}`)
      // console.log(`old summary on db data = ${props.summary}`)
      // console.log(`update_summary on local = ${localResSet.update_summary}`)
      // console.log(`old update_summary on db data = ${props.update_summary}`)

      const updateChecker = ref(false) // to see if need to update to backend server

      // check if the value is change, summary and updateSummary
      if (localResSet.summary !== props.summary) {
        autoAdjustFontSize('curStatus')
        updateChecker.value = true
      }
      if (localResSet.update_summary !== props.update_summary) {
        // check if the localResSet.update_summary === <br>, why, becoz when user want to remove the update_summary, the rich text editor will insert <br>, that is why need to replace it if only <br> on update_summary
        if (localResSet.update_summary === '<br>') {
          localResSet.update_summary = ''
          updateChecker.value = true
        } else {
          autoAdjustFontSize('UpdateStatus')
          updateChecker.value = true
        }
      }

      // hidden TextEditor Toolbar
      summaryToolBar.value = []
      updateSummaryToolBar.value = []
      // hidde TextEditor
      localEditorStatus.value = false
      // release sn from refreshNoteUnderEditingList
      const indexOfSn = isLogin.refreshNoteUnderEditingList.indexOf(props.sn)
      if (indexOfSn > -1) {
        isLogin.refreshNoteUnderEditingList.splice(indexOfSn, 1)
      }

      // update the summary and updateSummary, unlock flagUnderEdit to db by axios
      if (updateChecker.value) {
        const postData = reactive({
          newEditor: isLogin.value,
          targetNoteSn: props.sn,
          action: 'update',
          summary: localResSet.summary,
          updateSummary: localResSet.update_summary
        })
        console.log(postData)
        axios
          .post(`https://${ServiceDomainLocal}:9487/notes/update/status`, postData)
          .then((res) => {
            console.log(res)
            isLogin.refreshNoteStep += 1
          })
          .catch((error) => {
            console.log(error)
          })
      } else {
        console.log(
          'nothing change, so system will not update the comment, but call the cancel to unlock the ticket'
        )
        // hiddenAndCancelEditor(targetTicketSn)
      }
    }

    // TextEditor cancel button
    function hiddenAndCancelEditor(noteSn) {
      // hidden TextEditor Toolbar
      summaryToolBar.value = []
      updateSummaryToolBar.value = []
      // // hidde TextEditor, this one is diff with ticket, reverse the default value
      localEditorStatus.value = false
      // release sn from refreshNoteUnderEditingList
      const indexOfSn = isLogin.refreshNoteUnderEditingList.indexOf(props.sn)
      if (indexOfSn > -1) {
        isLogin.refreshNoteUnderEditingList.splice(indexOfSn, 1)
      }

      for (const [key, value] of Object.entries(props)) {
        if (Object.keys(localResSet).includes(key)) {
          localResSet[key] = value
        }
      }

      // adjust ticket status
      const postData = reactive({
        targetNoteSn: props.sn,
        action: 'cancel'
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/notes/update/status`, postData)
        .then((res) => {
          console.log(res)
          // reload the note
          isLogin.refreshNoteStep += 1
        })
        .catch((error) => {
          console.log(error)
        })
      const ele = document.getElementById('note' + props.sn)
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
        console.log('done for the adjust')
      } else if (target === 'UpdateStatus') {
        proxy.targetRef2.runCmd('selectAll')
        proxy.targetRef2.runCmd('fontsize', 2)
        console.log('autoAdjustFontSize hit UpdateStatus')
      }
    }

    function deleteNote() {
      $q.dialog({
        title: 'Confirm',
        message: `<span class="text-red-12 text-bold">Delete</span> Note - ${props.customer}?`,
        html: true,
        cancel: true,
        persistent: true
      }).onOk((data) => {
        const postData = reactive({
          targetNoteSn: props.sn,
          action: 'delete'
        })
        axios
          .post(`https://${ServiceDomainLocal}:9487/notes/update/status`, postData)
          .then((res) => {
            console.log(res)
            isLogin.refreshNoteKey += 1
          })
          .catch((error) => {
            console.log(error)
          })
      })
    }

    function rollbackNote() {
      const postData = reactive({
        targetNoteSn: props.sn,
        action: 'rollback'
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/notes/update/status`, postData)
        .then((res) => {
          console.log(res)
          isLogin.refreshNoteKey += 1
        })
        .catch((error) => {
          console.log(error)
        })
    }

    async function queryNoteSeqList() {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/notes/query/list`)
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
          targetNoteSn: props.sn,
          action: 'moveSequence',
          newPosition: newPosition
        }
        axios
          .post(`https://${ServiceDomainLocal}:9487/notes/update/status`, postData)
          .then((res) => {
            console.log(res)
          })
          .catch((error) => {
            console.log(error)
          })
      })
    }

    function kpiUpdate(newKpiSn) {
      console.log('hit kpiupdate function on DHSNoteList')
      const emitObject = newKpiSn
      emitObject.noteSn = props.sn
      context.emit('adjustNoteKpiOnlyListToPage', emitObject)
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

    async function callKpiHistory(targetKpiGruopNumber) {
      console.log('hit callKpiHistory')
      try {
        if (targetKpiGruopNumber) {
          await axios
            .get(`https://${ServiceDomainLocal}:9487/kpi/note/${targetKpiGruopNumber}`)
            .then((res) => {
              if (res.data.length !== 0) {
                localKpiHistoryTemplate.value = res.data
              } else {
                $q.notify({
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
        `https://${ServiceDomainLocal}:9487/query/kpi/${date}/${shift}/note/${sn}/${path}`,
        '_blank'
      )
    }

    function sortOutKpiResult() {
      if (props.kpi_group) {
        axios
          .get(`https://${ServiceDomainLocal}:9487/kpi/noteSortOut/${props.kpi_group}`)
          .then(async (res) => {
            console.log(res)
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
      } else {
        $q.notify({
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
    }

    function callLog() {
      containerOfLog.value = true
    }

    function onRejected(rejectedEntries) {
      // Notify plugin needs to be installed
      // https://quasar.dev/quasar-plugins/notify#Installation
      $q.notify({
        type: 'negative',
        message: `${rejectedEntries.length} file(s) did not pass validation constraints`
      })
    }

    function deleteAttachment(targetAttachmentSn) {
      const postData = reactive({
        targetAttachmentSn: targetAttachmentSn,
        noteSn: props.sn
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/bpNote/attachment/delete`, postData)
        .then((res) => {
          attachments.value = res.data
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function updateAttachmentList(event) {
      axios
        .get(`https://${ServiceDomainLocal}:9487/bpNote/attachment/query/${props.sn}`)
        .then((res) => {
          attachments.value = res.data
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function popuptheattachment(targetSn) {
      window.open(
        `https://${ServiceDomainLocal}:9487/bpNote/attachment/get/${targetSn}`,
        '_blank'
      )
    }

    // function adjustTheAvatarSize(direction, targetAttachment, event) {
    //   const newEle = 'note' + props.sn
    //   const ele = document.getElementById(newEle)
    //   const target = getScrollTarget(ele)
    //   const offset = ele.offsetTop - 55
    //   const duration = 200
    //   switch (direction) {
    //     case 'in':
    //       avatarSize.value[targetAttachment] = 'max-width: 100%'
    //       break
    //     case 'out':
    //       avatarSize.value[targetAttachment] = 'max-width: 75px'
    //       setVerticalScrollPosition(target, offset, duration)
    //       break
    //   }
    // }

    onMounted(() => {
      if (props.check_image) {
        axios
          .get(`https://${ServiceDomainLocal}:9487/bpNote/attachment/query/${props.sn}`)
          .then((res) => {
            attachments.value = res.data
          })
          .catch((error) => {
            console.log(error)
          })
      }
    })

    watch(
      () => group.value,
      (curKey, oldKey) => {
        // add
        if (curKey.length > oldKey.length) {
          // find the new
          const newItem = curKey.filter((ele) => {
            return !oldKey.includes(ele)
          })
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
          options.forEach((optionItem) => {
            if (removeItem[0] === optionItem.value) {
              optionItem.status = false
            }
          })
        }
      }
    )

    watch(
      () => [props.customer, props.summary, props.update_summary, props.update_by],
      (curValue, oldValue) => {
        console.log('hit DHSNoteList Watch 4 targets')
        curValue.forEach((num1, index) => {
          const num2 = oldValue[index]
          if (num1 !== num2) {
            if (index === 0) {
              localResSet.customer = num1
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
      () => isLogin.isExtendedNote,
      (curValue, oldValue) => {
        console.log('watch - isExtendedNote on DHSNOTELIST')
        console.log(curValue)
        expanded.value = curValue
      }
    )

    return {
      isLogin,
      tabofCard,
      reverseRefreshLockStatus,
      ServiceDomainLocal,
      dialogUnderEditing,
      robTheNote,
      localEditorStatus,
      localResSet,
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
      deleteNote,
      rollbackNote,
      queryNoteSeqList,
      radio,
      kpiUpdate,
      callKpi,
      localKpiTemplate,
      localKpiHistoryTemplate,
      callKpiHistory,
      popupKpiFile,
      sortOutKpiResult,
      callLog,
      containerOfLog,
      onRejected,
      attachments,
      deleteAttachment,
      updateAttachmentList,
      popuptheattachment,
      // adjustTheAvatarSize,
      avatarSize,
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
</style>
