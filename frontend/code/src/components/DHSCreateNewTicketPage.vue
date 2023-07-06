<!-- @format -->

<template>
  <q-ajax-bar
    ref="axiosExecuteBar"
    position="bottom"
    color="positive"
    size="10px"
    skip-hijack
  />
  <q-card v-if="group === 'SYS'">
    <q-card-section>
      <div class="text-h6">Create {{ group }} ticket</div>
      <div class="text-subtitle2">by {{ editor }}</div>
    </q-card-section>
    <q-separator class="q-mx-none" inset />
    <q-stepper v-model="step" ref="stepper" color="primary" animated>
      <q-step :name="1" title="Title & Details" icon="subject" :done="step > 1">
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption"
            :class="[
              ticketCollectSetSys.title === '' ? 'text-italic text-red-9' : 'text-grey-9'
            ]"
          >
            * Title
          </div>
          <q-input
            class="col-12"
            name="name"
            v-model="ticketCollectSetSys.title"
            color="primary"
            stack-label
            outlined
            clearable
          />
        </div>
        <q-separator class="q-mx-none" inset />
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption"
            :class="[
              ticketCollectSetSys.description === ''
                ? 'text-italic text-red-9'
                : 'text-grey-9'
            ]"
          >
            * Description
          </div>
          <q-editor
            v-model="ticketCollectSetSys.description"
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
        </div>
        <q-separator class="q-mx-none" inset />
        <div class="row">
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption"
              :class="[
                ticketCollectSetSys.bizUnit.length === 0
                  ? 'text-italic text-red-9'
                  : 'text-grey-9'
              ]"
            >
              * Biz Unit, Multiple choices
            </div>
            <q-select
              class="col-12"
              outlined
              behavior="dialog"
              v-model="ticketCollectSetSys.bizUnit"
              multiple
              :options="sysJSMcustomFields.bizUnitOptions"
              use-chips
              stack-label
            />
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption"
              :class="[
                ticketCollectSetSys.category.length === 0
                  ? 'text-italic text-red-9'
                  : 'text-grey-9'
              ]"
            >
              * Category, Multiple choices
            </div>
            <q-select
              outlined
              behavior="dialog"
              v-model="ticketCollectSetSys.category"
              multiple
              :options="sysJSMcustomFields.categoryOptions"
              use-chips
              stack-label
            />
          </div>
        </div>
        <q-separator class="q-mx-none q-my-xs" inset />
        <div class="row justify-center">
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption"
              :class="[
                ticketCollectSetSys.startTime.length !== 16
                  ? 'text-italic text-red-9'
                  : 'text-grey-9'
              ]"
            >
              * Start Time
            </div>
            <q-input class="" filled v-model="ticketCollectSetSys.startTime">
              <template v-slot:prepend>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date
                      v-model="ticketCollectSetSys.startTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
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
                    <q-time
                      v-model="ticketCollectSetSys.startTime"
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
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div class="text-caption text-italic text-grey-9">End Time</div>
            <q-input class="" filled v-model="ticketCollectSetSys.endTime">
              <template v-slot:prepend>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="ticketCollectSetSys.endTime" mask="YYYY-MM-DD HH:mm">
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
                    <q-time
                      v-model="ticketCollectSetSys.endTime"
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
          </div>
        </div>
      </q-step>
      <q-step
        :name="2"
        title="Handler & Participant & Priority"
        icon="description"
        :done="step > 2"
      >
        <q-select
          v-model="ticketCollectSetSys.handler"
          :options="sysHandlerOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          label="* Handler, Choose one at least"
          :label-color="[ticketCollectSetSys.handler.length === 0 ? 'red-9' : 'grey-9']"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
        <q-select
          v-model="ticketCollectSetSys.participant"
          :options="sysParticipantOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          label="Participant, Optional"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
        <q-select
          v-model="ticketCollectSetSys.priority"
          :options="priorityOptions"
          behavior="dialog"
          filled
          stack-label
          :label-color="[ticketCollectSetSys.priority !== '' ? 'grey-9' : 'red-9']"
          label="* Priority"
          class="col-12 q-mb-xs"
        >
          <template v-slot:prepend>
            <q-icon name="flag" />
          </template>
        </q-select>
      </q-step>
      <q-step :name="3" title="Confirm" icon="checklist">
        <q-card>
          <q-card-section class="row justify-center">Content</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-pb-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Title</div>
            <div class="col text-body1">{{ ticketCollectSetSys.title }}</div>
          </q-card-section>
          <q-card-section class="row q-pt-xs q-pb-md">
            <div class="col-1 text-bold text-subtitle1">Description</div>
            <div class="col text-body1" v-html="ticketCollectSetSys.description"></div>
          </q-card-section>
          <q-separator inset />
          <q-card-section class="row justify-center">JSM Details</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-pb-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Biz Unit</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetSys.bizUnit" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Category</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetSys.category" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Handler</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetSys.handler" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section
            v-if="ticketCollectSetSys.participant.length !== 0"
            class="row q-py-xs"
          >
            <div class="col-1 text-bold text-subtitle1">Participant</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetSys.participant" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Priority</div>
            <div class="col text-body1">
              <q-badge
                v-if="ticketCollectSetSys.priority === 'Highest'"
                outline
                color="negative"
                :label="ticketCollectSetSys.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetSys.priority === 'High'"
                outline
                color="negative"
                :label="ticketCollectSetSys.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetSys.priority === 'Medium'"
                outline
                color="warning"
                :label="ticketCollectSetSys.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetSys.priority === 'Low'"
                outline
                color="info"
                :label="ticketCollectSetSys.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetSys.priority === 'Lowest'"
                outline
                color="info"
                :label="ticketCollectSetSys.priority"
              />
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Time</div>
            <div class="col text-body1"></div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Start</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetSys.startTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetSys.duration" class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>End</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetSys.endTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetSys.duration" class="row q-pb-md q-pt-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Duration</li>
            </div>
            <div class="col text-body1">
              <q-badge
                :label="ticketCollectSetSys.duration[0]"
                outline
                color="secondary"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-step>

      <template v-slot:navigation>
        <q-separator class="q-mx-none q-mb-md" inset />
        <q-stepper-navigation>
          <q-btn
            @click="stepperController"
            color="primary"
            :label="step === 3 ? 'Update' : 'Continue'"
            :disable="defineSysNextButtonStatus"
          />
          <q-btn
            v-if="step > 1"
            flat
            color="primary"
            @click="$refs.stepper.previous()"
            label="Back"
            class="q-ml-sm"
          />
          <q-btn
            flat
            color="blue-grey-4"
            @click="cancelThis"
            label="Cancel"
            class="q-ml-sm"
          />
        </q-stepper-navigation>
      </template>
    </q-stepper>
  </q-card>

  <q-card v-else-if="group === 'NET'">
    <q-card-section>
      <div class="text-h6">Create {{ group }} ticket</div>
      <div class="text-subtitle2">by {{ editor }}</div>
    </q-card-section>
    <q-separator class="q-mx-none" inset />
    <q-stepper v-model="step" ref="stepper" color="primary" animated>
      <q-step :name="1" title="Title & Details" icon="subject" :done="step > 1">
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption"
            :class="[
              ticketCollectSetNet.title === '' ? 'text-italic text-red-9' : 'text-grey-9'
            ]"
          >
            * Title
          </div>
          <q-input
            class="col-12"
            name="name"
            v-model="ticketCollectSetNet.title"
            color="primary"
            stack-label
            outlined
            clearable
          />
        </div>
        <q-separator class="q-mx-none" inset />
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption"
            :class="[
              ticketCollectSetNet.description === ''
                ? 'text-italic text-red-9'
                : 'text-grey-9'
            ]"
          >
            * Description
          </div>
          <q-editor
            v-model="ticketCollectSetNet.description"
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
        </div>
        <q-separator class="q-mx-none" inset />
        <div class="row">
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption"
              :class="[
                ticketCollectSetNet.category ? 'text-grey-9' : 'text-italic text-red-9'
              ]"
            >
              * Category, Single choice
            </div>
            <q-select
              outlined
              behavior="dialog"
              v-model="ticketCollectSetNet.category"
              :options="netJSMcustomFields.categoryOptions"
              use-chips
              stack-label
            />
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption"
              :class="[
                ticketCollectSetNet.infra.length === 0
                  ? 'text-italic text-red-9'
                  : 'text-grey-9'
              ]"
            >
              * Infra, Multiple choices
            </div>
            <q-select
              class="col-12"
              outlined
              behavior="dialog"
              v-model="ticketCollectSetNet.infra"
              multiple
              :options="netJSMcustomFields.infraOptions"
              use-chips
              stack-label
            />
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption"
              :class="[
                ticketCollectSetNet.facilities.length === 0
                  ? 'text-italic text-red-9'
                  : 'text-grey-9'
              ]"
            >
              * Facilities, Multiple choices
            </div>
            <q-select
              outlined
              behavior="dialog"
              v-model="ticketCollectSetNet.facilities"
              :options="netJSMcustomFields.facilitiesOptions"
              use-chips
              stack-label
              multiple
            />
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div class="text-caption text-italic text-grey-9">
              Vendor Support, Multiple choices
            </div>
            <q-select
              outlined
              behavior="dialog"
              v-model="ticketCollectSetNet.vendorSupport"
              :options="netJSMcustomFields.vendorOptions"
              use-chips
              stack-label
              multiple
            />
          </div>
        </div>
        <q-separator class="q-mx-none q-my-xs" inset />
        <div class="row">
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption"
              :class="[
                ticketCollectSetNet.startTime.length !== 16
                  ? 'text-italic text-red-9'
                  : 'text-grey-9'
              ]"
            >
              * Start Time
            </div>
            <q-input class="" filled v-model="ticketCollectSetNet.startTime">
              <template v-slot:prepend>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date
                      v-model="ticketCollectSetNet.startTime"
                      mask="YYYY-MM-DD HH:mm"
                    >
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
                    <q-time
                      v-model="ticketCollectSetNet.startTime"
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
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div class="text-caption text-italic text-grey-9">End Time</div>
            <q-input class="" filled v-model="ticketCollectSetNet.endTime">
              <template v-slot:prepend>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                    <q-date v-model="ticketCollectSetNet.endTime" mask="YYYY-MM-DD HH:mm">
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
                    <q-time
                      v-model="ticketCollectSetNet.endTime"
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
          </div>
        </div>
      </q-step>
      <q-step :name="2" title="Handler & Participant" icon="people" :done="step > 2">
        <q-select
          v-model="ticketCollectSetNet.handler"
          :options="netHandlerOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          :label-color="[ticketCollectSetNet.handler.length === 0 ? 'red-9' : 'grey-9']"
          label="* Handler, Choose one at least"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
        <q-select
          v-model="ticketCollectSetNet.participant"
          :options="netParticipantOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          label="Participant, Optional"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
      </q-step>
      <q-step :name="3" title="Confirm" icon="checklist">
        <q-card>
          <q-card-section class="row justify-center">Content</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-pb-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Title</div>
            <div class="col text-body1">{{ ticketCollectSetNet.title }}</div>
          </q-card-section>
          <q-card-section class="row q-pt-xs q-pb-md">
            <div class="col-1 text-bold text-subtitle1">Description</div>
            <div class="col text-body1" v-html="ticketCollectSetNet.description"></div>
          </q-card-section>
          <q-separator inset />
          <q-card-section class="row justify-center">JSM Details</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-pb-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Infra</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetNet.Infra" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Category</div>
            <div class="col text-body1">
              <q-badge
                class="q-mr-sm"
                outline
                color="secondary"
                :label="ticketCollectSetNet.category"
              />
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Facilities</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetNet.facilities" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section
            v-if="ticketCollectSetNet.vendorSupport.length !== 0"
            class="row q-py-xs"
          >
            <div class="col-1 text-bold text-subtitle1">Vendor Support</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetNet.vendorSupport" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Handler</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetNet.handler" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section
            v-if="ticketCollectSetNet.participant.length !== 0"
            class="row q-py-xs"
          >
            <div class="col-1 text-bold text-subtitle1">Participant</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetNet.participant" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Time</div>
            <div class="col text-body1"></div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Start</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetNet.startTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetNet.duration" class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>End</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetNet.endTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetNet.duration" class="row q-pb-md q-pt-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Duration</li>
            </div>
            <div class="col text-body1">
              <q-badge
                :label="ticketCollectSetNet.duration[0]"
                outline
                color="secondary"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-step>

      <template v-slot:navigation>
        <q-separator class="q-mx-none q-mb-md" inset />
        <q-stepper-navigation>
          <q-btn
            @click="stepperController"
            color="primary"
            :label="step === 3 ? 'Update' : 'Continue'"
            :disable="defineNetNextButtonStatus"
          />
          <q-btn
            v-if="step > 1"
            flat
            color="primary"
            @click="$refs.stepper.previous()"
            label="Back"
            class="q-ml-sm"
          />
          <q-btn
            flat
            color="blue-grey-4"
            @click="cancelThis"
            label="Cancel"
            class="q-ml-sm"
          />
        </q-stepper-navigation>
      </template>
    </q-stepper>
  </q-card>

  <q-card v-else-if="group === 'DBA'">
    <q-card-section>
      <div class="text-h6">Create {{ group }} ticket</div>
      <div class="text-subtitle2">by {{ editor }}</div>
    </q-card-section>
    <q-separator class="q-mx-none" inset />
    <q-stepper v-model="step" ref="stepper" color="primary" animated>
      <q-step :name="1" title="Title & Details" icon="subject" :done="step > 1">
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption q-px-sm"
            :class="[
              ticketCollectSetDba.title === '' ? 'text-red-9 text-italic' : 'text-grey-9'
            ]"
          >
            * Title
          </div>
          <q-input
            class="col-12"
            name="name"
            v-model="ticketCollectSetDba.title"
            color="primary"
            stack-label
            outlined
            clearable
          />
        </div>
        <q-separator class="q-mx-none" inset />
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption q-px-sm"
            :class="[
              ticketCollectSetDba.description === ''
                ? 'text-red-9 text-italic'
                : 'text-grey-9'
            ]"
          >
            * Description
          </div>
          <q-editor
            v-model="ticketCollectSetDba.description"
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
        </div>
        <q-separator class="q-mx-none q-my-xs" inset />
        <div class="row">
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption q-px-sm"
              :class="[
                ticketCollectSetDba.category.length === 0
                  ? 'text-red-9 text-italic'
                  : 'text-grey-9'
              ]"
            >
              * Category, Multiple choices
            </div>
            <q-select
              outlined
              behavior="dialog"
              multiple
              v-model="ticketCollectSetDba.category"
              :options="dbaJSMcustomFields.categoryOptions"
              use-chips
              stack-label
            />
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption q-px-sm"
              :class="[
                ticketCollectSetDba.bizUnit.length === 0
                  ? 'text-red-9 text-italic'
                  : 'text-grey-9'
              ]"
            >
              * Biz Unit, Multiple choices
            </div>
            <q-select
              class="col-12"
              outlined
              behavior="dialog"
              v-model="ticketCollectSetDba.bizUnit"
              multiple
              :options="dbaJSMcustomFields.bizUnitOptions"
              use-chips
              stack-label
            />
          </div>
          <q-separator vertical inset />
          <div class="col q-pa-sm bg-grey-2">
            <div
              class="text-caption q-px-sm"
              :class="[
                ticketCollectSetDba.priority ? 'text-grey-9' : 'text-red-9 text-italic'
              ]"
            >
              * Priority, Single choices
            </div>
            <q-select
              class="col-12"
              outlined
              behavior="dialog"
              v-model="ticketCollectSetDba.priority"
              :options="priorityOptions"
              use-chips
              stack-label
            />
          </div>
          <q-separator vertical inset />
          <div class="col column q-pa-sm bg-grey-2">
            <div class="text-caption text-italic text-grey-9 q-px-sm">Service impact</div>
            <div class="col q-pt-xs">
              <q-toggle
                v-model="ticketCollectSetDba.isImpact"
                checked-icon="priority_high"
                color="red"
                :label="ticketCollectSetDba.isImpact ? 'Yes' : 'No'"
                unchecked-icon="check"
              />
            </div>
          </div>
        </div>
        <q-separator class="q-mx-none q-my-xs" inset />
        <div class="q-pa-sm bg-grey-2">
          <div class="row justify-start">
            <div class="col q-pa-sm bg-grey-2">
              <div
                class="text-caption"
                :class="[
                  ticketCollectSetDba.startTime.length !== 16
                    ? 'text-red-9 text-italic'
                    : 'text-grey-9'
                ]"
              >
                * Start Time
              </div>
              <q-input class="" filled v-model="ticketCollectSetDba.startTime">
                <template v-slot:prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date
                        v-model="ticketCollectSetDba.startTime"
                        mask="YYYY-MM-DD HH:mm"
                      >
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
                      <q-time
                        v-model="ticketCollectSetDba.startTime"
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
            </div>
            <q-separator vertical inset />
            <div class="col q-pa-sm bg-grey-2">
              <div
                class="text-caption"
                :class="[
                  ticketCollectSetDba.endTime.length !== 16
                    ? 'text-red-9 text-italic'
                    : 'text-grey-9'
                ]"
              >
                * End Time
              </div>
              <q-input class="" filled v-model="ticketCollectSetDba.endTime">
                <template v-slot:prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date
                        v-model="ticketCollectSetDba.endTime"
                        mask="YYYY-MM-DD HH:mm"
                      >
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
                      <q-time
                        v-model="ticketCollectSetDba.endTime"
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
            </div>
            <q-separator vertical inset />
            <div class="col column q-pa-sm bg-grey-2">
              <div
                class="text-caption q-px-sm"
                :class="[
                  ticketCollectSetDba.duration ? 'text-grey-9' : 'text-italic text-red-9'
                ]"
              >
                * Auto calculate working minutes
              </div>
              <div v-if="ticketCollectSetDba.duration" class="col q-pt-xs text-center">
                <div>
                  <q-icon
                    class="q-pr-sm q-py-sm"
                    size="lg"
                    name="task_alt"
                    color="green-9"
                  /><span>{{ ticketCollectSetDba.duration[0] }}</span>
                </div>
                <!-- <div>{{ticketCollectSetDba.duration[0]}}</div> -->
              </div>
              <div v-else class="col self-center content-center">
                <q-icon class="q-py-sm" size="lg" name="error" color="red-9" />
              </div>
            </div>
          </div>
        </div>
        <q-separator class="q-mx-none" inset />
      </q-step>
      <q-step :name="2" title="Handler & Participant" icon="description" :done="step > 4">
        <q-select
          v-model="ticketCollectSetDba.handler"
          :options="dbaHandlerOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          :label-color="[ticketCollectSetDba.handler.length === 0 ? 'red-9' : 'grey-9']"
          label="* Handler, Choose one at least"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
        <q-select
          v-model="ticketCollectSetDba.participant"
          :options="dbaParticipantOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          label="Participant, Optional"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
      </q-step>
      <q-step :name="3" title="Confirm" icon="checklist">
        <q-card>
          <q-card-section class="row justify-center">Content</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-pb-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Title</div>
            <div class="col text-body1">{{ ticketCollectSetDba.title }}</div>
          </q-card-section>
          <q-card-section class="row q-pt-xs q-pb-md">
            <div class="col-1 text-bold text-subtitle1">Description</div>
            <div class="col text-body1" v-html="ticketCollectSetDba.description"></div>
          </q-card-section>
          <q-separator inset />
          <q-card-section class="row justify-center">JSM Details</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-pb-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Infra</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetDba.bizUnit" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Category</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetDba.category" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Service Impact</div>
            <div class="col text-body1">
              <q-badge
                v-if="ticketCollectSetDba.isImpact"
                class="q-mr-sm"
                outline
                color="negative"
                label="Yes"
              />
              <q-badge v-else class="q-mr-sm" outline color="positive" label="No" />
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Priority</div>
            <div class="col text-body1">
              <q-badge
                v-if="ticketCollectSetDba.priority === 'Highest'"
                outline
                color="negative"
                :label="ticketCollectSetDba.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetDba.priority === 'High'"
                outline
                color="negative"
                :label="ticketCollectSetDba.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetDba.priority === 'Medium'"
                outline
                color="warning"
                :label="ticketCollectSetDba.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetDba.priority === 'Low'"
                outline
                color="info"
                :label="ticketCollectSetDba.priority"
              />
              <q-badge
                v-else-if="ticketCollectSetDba.priority === 'Lowest'"
                outline
                color="info"
                :label="ticketCollectSetDba.priority"
              />
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Handler</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetDba.handler" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section
            v-if="ticketCollectSetDba.participant.length !== 0"
            class="row q-py-xs"
          >
            <div class="col-1 text-bold text-subtitle1">Participant</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetDba.participant" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Time</div>
            <div class="col text-body1"></div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Start</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetDba.startTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>End</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetDba.endTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section class="row q-pb-md q-pt-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Work Hour</li>
            </div>
            <div class="col text-body1">
              <q-badge
                :label="ticketCollectSetDba.duration[0]"
                outline
                color="secondary"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-step>

      <template v-slot:navigation>
        <q-separator class="q-mx-none q-mb-md" inset />
        <q-stepper-navigation>
          <q-btn
            @click="stepperController"
            color="primary"
            :label="step === 3 ? 'Update' : 'Continue'"
            :disable="defineDbaNextButtonStatus"
          />
          <q-btn
            v-if="step > 1"
            flat
            color="primary"
            @click="$refs.stepper.previous()"
            label="Back"
            class="q-ml-sm"
          />
          <q-btn
            flat
            color="blue-grey-4"
            @click="cancelThis"
            label="Cancel"
            class="q-ml-sm"
          />
        </q-stepper-navigation>
      </template>
    </q-stepper>
  </q-card>

  <q-card v-else-if="group === 'OPS'">
    <q-card-section>
      <div class="text-h6">Create {{ group }} ticket</div>
      <div class="text-subtitle2">by {{ editor }}</div>
    </q-card-section>
    <q-separator class="q-mx-none" inset />
    <q-stepper v-model="step" ref="stepper" color="primary" animated>
      <q-step :name="1" title="Title & Details" icon="subject" :done="step > 1">
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption q-px-sm"
            :class="[
              ticketCollectSetOps.title === '' ? 'text-italic text-red-9' : 'text-grey-9'
            ]"
          >
            * Title
          </div>
          <q-input
            class="col-12"
            name="name"
            v-model="ticketCollectSetOps.title"
            color="primary"
            stack-label
            outlined
            clearable
          />
        </div>
        <q-separator class="q-mx-none" inset />
        <div class="q-pa-sm bg-grey-2">
          <div
            class="text-caption q-px-sm"
            :class="[
              ticketCollectSetOps.description === ''
                ? 'text-italic text-red-9'
                : 'text-grey-9'
            ]"
          >
            * Description
          </div>
          <q-editor
            v-model="ticketCollectSetOps.description"
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
                    <q-item v-for="i in opsTemplatesSet" :key="i.name" clickable>
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
        <q-separator class="q-mx-none" inset />
        <div class="q-pa-sm bg-grey-2">
          <div class="row justify-start">
            <section class="col">
              <div
                class="text-caption q-px-sm"
                :class="[
                  ticketCollectSetOps.category ? 'text-grey-9' : 'text-italic text-red-9'
                ]"
              >
                * Category, Single choices
              </div>
              <q-select
                dense
                class="col-12"
                outlined
                behavior="dialog"
                v-model="ticketCollectSetOps.category"
                :options="opsJSMcustomFields.categoryOptions"
                use-chips
                stack-label
              />
              {{ ticketCollectSetOps.category }}
            </section>
            <q-separator class="q-mx-sm q-my-none" vertical inset />
            <section class="col">
              <div
                class="text-caption q-px-sm"
                :class="[
                  ticketCollectSetOps.infra.length === 0
                    ? 'text-italic text-red-9'
                    : 'text-grey-9'
                ]"
              >
                * Infra, Multiple choices
              </div>
              <q-select
                dense
                class="col-12"
                outlined
                behavior="dialog"
                v-model="ticketCollectSetOps.infra"
                multiple
                :options="opsJSMcustomFields.infraOptions"
                use-chips
                stack-label
              />
            </section>
            <q-separator class="q-mx-sm q-my-none" vertical inset />
            <section class="col">
              <div
                class="text-caption q-px-sm"
                :class="[
                  ticketCollectSetOps.bizUnit.length === 0
                    ? 'text-italic text-red-9'
                    : 'text-grey-9'
                ]"
              >
                * BizUnit, Multiple choices
              </div>
              <q-select
                dense
                class="col-12"
                outlined
                behavior="dialog"
                v-model="ticketCollectSetOps.bizUnit"
                multiple
                :options="opsJSMcustomFields.bizUnitOptions"
                use-chips
                stack-label
              />
            </section>
          </div>
        </div>
        <q-separator class="q-mx-none q-my-xs" inset />
        <div class="q-pa-sm bg-grey-2">
          <div class="row justify-start">
            <div class="col q-pa-sm bg-grey-2">
              <div
                class="text-caption"
                :class="[
                  ticketCollectSetOps.startTime.length !== 16
                    ? 'text-italic text-red-9'
                    : 'text-grey-9'
                ]"
              >
                * Start Time
              </div>
              <q-input dense class="" filled v-model="ticketCollectSetOps.startTime">
                <template v-slot:prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date
                        v-model="ticketCollectSetOps.startTime"
                        mask="YYYY-MM-DD HH:mm"
                      >
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
                      <q-time
                        v-model="ticketCollectSetOps.startTime"
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
            </div>
            <q-separator vertical inset />
            <div class="col q-pa-sm bg-grey-2">
              <div class="text-caption text-italic text-grey-9">End Time</div>
              <q-input dense class="" filled v-model="ticketCollectSetOps.endTime">
                <template v-slot:prepend>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date
                        v-model="ticketCollectSetOps.endTime"
                        mask="YYYY-MM-DD HH:mm"
                      >
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
                      <q-time
                        v-model="ticketCollectSetOps.endTime"
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
            </div>
          </div>
        </div>
      </q-step>
      <q-step :name="2" title="handler & participants" icon="people" :done="step > 2">
        <q-select
          v-model="ticketCollectSetOps.handler"
          :options="opsHandlerOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          label="* Handler, Choose one at least"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
        <q-select
          v-model="ticketCollectSetOps.participant"
          :options="opsParticipantOptions"
          behavior="dialog"
          filled
          multiple
          use-chips
          stack-label
          emit-value
          map-options
          label="Participant, Optional"
          class="col-12 q-mb-xs"
          option-value="desc"
          option-label="desc"
          option-disable="inactive"
        >
          <template v-slot:prepend>
            <q-icon name="fas fa-users" />
          </template>
        </q-select>
      </q-step>
      <q-step :name="3" title="Confirm" icon="checklist" :done="step > 3">
        <q-card>
          <q-card-section class="row justify-center">Content</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-pb-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Title</div>
            <div class="col text-body1">{{ ticketCollectSetOps.title }}</div>
          </q-card-section>
          <q-card-section class="row q-pt-xs q-pb-md">
            <div class="col-1 text-bold text-subtitle1">Description</div>
            <div class="col text-body1" v-html="ticketCollectSetOps.description"></div>
          </q-card-section>
          <q-separator inset />
          <q-card-section class="row justify-center">JSM Details</q-card-section>
          <q-separator inset />
          <q-card-section class="row q-py-xs q-pt-md">
            <div class="col-1 text-bold text-subtitle1">Category</div>
            <div class="col text-body1">
              <q-badge
                class="q-mr-sm"
                outline
                color="secondary"
                :label="ticketCollectSetOps.category"
              />
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Infra</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetOps.infra" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Biz Unit</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetOps.bizUnit" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Handler</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetOps.handler" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section
            v-if="ticketCollectSetOps.participant.length !== 0"
            class="row q-py-xs"
          >
            <div class="col-1 text-bold text-subtitle1">Participant</div>
            <div class="col text-body1">
              <span v-for="x in ticketCollectSetOps.participant" :key="x">
                <q-badge class="q-mr-sm" outline color="secondary" :label="x" />
              </span>
            </div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetOps.duration" class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">Time</div>
            <div class="col text-body1"></div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetOps.duration" class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Start</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetOps.startTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetOps.duration" class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>End</li>
            </div>
            <div class="col text-body1">
              <q-badge :label="ticketCollectSetOps.endTime" outline color="secondary" />
            </div>
          </q-card-section>
          <q-card-section v-if="ticketCollectSetOps.duration" class="row q-py-xs">
            <div class="col-1 text-bold text-subtitle1">
              <li>Duration</li>
            </div>
            <div class="col text-body1">
              <q-badge
                :label="ticketCollectSetOps.duration[0]"
                outline
                color="secondary"
              />
            </div>
          </q-card-section>
        </q-card>
      </q-step>
      <template v-slot:navigation>
        <q-separator class="q-mx-none q-mb-md" inset />
        <q-stepper-navigation>
          <q-btn
            @click="stepperController"
            color="primary"
            :label="step === 3 ? 'Update' : 'Continue'"
            :disable="defineOpsNextButtonStatus"
          />
          <q-btn
            v-if="step > 1"
            flat
            color="primary"
            @click="$refs.stepper.previous()"
            label="Back"
            class="q-ml-sm"
          />
          <q-btn
            flat
            color="blue-grey-4"
            @click="cancelThis"
            label="Cancel"
            class="q-ml-sm"
          />
        </q-stepper-navigation>
      </template>
    </q-stepper>
  </q-card>
</template>

<script>
import {
  defineComponent,
  reactive,
  ref,
  computed,
  getCurrentInstance,
  watch,
  onMounted
} from 'vue'
import { date, useQuasar } from 'quasar'
import _ from 'lodash'
import axios from 'axios'
import { useStore } from 'vuex'
// import { defineComponent, ref, reactive, computed, onMounted, watch } from 'vue'
export default defineComponent({
  name: 'DHSCreateNewTicketPage',
  props: {
    group: String,
    editor: String
  },
  emits: ['triggerByChildren'],
  setup(props, context) {
    const $q = useQuasar()
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const step = ref(1)
    const { proxy } = getCurrentInstance()
    // default option
    const priorityOptions = ['Highest', 'High', 'Medium', 'Low', 'Lowest']

    // richEditor start
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
      ['token3'],
      ['fullscreen']
    ])
    const foreColor = ref('#000000')
    const backColor = ref('#ffff00')
    const targetRef = ref(null)
    const kpiEditorBtnDropDownColor = ref(null)
    const kpiEditorBtnDropDownBGColor = ref(null)
    // richEditor end

    // loading bar
    const axiosExecuteBar = ref(null)

    const isLockUpdateNewTicketButton = ref(false)

    // For OPS
    const ticketCollectSetOps = reactive({
      title: '',
      description: '',
      infra: [],
      bizUnit: [],
      category: null,
      handler: [props.editor.replace('.', ' ')],
      participant: [],
      priority: null,
      startTime: date.formatDate(Date.now(), 'YYYY-MM-DD HH:mm'),
      endTime: '',
      duration: computed(() => {
        if (
          date.isValid(ticketCollectSetOps.startTime) &&
          date.isValid(ticketCollectSetOps.endTime)
        ) {
          const startTimeObject = new Date(ticketCollectSetOps.startTime)
          const endTimeObject = new Date(ticketCollectSetOps.endTime)
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
    const opsDefaultPersonOptions = ref([
      {
        desc: 'Aiden Tan',
        inactive: false
      },
      {
        desc: 'Albert Liu',
        inactive: false
      },
      {
        desc: 'Alex lin',
        inactive: false
      },
      {
        desc: 'Asky Huang',
        inactive: false
      },
      {
        desc: 'Bayu Winursito',
        inactive: false
      },
      {
        desc: 'Bob Lin',
        inactive: false
      },
      {
        desc: 'Cadalora Lin',
        inactive: false
      },
      {
        desc: 'Cyril Rejas',
        inactive: false
      },
      {
        desc: 'Daniel Liu',
        inactive: false
      },
      {
        desc: 'Danny Wu',
        inactive: false
      },
      {
        desc: 'Eric Kao',
        inactive: false
      },
      {
        desc: 'Gary Wu',
        inactive: false
      },
      {
        desc: 'Huck Chen',
        inactive: false
      },
      {
        desc: 'Ivan Chu',
        inactive: false
      },
      {
        desc: 'Keven Chang',
        inactive: false
      },
      {
        desc: 'Larry Tsou',
        inactive: false
      },
      {
        desc: 'Thurston Chao',
        inactive: false
      },
      {
        desc: 'Rorschach Ye',
        inactive: false
      }
    ])
    const opsHandlerOptions = _.cloneDeep(opsDefaultPersonOptions)
    const opsParticipantOptions = _.cloneDeep(opsDefaultPersonOptions)
    const opsJSMcustomFields = reactive({})
    const opsTemplatesSet = reactive([
      {
        name: 'KB Team',
        value: [
          {
            name: 'Example1',
            value: `
              <div><b>Updater</b>: ${props.editor}</div>
              <div><b>Date</b>: ${date.formatDate(Date.now(), 'YYYY-MM-DD')}</div>
              <div><b>Type</b>:</div>
              <div><b>Detail</b>:</div>
              <div><b>Link</b>:</div>
              <div><b>Comment</b>:</div>`
          }
        ]
      }
    ])
    const defineOpsNextButtonStatus = computed(() => {
      if (step.value === 1) {
        return (
          ticketCollectSetOps.title === '' ||
          ticketCollectSetOps.description === '' ||
          ticketCollectSetOps.description.length > 30000 ||
          ticketCollectSetOps.infra.length === 0 ||
          ticketCollectSetOps.bizUnit.length === 0 ||
          ticketCollectSetOps.category === null
        )
      } else if (step.value === 2) {
        return ticketCollectSetOps.handler.length === 0
      } else {
        if (isLockUpdateNewTicketButton.value) {
          return true
        } else {
          return false
        }
      }
    })

    // For DBA
    const ticketCollectSetDba = reactive({
      title: '',
      description: '',
      bizUnit: [],
      category: [],
      isImpact: false,
      handler: [],
      participant: [],
      priority: null,
      startTime: date.formatDate(Date.now(), 'YYYY-MM-DD HH:mm'),
      endTime: '',
      duration: computed(() => {
        if (
          date.isValid(ticketCollectSetDba.startTime) &&
          date.isValid(ticketCollectSetDba.endTime)
        ) {
          const startTimeObject = new Date(ticketCollectSetDba.startTime)
          const endTimeObject = new Date(ticketCollectSetDba.endTime)
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
    const dbaDefaultPersonOptions = ref([
      {
        desc: 'David Tung',
        inactive: false
      },
      {
        desc: 'Tony Wu',
        inactive: false
      },
      {
        desc: 'Albert Huang',
        inactive: false
      },
      {
        desc: 'Robert Lin',
        inactive: false
      },
      {
        desc: 'Stanley Chen',
        inactive: false
      },
      {
        desc: 'Demon Wu',
        inactive: false
      },
      {
        desc: 'Carny Chou',
        inactive: false
      },
      {
        desc: 'Austin Chang',
        inactive: false
      },
      {
        desc: 'William Liu',
        inactive: false
      }
    ])
    const dbaHandlerOptions = _.cloneDeep(dbaDefaultPersonOptions)
    const dbaParticipantOptions = _.cloneDeep(dbaDefaultPersonOptions)
    const dbaJSMcustomFields = reactive({})
    // const dbaJSMcustomFields = reactive({
    //   bizUnitOptions: [
    //     'INFRA-APP',
    //     'INFRA-CEM',
    //     'INFRA-CWD',
    //     'INFRA-DBA',
    //     'INFRA-NET',
    //     'INFRA-OPS',
    //     'INFRA-SYS',
    //     'INFRA-TS',
    //     'XN-EA',
    //     'XN-IL',
    //     'XN-LDR',
    //     'XN-NBG',
    //     'XN-RTX',
    //     'XN-SBK',
    //     'XN-188Asia',
    //     'XN-BI',
    //     'XN-CAS',
    //     'XN-OFC',
    //     'TRS',
    //     'Others'
    //   ],
    //   categoryOptions: [
    //     'Deployment',
    //     'DB-Request(Instance/DB/Schema)',
    //     'DB-Decom',
    //     'DB-Security',
    //     'DB-Config',
    //     'DB-Add/Resize file',
    //     'DB-Monitor System',
    //     'DB-Others',
    //     'Disk Extend',
    //     'Storage-Upgrade',
    //     'Storage-Volume move',
    //     'Storage-Cabling',
    //     'Storage-Hardware replacement',
    //     'Storage-Others',
    //     'On Call-Urgent/Deployment',
    //     'Vault',
    //     'DB Automation',
    //     'SOP document',
    //     'Troubleshooting/Performance Tunning',
    //     'JIRA Related',
    //     'Others-DB Relaetd',
    //     'Others-No DB Related'
    //   ]
    // })
    const defineDbaNextButtonStatus = computed(() => {
      if (step.value === 1) {
        // title & desc
        // || -> title & description have data then return false, else return true
        return (
          ticketCollectSetDba.title === '' ||
          ticketCollectSetDba.description === '' ||
          ticketCollectSetDba.duration === null ||
          ticketCollectSetDba.priority === null ||
          ticketCollectSetDba.bizUnit.length === 0 ||
          ticketCollectSetDba.category.length === 0
        )
      } else if (step.value === 2) {
        return ticketCollectSetDba.handler.length === 0
      } else {
        if (isLockUpdateNewTicketButton.value) {
          return true
        } else {
          return false
        }
      }
    })

    // For NET
    const ticketCollectSetNet = reactive({
      title: '',
      description: '',
      infra: [],
      category: null,
      facilities: [],
      vendorSupport: [],
      handler: [],
      participant: [],
      startTime: date.formatDate(Date.now(), 'YYYY-MM-DD HH:mm'),
      endTime: '',
      duration: computed(() => {
        if (
          date.isValid(ticketCollectSetNet.startTime) &&
          date.isValid(ticketCollectSetNet.endTime)
        ) {
          const startTimeObject = new Date(ticketCollectSetNet.startTime)
          const endTimeObject = new Date(ticketCollectSetNet.endTime)
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
    const netDefaultPersonOptions = ref([
      {
        desc: 'Justin Yeh',
        inactive: false
      },
      {
        desc: 'Josh Liu',
        inactive: false
      },
      {
        desc: 'Ryo Bing',
        inactive: false
      },
      {
        desc: 'Ray Hong',
        inactive: false
      },
      {
        desc: 'Chris Yen',
        inactive: false
      },
      {
        desc: 'Shane Tzou',
        inactive: false
      }
    ])
    const netHandlerOptions = _.cloneDeep(netDefaultPersonOptions)
    const netParticipantOptions = _.cloneDeep(netDefaultPersonOptions)
    const netJSMcustomFields = reactive({})
    // const netJSMcustomFields = reactive({
    //   infraOptions: [
    //     'FRI',
    //     'SUN',
    //     'LBT',
    //     'RTX',
    //     'UAT',
    //     'MPLS',
    //     'Highway',
    //     'DEV/QAT',
    //     'Others'
    //   ],
    //   categoryOptions: [
    //     'Architecture',
    //     'Replacement',
    //     'Upgrade',
    //     'Project',
    //     'Migration',
    //     'Routine',
    //     'Decommission',
    //     'Regular Procurement',
    //     'Troubleshooting',
    //     'Other'
    //   ],
    //   facilitiesOptions: [
    //     'BR',
    //     'FW',
    //     'Switch',
    //     'LTM',
    //     'APS',
    //     'WAF',
    //     'Domain',
    //     'DNS',
    //     'Certificate'
    //   ],
    //   vendorOptions: ['Sanfran', 'Lantro', 'eASPNet']
    // })
    const defineNetNextButtonStatus = computed(() => {
      if (step.value === 1) {
        // title & details
        return (
          ticketCollectSetNet.title === '' ||
          ticketCollectSetNet.description === '' ||
          ticketCollectSetNet.infra.length === 0 ||
          ticketCollectSetNet.category === null ||
          ticketCollectSetNet.facilities.length === 0 ||
          ticketCollectSetNet.startTime.length !== 16 ||
          date.isValid(ticketCollectSetNet.startTime) === false
        )
      } else if (step.value === 2) {
        // handler
        return ticketCollectSetNet.handler.length === 0
      } else {
        if (isLockUpdateNewTicketButton.value) {
          return true
        } else {
          return false
        }
      }
    })

    // For SYS
    const ticketCollectSetSys = reactive({
      title: '',
      description: '',
      bizUnit: [],
      category: [],
      handler: [],
      participant: [],
      priority: '',
      startTime: date.formatDate(Date.now(), 'YYYY-MM-DD HH:mm'),
      endTime: '',
      duration: computed(() => {
        if (
          date.isValid(ticketCollectSetSys.startTime) &&
          date.isValid(ticketCollectSetSys.endTime)
        ) {
          const startTimeObject = new Date(ticketCollectSetSys.startTime)
          const endTimeObject = new Date(ticketCollectSetSys.endTime)
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
    const sysDefaultPersonOptions = ref([
      {
        desc: 'Gary Tseng',
        inactive: false
      },
      {
        desc: 'Sun Sun',
        inactive: false
      },
      {
        desc: 'Paul Chen',
        inactive: false
      },
      {
        desc: 'Ran Shih',
        inactive: false
      },
      {
        desc: 'Ian Hsu',
        inactive: false
      },
      {
        desc: 'Noel Huang',
        inactive: false
      },
      {
        desc: 'Wesley Hung',
        inactive: false
      },
      {
        desc: 'Ralf Wu',
        inactive: false
      }
    ])
    const sysHandlerOptions = _.cloneDeep(sysDefaultPersonOptions)
    const sysParticipantOptions = _.cloneDeep(sysDefaultPersonOptions)
    const sysJSMcustomFields = reactive({})
    // const sysJSMcustomFields = reactive({
    //   categoryOptions: [
    //     'Server-Provision',
    //     'Server-Decommission',
    //     'Server-Specification Adjust',
    //     'Server-Software Installation',
    //     'Hardware-Installation',
    //     'Hardware-Replacment',
    //     'Hardware-Decommission',
    //     'Account-Creation',
    //     'Account-Disable',
    //     'Account-Privilege Modification',
    //     'Platform-Anti-Virus Related',
    //     'Platform-ELK Related',
    //     'Platform-Kubernetes Related',
    //     'Platform-Mail Related',
    //     'Platform-RabbitMQ Related',
    //     'Platform-NAS Related',
    //     'Platform-Nutanix Related',
    //     'Platform-Proxy Related',
    //     'Platform-Redis Related',
    //     'Monitor-HostMonitor Related',
    //     'Monitor-Prometheus/Grafana Related',
    //     'Security Related',
    //     'Trouble Shooting',
    //     'Advanced Trouble Shooting (Generate SOP/KB)',
    //     'Others'
    //   ],
    //   bizUnitOptions: [
    //     'XN-188Asia',
    //     'XN-SBK',
    //     'XN-NBG',
    //     'XN-LDR',
    //     'XN-CAS',
    //     'XN-BI',
    //     'XN-IL',
    //     'XN-RTX',
    //     'XN-EA',
    //     'XN-OFC',
    //     'TRS',
    //     'Infra-APP',
    //     'Infra-CEM',
    //     'Infra-CWD',
    //     'Infra-DBA',
    //     'Infra-NET',
    //     'Infra-OPS',
    //     'Infra-SYS',
    //     'Infra-TS',
    //     'Office',
    //     'Others'
    //   ]
    // })
    const defineSysNextButtonStatus = computed(() => {
      // step1, check if checkbox selected already
      if (step.value === 1) {
        // title & details
        return (
          ticketCollectSetSys.title === '' ||
          ticketCollectSetSys.description === '' ||
          ticketCollectSetSys.bizUnit.length === 0 ||
          ticketCollectSetSys.category.length === 0 ||
          ticketCollectSetSys.startTime.length !== 16 ||
          date.isValid(ticketCollectSetSys.startTime) === false
        )
      } else if (step.value === 2) {
        return (
          ticketCollectSetSys.handler.length === 0 || ticketCollectSetSys.priority === ''
        )
      } else {
        if (isLockUpdateNewTicketButton.value) {
          return true
        } else {
          return false
        }
      }
    })

    onMounted(() => {
      if (props.group === 'OPS') {
        opsParticipantOptions.value.forEach(function (ele) {
          if (ele.desc === ticketCollectSetOps.handler[0]) {
            ele.inactive = true
          }
        })
      }
      axios
        .get(
          `https://${ServiceDomainLocal}:9487/bpCowork/jsm/createTicket/field/${props.group}`
        )
        .then((res) => {
          if (props.group === 'SYS') {
            sysJSMcustomFields.categoryOptions = _.cloneDeep(res.data.categoryOptions)
            sysJSMcustomFields.bizUnitOptions = _.cloneDeep(res.data.bizUnitOptions)
          } else if (props.group === 'NET') {
            netJSMcustomFields.infraOptions = _.cloneDeep(res.data.infraOptions)
            netJSMcustomFields.categoryOptions = _.cloneDeep(res.data.categoryOptions)
            netJSMcustomFields.facilitiesOptions = _.cloneDeep(res.data.facilitiesOptions)
            netJSMcustomFields.vendorOptions = _.cloneDeep(res.data.vendorOptions)
          } else if (props.group === 'DBA') {
            dbaJSMcustomFields.categoryOptions = _.cloneDeep(res.data.categoryOptions)
            dbaJSMcustomFields.bizUnitOptions = _.cloneDeep(res.data.bizUnitOptions)
          } else if (props.group === 'OPS') {
            opsJSMcustomFields.categoryOptions = _.cloneDeep(res.data.categoryOptions)
            opsJSMcustomFields.infraOptions = _.cloneDeep(res.data.infraOptions)
            opsJSMcustomFields.bizUnitOptions = _.cloneDeep(res.data.bizUnitOptions)
          }
        })
        .catch((error) => {
          console.log(error)
        })
    })

    // richEditor function 1
    function adjustFontColor(cmd, name) {
      proxy.kpiEditorBtnDropDownColor.hide()
      proxy.kpiEditorBtnDropDownBGColor.hide()
      proxy.targetRef.runCmd(cmd, name)
      proxy.targetRef.focus()
    }

    // richEditor function 2
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

    function stepperController() {
      switch (props.group) {
        case 'SYS':
          if (step.value > 2) {
            isLockUpdateNewTicketButton.value = true
            updateDb('SYS')
          } else {
            step.value = ++step.value
          }
          break
        case 'NET':
          if (step.value > 2) {
            isLockUpdateNewTicketButton.value = true
            updateDb('NET')
          } else {
            step.value = ++step.value
          }
          break
        case 'DBA':
          if (step.value > 2) {
            isLockUpdateNewTicketButton.value = true
            updateDb('DBA')
          } else {
            step.value = ++step.value
          }
          break
        case 'OPS':
          if (step.value > 2) {
            isLockUpdateNewTicketButton.value = true
            updateDb('OPS')
          } else {
            step.value = ++step.value
          }
          break
      }
    }

    async function updateDb(team) {
      const barRef = axiosExecuteBar.value
      barRef.start()
      const postData = reactive({
        targetTeam: team,
        editor: props.editor
      })
      switch (team) {
        case 'SYS':
          postData.result = ticketCollectSetSys
          break
        case 'DBA':
          postData.result = ticketCollectSetDba
          break
        case 'NET':
          postData.result = ticketCollectSetNet
          break
        case 'OPS':
          postData.result = ticketCollectSetOps
          break
      }
      await axios
        .post(`https://${ServiceDomainLocal}:9487/bpCowork/update/db`, postData)
        .then((res) => {
          console.log(res)
          if (res.status === 200) {
            $q.notify({
              message: 'Create new ticket successful!',
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
            updateThis()
          } else {
            console.log('something wrong, need to check')
            $q.notify({
              message: 'Create new ticket failed!',
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
      barRef.stop()
      isLockUpdateNewTicketButton.value = false
    }

    // OPS template update function
    function updateValueToSummary(target) {
      ticketCollectSetOps.description = target.value
      ticketCollectSetOps.title = `[TYPE] ${ticketCollectSetOps.title}`
    }

    // call parent
    function cancelThis() {
      context.emit('triggerByChildren', { action: 'cancel' })
    }

    function updateThis() {
      context.emit('triggerByChildren', { action: 'added' })
    }

    watch(
      () => ticketCollectSetOps.description,
      (curValue, oldValue) => {
        if (curValue.length > 30000) {
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
        }
      }
    )

    watch(
      () => ticketCollectSetDba.description,
      (curValue, oldValue) => {
        if (curValue.length > 30000) {
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
        }
      }
    )

    watch(
      () => ticketCollectSetSys.description,
      (curValue, oldValue) => {
        if (curValue.length > 30000) {
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
        }
      }
    )

    watch(
      () => ticketCollectSetNet.description,
      (curValue, oldValue) => {
        if (curValue.length > 30000) {
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
        }
      }
    )

    // DBA H
    watch(
      () => ticketCollectSetDba.handler,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one handler, need to adjust participant
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            dbaParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            dbaParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          dbaParticipantOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    // SYS H
    watch(
      () => ticketCollectSetSys.handler,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one handler, need to adjust participant
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            sysParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            sysParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          sysParticipantOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    // OPS H
    watch(
      () => ticketCollectSetOps.handler,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one handler, need to adjust participant
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            opsParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            opsParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          opsParticipantOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    // NET H
    watch(
      () => ticketCollectSetNet.handler,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one handler, need to adjust participant
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            netParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            netParticipantOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          netParticipantOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    // DBA P
    watch(
      () => ticketCollectSetDba.participant,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one participant, need to adjust handler
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            dbaHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            dbaHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          dbaHandlerOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    // SYS P
    watch(
      () => ticketCollectSetSys.participant,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one participant, need to adjust handler
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            sysHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            sysHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          sysHandlerOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    // NET P
    watch(
      () => ticketCollectSetNet.participant,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one participant, need to adjust handler
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            netHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            netHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          netHandlerOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    // OPS P
    watch(
      () => ticketCollectSetOps.participant,
      (curList, oldList) => {
        if (curList.length !== 0) {
          // means user add one participant, need to adjust handler
          if (curList.length > oldList.length) {
            // add ['a', 'b', 'c'] and ['a', 'b'], find the 'c'
            const difference = curList.filter((x) => !oldList.includes(x))
            opsHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = true
              }
            })
          } else {
            // remove
            const difference = oldList.filter((x) => !curList.includes(x))
            opsHandlerOptions.value.forEach((ele, index, object) => {
              if (ele.desc === difference[0]) {
                ele.inactive = false
              }
            })
          }
        } else {
          // curList become 0, remove last one
          opsHandlerOptions.value.forEach((ele, index, object) => {
            if (ele.desc === oldList[0]) {
              ele.inactive = false
            }
          })
        }
      }
    )

    return {
      step,
      cancelThis,
      customEditorToolBar,
      foreColor,
      backColor,
      targetRef,
      kpiEditorBtnDropDownColor,
      kpiEditorBtnDropDownBGColor,
      adjustFontColor,
      ConvertforeColor,
      priorityOptions,
      ticketCollectSetSys,
      sysHandlerOptions,
      sysParticipantOptions,
      sysJSMcustomFields,
      defineSysNextButtonStatus,
      stepperController,
      ticketCollectSetNet,
      netHandlerOptions,
      netParticipantOptions,
      netJSMcustomFields,
      defineNetNextButtonStatus,
      ticketCollectSetDba,
      dbaHandlerOptions,
      dbaParticipantOptions,
      dbaJSMcustomFields,
      defineDbaNextButtonStatus,
      ticketCollectSetOps,
      opsHandlerOptions,
      opsParticipantOptions,
      opsJSMcustomFields,
      opsTemplatesSet,
      defineOpsNextButtonStatus,
      axiosExecuteBar,
      updateValueToSummary
    }
  }
})
</script>
