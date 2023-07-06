<!-- @format -->

<template>
  <q-layout view="lHh Lpr lFf">
    <q-ajax-bar
      ref="closeAllTicketStatusBar"
      position="bottom"
      color="positive"
      size="10px"
      skip-hijack
    />
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>
          <span
            shrink
            class="q-mr-md cursor-pointer"
            id="handoverTitleDhs"
            @click="scrollToTheTitle"
            >NDHS{{ isLogin.group !== 'Null' ? `_${isLogin.group}` : '' }}</span
          >
          <span v-if="isLogin.group !== 'OPS' && isLogin.status">
            <q-btn
              class="q-mx-sm"
              push
              color="primary"
              text-color="white"
              flat
              dense
              no-caps
              label="Create Ticket"
              @click="checkNewTicketStatus"
            >
            </q-btn>
          </span>
          <span v-for="item in controllerSet" :key="item.name">
            <span v-if="item.isExtend && isSearchButtonOn !== true">
              <span v-if="item.name === 'controllerNote'">
                <q-btn
                  class="q-mx-sm"
                  push
                  color="primary"
                  text-color="white"
                  flat
                  dense
                  no-caps
                  :label="'@ ' + item.displayName"
                >
                  <q-menu>
                    <q-list dense style="min-width: 100px">
                      <q-item clickable v-close-popup>
                        <q-item-section @click="createNewNote">
                          <span>
                            <q-icon name="create" class="q-pr-xs" />
                            Create New Note
                          </span>
                        </q-item-section>
                      </q-item>
                      <q-item clickable v-close-popup>
                        <q-item-section
                          @click="isLogin.isExtendedNote = !isLogin.isExtendedNote"
                        >
                          <span v-if="isLogin.isExtendedNote">
                            <q-icon name="keyboard_arrow_up" class="q-pr-xs" /> Shorten
                          </span>
                          <span v-else>
                            <q-icon name="keyboard_arrow_down" class="q-pr-xs" /> Extended
                          </span>
                        </q-item-section>
                      </q-item>
                      <q-item clickable v-close-popup>
                        <q-item-section
                          @click="isLogin.isHiddenDelNote = !isLogin.isHiddenDelNote"
                        >
                          <span v-if="isLogin.isHiddenDelNote">
                            <q-icon name="visibility_off" class="q-pr-xs" /> Hide all
                            deleted notes
                          </span>
                          <span v-else>
                            <q-icon name="visibility" class="q-pr-xs" /> show all deleted
                            notes
                          </span>
                        </q-item-section>
                      </q-item>
                      <q-item clickable v-close-popup>
                        <q-item-section>Quit</q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>
              </span>
              <span v-else-if="item.name === 'controllerTicket'">
                <q-btn
                  class="q-mx-sm"
                  push
                  color="primary"
                  text-color="white"
                  flat
                  dense
                  no-caps
                  :label="'@ ' + item.displayName"
                >
                  <q-menu>
                    <q-list dense style="min-width: 100px">
                      <q-item clickable v-close-popup>
                        <q-item-section @click="checkNewTicketStatus"
                          >Create JSM Ticket</q-item-section
                        >
                      </q-item>
                      <q-item disabled>
                        <q-item-section class="text-italic"
                          >Unlock all tickets</q-item-section
                        >
                      </q-item>
                      <q-item disabled>
                        <q-item-section class="text-italic"
                          >Sort out ticket summary</q-item-section
                        >
                      </q-item>
                      <q-item clickable v-close-popup>
                        <q-item-section>Quit</q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>
              </span>
              <span v-else-if="item.name === 'controllerFavorite'">
                <span v-if="item.value">
                  <q-btn
                    v-for="(item, index) in item.isExtend"
                    class="q-mx-sm"
                    color="amber"
                    text-color="black"
                    flat
                    dense
                    :label="item.title"
                    :key="index"
                    @click="openNewPage(item)"
                    no-caps
                  >
                  </q-btn>
                </span>
              </span>
            </span>
          </span>
        </q-toolbar-title>
        <!-- {{ isLogin }} -->
        <div
          v-if="isLogin.group === 'OPS'"
          @click="dataShift.sortOutType = !dataShift.sortOutType"
          class="q-mx-sm"
          v-html="dataShift.sortOutHtml"
        ></div>
        <div class="q-gutter-xs">
          <q-btn-dropdown
            v-if="isLogin.status && isSearchButtonOn !== true && isLogin.group === 'OPS'"
            @click="createTheList"
            icon="history"
            color="white"
            text-color="black"
            size="sm"
            label=""
            menu-anchor="bottom end"
          >
            <q-list v-for="i in reviewList" :key="i[1]" dense>
              <q-item
                dense
                clickable
                v-close-popup
                :href="`/reviewPage/${i[2]}/${i[3]}`"
                target="_blank"
                :class="{ hidden: i[4] }"
              >
                <!-- <q-item dense clickable v-close-popup @click="clickToWindowOpenReviewPage(i[2], i[3])"> -->
                <q-item-section>
                  <q-item-label>{{ i[0] }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
          <q-btn
            v-if="isLogin.status && isSearchButtonOn !== true && isLogin.group === 'OPS'"
            @click="init('button')"
            color="white"
            text-color="black"
            icon="refresh"
            label=""
            size="sm"
          >
            <q-tooltip class="bg-amber text-black shadow-4" :offset="[10, 10]">
              Refresh
            </q-tooltip>
          </q-btn>
          <q-btn
            v-if="isLogin.group !== 'OPS' && isLogin.status"
            color="white"
            text-color="black"
            :icon="isHistoryButtonOn ? 'undo' : 'history'"
            :label="isHistoryButtonOn ? 'Back' : ''"
            size="sm"
            @click="historyButtonEvent"
          >
            <q-tooltip
              v-if="isHistoryButtonOn === false"
              class="bg-amber text-black shadow-4"
              :offset="[10, 10]"
            >
              View all closed ticket
            </q-tooltip>
          </q-btn>
          <q-btn
            v-if="isLogin.status"
            @click="searchButtonEvent"
            color="white"
            text-color="black"
            :icon="isSearchButtonOn ? 'undo' : 'search'"
            :label="isSearchButtonOn ? 'Back' : ''"
            size="sm"
          >
            <q-tooltip
              v-if="isSearchButtonOn === false"
              class="bg-amber text-black shadow-4"
              :offset="[10, 10]"
            >
              Search
            </q-tooltip>
          </q-btn>
          <q-btn
            v-if="isLogin.status && isSearchButtonOn !== true && isLogin.group === 'OPS'"
            color="green-2"
            text-color="black"
            to="/confirmPage"
            icon="email"
            size="sm"
            :disable="onShiftResult.length === 0"
          >
            <q-tooltip
              v-if="isSearchButtonOn === false"
              class="bg-amber text-black shadow-4"
              :offset="[10, 10]"
            >
              ConfirmPage
            </q-tooltip>
          </q-btn>
          <q-btn
            v-if="isLogin.status && isSearchButtonOn !== true"
            color="blue-grey-10"
            text-color="blue-grey-1"
            label=""
            size="sm"
            icon="tune"
          >
            <q-tooltip class="bg-amber text-black shadow-4" :offset="[10, 10]">
              Controller
            </q-tooltip>
            <q-menu :offset="[0, 10]">
              <div class="row no-wrap q-pa-md">
                <div v-if="isLogin.group === 'OPS'" class="column">
                  <div class="text-subtitle1 text-bold q-mb-md">Dashboard settings</div>
                  <span>
                    <div class="row justify-between text-caption">
                      <div>ZONE</div>
                      <div>Extensions</div>
                    </div>
                  </span>
                  <span v-for="item in controllerSet" :key="item.name">
                    <div class="row justify-between">
                      <q-toggle
                        class="col-11"
                        v-model="item.value"
                        :label="item.displayName"
                        :class="[
                          item.value ? 'text-caption' : 'text-caption text-italic'
                        ]"
                      />
                      <q-checkbox
                        v-if="item.name !== 'controllerFavorite'"
                        class="col"
                        v-model="item.isExtend"
                        :disable="item.value === false"
                      />
                      <div v-else class="col q-pt-sm q-pl-xs" clickable v-close-popup>
                        <q-icon
                          @click="adjustFavorite"
                          name="settings"
                          size="sm"
                          class="q-pl-xs cursor-pointer"
                        />
                      </div>
                    </div>
                  </span>
                </div>

                <q-separator
                  v-if="isLogin.group === 'OPS'"
                  vertical
                  inset
                  class="q-mx-lg"
                />

                <div
                  class="column flex-center items-center justify-center content-center self-center"
                >
                  <q-avatar size="72px">
                    <img
                      :src="
                        'https://' +
                        ServiceDomainLocal +
                        ':9487/review/avatar/' +
                        isLogin.value
                      "
                    />
                  </q-avatar>

                  <div class="text-subtitle1 text-bold q-my-xs">{{ isLogin.value }}</div>

                  <q-btn
                    color="primary"
                    label="Logout"
                    @click="buttonLogout"
                    push
                    size="sm"
                    v-close-popup
                  />

                  <div
                    v-if="isLogin.group === 'OPS'"
                    class="col q-pa-sm text-caption text-no-wrap"
                  >
                    <div class="text-bold">Current Shift:</div>
                    <div class="text-center">{{ CurData }}-{{ CurShift }}</div>
                    <!-- <span class="text-bold">DB TimeStamp:</span><br />
                    {{ sysInfo.curValue.timeStamp }}+8<br /> -->
                    <div class="text-bold">On the Shift:</div>
                    <div v-if="onShiftResult.length == 0" class="text-center">
                      <q-icon
                        class="cursor-pointer"
                        name="person_add"
                        size="md"
                        @click="updateTheOnShiftList"
                      />
                    </div>
                    <div
                      class="cursor-pointer text-center items-end"
                      @click="updateTheOnShiftList"
                    >
                      <q-icon size="sm" name="manage_accounts"></q-icon>
                      {{ onShiftResult.join(' | ') }}
                    </div>
                    <q-separator color="orange-8" spaced inset />
                    <div class="text-bold row"><span class="col">handover_handler:</span><span class="text-caption col text-right">{{ shiftDict.title_handover.join(', ') }}</span></div>
                    <div class="text-bold row"><span class="col">alert_handler:</span><span class="text-caption col text-right">{{ shiftDict.title_alert_handler.join(', ') }}</span></div>
                    <div class="text-bold row"><span class="col">message_handler:</span><span class="text-caption col text-right">{{ shiftDict.title_message_handler.join(', ') }}</span></div>
                    <div class="text-bold row"><span class="col">request_handler:</span><span class="text-caption col text-right">{{ shiftDict.title_request_handler.join(', ') }}</span></div>
                  </div>
                  <div v-if="isLogin.group === 'OPS'" class="col">
                    <div class="row q-gutter-xs">
                      <q-btn
                        class="col"
                        color="primary"
                        label="Save"
                        push
                        size="sm"
                        @click="saveControllerSetting"
                      />
                      <q-btn
                        class="col"
                        color="primary"
                        label="Load"
                        push
                        size="sm"
                        @click="loadControllerSetting"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
        <!-- <div>Quasar v{{ $q.version }}</div> -->
      </q-toolbar>
    </q-header>

    <q-drawer v-if="isLogin.status" v-model="leftDrawerOpen" bordered>
      <!-- <q-drawer v-model="leftDrawerOpen" show-if-above bordered> -->
      <q-list>
        <q-item-label header> hyperlink of SRE page </q-item-label>
        <EssentialLink v-for="link in essentialLinks" :key="link.title" v-bind="link" />
        <q-item-label class="absolute-top row justify-end">
          <q-btn
            class="q-mt-sm q-mr-xs"
            size="sm"
            push
            color="white"
            text-color="primary"
            round
            icon="settings"
            @click="callHyperlink"
            :disable="isLogin.group !== 'OPS'"
          />
          <q-btn
            class="q-mt-sm q-mr-xs"
            size="sm"
            push
            color="white"
            text-color="primary"
            round
            icon="add_circle"
            @click="isShowAddHyperLink = true"
            :disable="isLogin.group !== 'OPS'"
          />
        </q-item-label>
      </q-list>
    </q-drawer>

    <q-page-container>
      <!-- persistent -->
      <!-- :class="{ hidden: createTicketSet.isDialogShow }" -->
      <q-dialog persistent full-width v-model="createTicketSet.isShow">
        <DHSCreateNewTicketPage
          :group="isLogin.group"
          :editor="isLogin.value"
          :key="createTicketSet.refreshKey"
          @triggerByChildren="adjustCreateTicketSet"
        ></DHSCreateNewTicketPage>
      </q-dialog>
      <q-dialog persistent v-model="isShowOnShiftList">
        <q-card style="width: 700px; max-width: 80vw">
          <q-card-section>
            <div class="text-h6">{{ CurData }}-{{ CurShift }} Teammates</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            <q-select
              filled
              use-chips
              stack-label
              v-model="onShiftResult"
              multiple
              virtual-scroll-horizontal
              :options="shiftList"
              label="On the shift"
            />
          </q-card-section>

          <q-card-section
            v-if="
              PullApiDict.curShift &&
              PullApiDict.curShiftMember.length &&
              PullApiDict.nextShiftMember.length
            "
          >
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label>Current Shift</q-item-label>
                  <q-item-label caption>{{
                    PullApiDict.curShiftMember.join(' | ')
                  }}</q-item-label>
                </q-item-section>

                <q-item-section side top>
                  <q-item-label caption>{{ PullApiDict.curShift }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-separator spaced inset />
              <q-item>
                <q-item-section>
                  <q-item-label>Next Shift</q-item-label>
                  <q-item-label side caption>{{
                    PullApiDict.nextShiftMember.join(' | ')
                  }}</q-item-label>
                </q-item-section>
                <q-item-section side top>
                  <q-item-label caption>{{ PullApiDict.nextShift }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-separator color="orange-8" spaced inset />
            </q-list>
          </q-card-section>
          <q-card-section v-if="PullApiDict.curShift !== 'N'">
            <q-list>
              <q-item>
                <q-item-section>
                  <q-item-label>Shift Leader</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label caption>
                    <span
                      @click="changeShiftLeader(name)"
                      class="q-pr-xs cursor-pointer"
                      v-for="name in onShiftResult"
                      :key="name"
                    >
                      <span
                        v-if="name === shiftDict.shift_leader"
                        class="text-red-8 text-bold"
                        >{{ name }}</span
                      >
                      <span v-else>{{ name }}</span>
                    </span>
                  </q-item-label>
                </q-item-section>
                <q-separator spaced inset />
              </q-item>
              <q-separator color="orange-8" spaced inset />
              <q-item class="row justify-center items-center">Handler</q-item>
              <q-item class="row">
                <q-item-section class="col">
                  <q-item-label>Handover</q-item-label>
                </q-item-section>
                <q-item-section class="col">
                  <q-item-label
                    @click="changeTitle('handover', name)"
                    v-for="name in onShiftResult"
                    :key="name"
                    caption
                  >
                    <span
                      v-if="shiftDict.title_handover.includes(name)"
                      class="text-red-8 text-bold cursor-pointer"
                      >{{ name }}</span
                    >
                    <span v-else class="cursor-pointer">{{ name }}</span>
                  </q-item-label>
                </q-item-section>
                <q-item-section class="col">
                  <q-item-label>Alert</q-item-label>
                </q-item-section>
                <q-item-section class="col">
                  <q-item-label
                    @click="changeTitle('alert', name)"
                    v-for="name in onShiftResult"
                    :key="name"
                    caption
                  >
                    <span
                      v-if="shiftDict.title_alert_handler.includes(name)"
                      class="text-red-8 text-bold cursor-pointer"
                      >{{ name }}</span
                    >
                    <span v-else class="cursor-pointer">{{ name }}</span>
                  </q-item-label>
                </q-item-section>
                <q-item-section class="col">
                  <q-item-label>Message</q-item-label>
                </q-item-section>
                <q-item-section class="col">
                  <q-item-label
                    @click="changeTitle('message', name)"
                    v-for="name in onShiftResult"
                    :key="name"
                    caption
                  >
                    <span
                      v-if="shiftDict.title_message_handler.includes(name)"
                      class="text-red-8 text-bold cursor-pointer"
                      >{{ name }}</span
                    >
                    <span v-else class="cursor-pointer">{{ name }}</span>
                  </q-item-label>
                </q-item-section>
                <q-item-section class="col">
                  <q-item-label>Request</q-item-label>
                </q-item-section>
                <q-item-section class="col">
                  <q-item-label
                    @click="changeTitle('request', name)"
                    v-for="name in onShiftResult"
                    :key="name"
                    caption
                  >
                    <span
                      v-if="shiftDict.title_request_handler.includes(name)"
                      class="text-red-8 text-bold cursor-pointer"
                      >{{ name }}</span
                    >
                    <span v-else class="cursor-pointer">{{ name }}</span>
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>

          <q-linear-progress
            v-if="isShiftInfoUpdating"
            indeterminate
            color="warning"
            class="q-mt-sm"
          />

          <q-card-actions align="right" class="bg-white text-teal">
            <q-btn
              no-caps
              flat
              size="md"
              label="Cancel"
              @click="reloadShiftInfo"
              v-close-popup
            />
            <q-btn
              no-caps
              flat
              size="md"
              label="Pull data"
              @click="pullApiFunction"
              :loading="PullApiDict.isLoading"
            />
            <q-btn
              no-caps
              flat
              size="md"
              label="Update"
              @click="updateShiftInfo"
              :disable="isShiftInfoUpdating"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-dialog persistent v-model="isShowAddHyperLink">
        <q-card style="width: 700px; max-width: 80vw" class="my-card">
          <q-card-section>
            <div class="text-h6">Add new hyperlink to DHS</div>
          </q-card-section>
          <q-card-section class="q-py-none q-pb-sm">
            <q-input
              filled
              v-model="hyperlinkSet.title"
              input-class="text-right"
              label-slot
              clearable
            >
              <template v-slot:label>
                <div class="row items-center all-pointer-events">
                  <q-icon
                    class="q-mr-xs"
                    color="deep-orange"
                    size="24px"
                    name="description"
                  />
                  name
                </div>
              </template>
            </q-input>
          </q-card-section>
          <q-card-section class="q-py-none q-pb-sm">
            <q-input
              filled
              v-model="hyperlinkSet.caption"
              input-class="text-right"
              label-slot
              clearable
            >
              <template v-slot:label>
                <div class="row items-center all-pointer-events">
                  <q-icon
                    class="q-mr-xs"
                    color="deep-orange"
                    size="24px"
                    name="fas fa-lightbulb"
                  />
                  description
                </div>
              </template>
            </q-input>
          </q-card-section>
          <q-card-section class="q-py-none q-pb-sm">
            <q-input
              filled
              v-model="hyperlinkSet.link"
              input-class="text-right"
              label-slot
              clearable
            >
              <template v-slot:label>
                <div class="row items-center all-pointer-events">
                  <q-icon class="q-mr-xs" color="deep-orange" size="24px" name="link" />
                  hyperlink
                </div>
              </template>
            </q-input>
          </q-card-section>
          <q-card-actions align="right" class="bg-white text-teal">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn
              flat
              label="OK"
              @click="addHyperLink"
              :disabled="hyperlinkSet.allowToSubmit"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-dialog full-width v-model="isShowHpyerLinkSetting" persistent>
        <q-table
          class="my-sticky-header-table ellipsis"
          style="width: 700px; max-width: 80vw"
          title="HYPERLINK OF SRE PAGE"
          :rows="rows"
          :columns="columns"
          row-key="name"
          :rows-per-page-options="['0']"
          separator="cell"
          dense
        >
          <template v-slot:header="props">
            <q-tr :props="props">
              <q-th auto-width />
              <q-th v-for="col in props.cols" :key="col.name" :props="props">
                {{ col.label }}
              </q-th>
            </q-tr>
          </template>
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td class="text-center customPaddingQTbx" auto-width>
                <q-btn
                  size="sm"
                  class="text-center"
                  push
                  color="white"
                  text-color="primary"
                  round
                  dense
                  icon="delete"
                  @click="deleteHyperLink(props.row.sn, props.row.title)"
                />
              </q-td>
              <q-td key="title" :props="props">
                {{ props.row.title }}
                <q-popup-edit v-model="props.row.title">
                  <section class="text-caption text-bold row">
                    <span class="col-12 text-center">* Update Name *</span>
                  </section>
                  <q-input v-model="props.row.title" dense autofocus counter />
                  <section class="text-caption text-italic row justity-center">
                    <span class="col-12 text-center"
                      >{{ props.row.caption }} | {{ props.row.link }}</span
                    >
                  </section>
                </q-popup-edit>
              </q-td>
              <q-td key="caption" :props="props">
                {{ props.row.caption }}
                <q-popup-edit v-model="props.row.caption">
                  <section class="text-caption text-bold row">
                    <span class="col-12 text-center">* Update Description *</span>
                  </section>
                  <q-input v-model="props.row.caption" dense autofocus counter />
                  <section class="text-caption text-italic row justity-center">
                    <span class="col-12 text-center"
                      >{{ props.row.title }} | {{ props.row.link }}</span
                    >
                  </section>
                </q-popup-edit>
              </q-td>
              <q-td key="link" :props="props">
                <div class="row justify-center">
                  <div style="width: 200px" class="customEllipsis">
                    {{ props.row.link }}
                  </div>
                </div>
                <q-popup-edit v-model="props.row.link">
                  <section class="text-caption text-bold row">
                    <span class="col-12 text-center">* Update hyperlink *</span>
                  </section>
                  <q-input v-model="props.row.link" dense autofocus counter />
                  <section class="text-caption text-italic row justity-center">
                    <span class="col-12 text-center"
                      >{{ props.row.title }} | {{ props.row.caption }}</span
                    >
                  </section>
                </q-popup-edit>
              </q-td>
              <q-td key="icon" :props="props">
                <q-icon size="md" :name="props.row.icon"></q-icon>
                <q-popup-edit anchor="bottom right" v-model="props.row.icon">
                  <q-select
                    transition-show="scale"
                    transition-hide="scale"
                    standout
                    v-model="props.row.icon"
                    :options="options"
                    dense
                    options-dense
                  >
                    <template v-slot:prepend>
                      <q-avatar :icon="props.row.icon" />
                    </template>
                    <template v-slot:option="scope">
                      <q-item v-bind="scope.itemProps">
                        <q-item-section avatar>
                          <q-icon :name="scope.opt" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ scope.opt }}</q-item-label>
                        </q-item-section>
                      </q-item>
                    </template>
                  </q-select>
                  <!-- <q-input v-model="props.row.icon"  /> -->
                </q-popup-edit>
              </q-td>
              <!-- <q-td key="caption" :props="props">
                {{ props.row.caption }}
                <q-popup-edit v-model="props.row.caption" title="Update caption" buttons>
                  <q-input type="number" v-model="props.row.caption" dense autofocus />
                </q-popup-edit>
              </q-td>
              <q-td key="link" :props="props">
                <div class="text-pre-wrap">{{ props.row.link }}</div>
                <q-popup-edit v-model="props.row.link">
                  <q-input type="textarea" v-model="props.row.link" dense autofocus />
                </q-popup-edit>
              </q-td> -->
            </q-tr>
          </template>
          <template v-slot:bottom>
            <section class="col-12 text-right">
              <q-btn flat label="Cancel" v-close-popup />
              <q-btn flat label="Update" @click="updateHyperByTable" />
            </section>
          </template>
        </q-table>
      </q-dialog>
      <div v-if="isLogin.status">
        <div v-if="isHistoryButtonOn">
          <q-page class="bg-grey-3">
            <div class="row q-pa-sm bg-teal-1 text-italic">History</div>
            <HistoryPage
              :username="isLogin.value"
              :whichTeam="isLogin.group"
              :startQuery="isHistoryButtonOn"
            >
            </HistoryPage>
          </q-page>
        </div>
        <div v-show="isSearchButtonOn">
          <q-page class="bg-grey-3">
            <div class="row q-pa-sm bg-teal-1 text-italic">
              Search Page, For JSM -
              <a
                class="q-px-xs"
                href="https://okta.opsware.xyz:9488/search"
                target="_blank"
              >
                New version</a
              >
            </div>
            <SearchPage></SearchPage>
          </q-page>
        </div>
        <div v-show="!isSearchButtonOn">
          <section v-if="isLogin.group === 'OPS'">
            <div class="row q-pa-md q-col-gutter-md">
              <div
                :class="controllerSet[0].isExtend ? 'col-12' : 'col-6'"
                v-show="controllerSet[0].value"
              >
                <DHSCustomerStatusPage
                  :key="isLogin.refreshCustomerStatusKey"
                ></DHSCustomerStatusPage>
              </div>
              <div
                :class="controllerSet[1].isExtend ? 'col-12' : 'col-6'"
                v-show="controllerSet[1].value"
              >
                <DHSCalendarPage
                  class="customChildMinHeight"
                  :key="isLogin.refreshCalendarKey"
                ></DHSCalendarPage>
              </div>
              <div
                :class="controllerSet[2].isExtend ? 'col-12' : 'col-6'"
                v-show="controllerSet[2].value"
              >
                <DHSMonitoringSystemPage
                  :key="isLogin.refreshMonitoringSystemKey"
                ></DHSMonitoringSystemPage>
              </div>
              <div
                :class="controllerSet[3].isExtend ? 'col-12' : 'col-6'"
                v-show="controllerSet[3].value"
              >
                <DHSICPPage :key="isLogin.refreshICPKey"></DHSICPPage>
              </div>
            </div>
            <div class="col-12 bg-brown-1" v-show="controllerSet[4].value">
              <!-- <div class="text-h4 bg-green-3 q-ma-md text-center">DISPLAY NOTE ZONE</div> -->
              <DHSNotePage :key="isLogin.refreshNoteKey"></DHSNotePage>
            </div>
            <div class="col-12 q-pb-md bg-brown-1" v-show="controllerSet[5].value">
              <DHSOPSJSMPage :key="createTicketSet.refreshKey"></DHSOPSJSMPage>
            </div>
          </section>
          <section
            class="bg-brown-1 q-pb-md"
            v-else-if="(isLogin.group === 'NET') & !isHistoryButtonOn"
          >
            <DHSNETJSMPage :key="createTicketSet.refreshKey"></DHSNETJSMPage>
          </section>
          <section
            class="bg-brown-1 q-pb-md"
            v-else-if="(isLogin.group === 'SYS') & !isHistoryButtonOn"
          >
            <DHSSYSJSMPage :key="createTicketSet.refreshKey"></DHSSYSJSMPage>
          </section>
          <section
            class="bg-brown-1 q-pb-md"
            v-else-if="(isLogin.group === 'DBA') & !isHistoryButtonOn"
          >
            <DHSDBAJSMPage :key="createTicketSet.refreshKey"></DHSDBAJSMPage>
            <!-- <DHSDBAOTRSPage :key="isLogin.refreshDBAOTRSPageKey"></DHSDBAOTRSPage> -->
          </section>
        </div>
      </div>
      <div v-else>
        <q-page class="bg-grey-3">
          <div class="row q-pa-sm bg-teal-1 text-italic">
            Please login AD account first.
          </div>
          <LoginPage></LoginPage>
        </q-page>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script>
import EssentialLink from 'components/EssentialLink.vue'
import DHSOPSJSMPage from 'pages/DHSOpsJSMPage.vue'
import DHSNETJSMPage from 'pages/DHSNetJSMPage.vue'
import DHSSYSJSMPage from 'pages/DHSSysJSMPage.vue'
import DHSDBAJSMPage from 'pages/DHSDbaJSMPage.vue'
// import DHSDBAOTRSPage from 'pages/DHSDbaOTRSPage.vue'
import DHSNotePage from 'pages/DHSNotePage.vue'
// import DHSOTRSPage from 'pages/DHSOTRSPage.vue'
import DHSICPPage from 'pages/DHSICPPage.vue'
import DHSMonitoringSystemPage from 'pages/DHSMonitoringSystemPage.vue'
import DHSCustomerStatusPage from 'pages/DHSCustomerStatusPage.vue'
import DHSCalendarPage from 'pages/DHSCalendarPage.vue'
import LoginPage from 'components/LoginPage.vue'
import SearchPage from 'components/SearchPage.vue'
import HistoryPage from 'components/HistoryPage.vue'
import DHSCreateNewTicketPage from 'components/DHSCreateNewTicketPage.vue'
import {
  defineComponent,
  ref,
  provide,
  reactive,
  watch,
  computed,
  onMounted,
  onBeforeUnmount
} from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useQuasar, Cookies, date, scroll, useMeta } from 'quasar'
import axios from 'axios'
import _ from 'lodash'

const metaData = {
  // sets document title
  title: 'NDHS',
  titleTemplate: (title) => `${title}`
}

export default defineComponent({
  name: 'MainLayout',
  components: {
    EssentialLink,
    DHSNETJSMPage,
    DHSOPSJSMPage,
    DHSSYSJSMPage,
    DHSDBAJSMPage,
    // DHSDBAOTRSPage,
    LoginPage,
    SearchPage,
    HistoryPage,
    DHSNotePage,
    // DHSOTRSPage,
    DHSICPPage,
    DHSMonitoringSystemPage,
    DHSCustomerStatusPage,
    DHSCalendarPage,
    DHSCreateNewTicketPage
  },
  setup(root) {
    useMeta(metaData)
    const $q = useQuasar()
    const $store = useStore()
    const scriptContainer = ref()
    const closeAllTicketStatusBar = ref(null)
    const selfTime = ref(null)
    const selfinitTime = ref(null)
    const { getScrollTarget, setVerticalScrollPosition } = scroll
    const leftDrawerOpen = ref(false)
    const CurData = ref('')
    const CurShift = ref('')
    const nextShiftDefine = ref(false)
    // const JiraList = ref([])
    const isSearchButtonOn = ref(false)
    const isHistoryButtonOn = ref(false)
    const isSync = ref(true) // true = no need to sync, false = need to sync, will change the button status
    const PullApiDict = reactive({
      isLoading: false,
      curShiftMember: [],
      nextShiftMember: [],
      curShift: '',
      nextShift: ''
    })
    const reviewList = ref([])
    const isLogin = reactive({
      value: $q.cookies.get('handoverEditor') ? $q.cookies.get('handoverEditor') : 'Null',
      group: $q.cookies.get('handoverGroup') ? $q.cookies.get('handoverGroup') : 'Null',
      status: $q.cookies.has('handoverEditor'),
      refreshNoteKey: 0, // reload DHSNotePage key
      refreshCreateNewTicketKey: 0, // reload DHSJIRAPage key
      refreshNoteStep: 0, // watch on DHSNotePage let child component ( DHSNoteList ) reload, but user will not feel it
      refreshJIRAStep: 0, // watch on DHSNotePage let child component ( DHSNoteList ) reload, but user will not feel it
      refreshNoteUnderEditingList: [],
      refreshJIRAUnderEditingList: [],
      keepNoteSn: 0,
      isHiddenDelNote: true,
      isExtendedNote: false,
      refreshICPKey: 0,
      refreshMonitoringSystemKey: 0,
      refreshCustomerStatusKey: 0,
      refreshDBAOTRSPageKey: 0,
      filterJiraTicket: 'All'
    })
    const createTicketSet = reactive({
      refreshKey: 0,
      isShow: false,
      isDialogShow: false
    })

    const controllerSet = reactive([
      {
        name: 'controllerCustomerStatus',
        value: ref(true),
        displayName: 'Service Status',
        isExtend: ref(false)
      },
      {
        name: 'controllerCalendar',
        value: ref(true),
        displayName: 'Calendar',
        isExtend: ref(false)
      },
      {
        name: 'controllerMontoringService',
        value: ref(true),
        displayName: 'Health Map',
        isExtend: ref(false)
      },
      {
        name: 'controllerICPStatus',
        value: ref(true),
        displayName: 'ICP Status',
        isExtend: ref(false)
      },
      {
        name: 'controllerNote',
        value: ref(true),
        displayName: 'Notes',
        isExtend: ref(false)
      },
      {
        name: 'controllerTicket',
        value: ref(true),
        displayName: 'Tickets',
        isExtend: ref(false)
      },
      {
        name: 'controllerFavorite',
        value: ref(true),
        displayName: 'Favorite',
        isExtend: ref([])
      }
    ])

    const router = useRouter()

    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain

    // duty & shift -
    const dataShift = reactive({
      duty: 'null',
      standby: 'null',
      sortOutType: true,
      sortOutHtml: computed(() => {
        if (dataShift.sortOutType) {
          if (dataShift.duty.includes('Shift_Leader - Cadalora')) {
            return `<span>&#128520;&nbsp&nbsp</span>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Cyril Rejas')) {
            return `<i class="fas fa-futbol">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Bob Lin')) {
            return `<i class="fas fa-gamepad">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Shift_Leader - Asky Huang')) {
            return `<i class="fas fa-child">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Daniel Liu')) {
            return `<i class="fas fa-wine-glass-alt">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Shift_Leader - Danny Wu')) {
            return `<i class="fas fa-drumstick-bite">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Ivan Chu')) {
            return `<i class="fas fa-search">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Gary Wu')) {
            return `<i class="fas fa-dumbbell">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Shift_Leader - Aiden Tan')) {
            return `<i class="fas fa-dog">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Shift_Leader - Keven Chang')) {
            return `<i class="fas fa-walking">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Albert Liu')) {
            return `<i class="fas fa-table-tennis">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Thurston Chao')) {
            return `<i class="fas fa-fire">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Duty - Eric Kao')) {
            return `<i class="fas fa-chart-line">&nbsp&nbsp</i>${dataShift.duty}`
          } else if (dataShift.duty.includes('Shift_Leader - Larry Tsou')) {
            return `<i class="fas fa-skiing-nordic">&nbsp&nbsp</i>${dataShift.duty}`
          } else {
            return `<i class="fas fa-crown">&nbsp&nbsp</i>${dataShift.duty}`
          }
        } else {
          return `<i class="fas fa-crown">&nbsp&nbsp</i>${dataShift.standby}`
        }
      })
    })

    const essentialLinks = ref()

    const isShowAddHyperLink = ref(false)
    const isShowHpyerLinkSetting = ref(false)

    const hyperlinkSet = reactive({
      title: '',
      caption: '',
      icon: '',
      link: '',
      allowToSubmit: computed(() => {
        if (hyperlinkSet.title !== '') {
          if (hyperlinkSet.caption !== '') {
            if (hyperlinkSet.link !== '') {
              return false
            } else {
              return true
            }
          } else {
            return false
          }
        } else {
          return true
        }
      })
    })

    // hyperlink setting columns
    const columns = [
      {
        name: 'title',
        align: 'center',
        label: 'Name',
        field: 'title'
      },
      {
        name: 'caption',
        align: 'center',
        label: 'Description',
        field: 'caption'
      },
      {
        name: 'link',
        align: 'center',
        label: 'hyperlink',
        field: 'link'
      },
      {
        name: 'icon',
        align: 'center',
        label: 'icon',
        field: 'icon'
      }
    ]

    // hyperlink setting data rows
    const rows = ref()

    // hyperlink setting icon options
    const options = [
      'search',
      'home',
      'settings',
      'info',
      'web',
      'dns',
      'link',
      'new_releases',
      'event',
      'cloud',
      'auto_awesome',
      'fas fa-chart-line',
      'fas fa-network-wired'
    ]

    // display the dialog for on shift table or not
    const isShowOnShiftList = ref(false)

    // teammate options
    const shiftList = ref([
      'Aiden',
      'Albert',
      'Alex',
      'Asky',
      'Bob',
      'Cadalora',
      'Cyril',
      'Daniel',
      'Eric',
      'Gary',
      'Thurston',
      'Rorschach',
      'Bayu',
      'Danny',
      'Huck',
      'Ivan',
      'Keven',
      'Larry'
    ])
    const onShiftResult = ref([])
    const isShiftInfoUpdating = ref(false)
    const shiftDict = reactive({
      shift_leader: '',
      title_handover: [],
      title_alert_handler: [],
      title_message_handler: [],
      title_request_handler: []
    })

    provide('isLogin', isLogin)
    provide('CurData', CurData)
    provide('CurShift', CurShift)

    function localDataSync(_type) {
      if (_type === 'update') {
        alert('Update success, but local data is not match with server, reload page now')
      } else if (_type === 'edit') {
        alert(
          'Unable to EDIT ticket due to Local data is not match with server, reload the page now'
        )
      }
      router.go('/handover')
    }

    function initIntervalQuery() {
      if ($q.cookies.has('handoverEditor')) {
        if (isLogin.group === 'OPS') {
          init('firstTime')
          // $q.notify({
          //   message: 'KPI review released',
          //   color: 'yellow-3',
          //   textColor: 'red-8',
          //   progress: true,
          //   actions: [
          //     {
          //       icon: 'open_in_browser',
          //       color: 'positive',
          //       handler: () => {
          //         openNewPage('kpi')
          //       }
          //     }
          //   ]
          // })
          if (selfinitTime.value !== null) {
            selfinitTime.value = setInterval(() => {
              init('auto')
              // }, 2000)
            }, 180000)
          }
        } else if (isLogin.group === 'NET') {
          loadHyperLink()
        } else if (isLogin.group === 'SYS') {
          loadHyperLink()
        } else if (isLogin.group === 'DBA') {
          loadHyperLink()
        }
      } else {
        console.log('user need to login')
      }
    }

    async function init(from) {
      // Check editor cookie
      // const hasCookie = $q.cookies.has('handoverEditor')
      // Get current date and shift
      await axios
        .get(`https://${ServiceDomainLocal}:9487/handover/main/init`)
        .then((response) => {
          if (from === 'firstTime') {
            CurData.value = response.data.date
            CurShift.value = response.data.shift
            loadControllerSetting()
            loadHyperLink()
            reloadShiftInfo()
            loadDateShift() // check the duty and standby
          } else {
            if (
              CurData.value !== response.data.date ||
              CurShift.value !== response.data.shift
            ) {
              nextShiftDefine.value = true
              CurData.value = response.data.date
              CurShift.value = response.data.shift
              loadDateShift()
            }
          }
        })
        .catch((error) => {
          console.log(error)
        })

      const timeStamp = Date.now()
      const formattedString = date.formatDate(timeStamp, 'HH:mm:ss')
      if (nextShiftDefine.value === true) {
        isLogin.refreshNoteKey += 1
        createTicketSet.refreshKey += 1
        $q.notify({
          message: `Data & Shift has change, all tickets & notes are sync at ${formattedString}`,
          color: 'purple-12',
          progress: true,
          actions: [
            {
              icon: 'cancel',
              color: 'white',
              handler: () => {}
            }
          ]
        })
      } else {
        if (from === 'firstTime') {
          $q.notify({
            message: `<b>Tickets</b> & <b>Notes</b> are sync at ${formattedString}`,
            color: 'brown-6',
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
        } else if (from === 'auto') {
          console.log('hit auto')
          isLogin.refreshNoteStep += 1
          isLogin.refreshJIRAStep += 1
        } else if (from === 'button') {
          isLogin.refreshNoteStep += 1
          isLogin.refreshJIRAStep += 1
          $q.notify({
            message: `<b>Tickets</b> & <b>Notes</b> are sync at ${formattedString}`,
            color: 'brown-6',
            html: true,
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
    }

    // logout function, change the isLogin and JiraList value
    function buttonLogout() {
      Cookies.remove('handoverEditor')
      Cookies.remove('handoverGroup')
      isLogin.status = false
      isLogin.value = 'Null'
      isLogin.group = 'Null'
      clearInterval(selfinitTime.value)
      controllerSet.forEach((item, index, object) => {
        object[index].isExtend = false
      })
    }

    function scrollToTheTitle() {
      const ele = document.getElementById('handoverTitleDhs')
      const target = getScrollTarget(ele)
      const offset = ele.offsetTop - ele.scrollHeight
      const duration = 100
      setVerticalScrollPosition(target, offset, duration)
    }

    function createNewNote() {
      $q.dialog({
        title: 'Create New Note',
        message: 'What is the subject?',
        prompt: {
          model: '',
          isValid: (val) => val.length > 2, // << here is the magic
          type: 'text' // optional
        },
        cancel: true,
        persistent: true
      }).onOk(async (data) => {
        console.log('>>>> OK, received', data)
        const postData = reactive({
          newTitle: data,
          newEditor: isLogin.value
        })
        await axios
          .post(`https://${ServiceDomainLocal}:9487/note/create`, postData)
          .then((res) => {
            isLogin.keepNoteSn = res.data
            isLogin.refreshNoteKey += 1 // becoz need reload whole DHSNotePage component let new child component show up, that is why need + 1
          })
          .catch((error) => {
            console.log(error)
          })
      })
    }

    function saveControllerSetting() {
      const postData = reactive({
        currentUser: isLogin.value,
        currentControllerSetting: controllerSet
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/controller/update`, postData)
        .then((res) => {
          console.log(res)
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function loadControllerSetting() {
      axios
        .get(`https://${ServiceDomainLocal}:9487/controller/query/${isLogin.value}`)
        .then((res) => {
          if (res.data !== 'new') {
            controllerSet[0].value = res.data.controllerCustomerStatus[0]
            controllerSet[0].isExtend = res.data.controllerCustomerStatus[1]
            controllerSet[1].value = res.data.controllerCalendar[0]
            controllerSet[1].isExtend = res.data.controllerCalendar[1]
            controllerSet[2].value = res.data.controllerMontoringService[0]
            controllerSet[2].isExtend = res.data.controllerMontoringService[1]
            controllerSet[3].value = res.data.controllerICPStatus[0]
            controllerSet[3].isExtend = res.data.controllerICPStatus[1]
            controllerSet[4].value = res.data.controllerNote[0]
            controllerSet[4].isExtend = res.data.controllerNote[1]
            controllerSet[5].value = res.data.controllerTicket[0]
            controllerSet[5].isExtend = res.data.controllerTicket[1]
            controllerSet[6].value = res.data.controllerFavorite[0]
            controllerSet[6].isExtend = res.data.controllerFavorite[1]
          } else {
            saveControllerSetting()
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function loadDateShift() {
      axios
        .get(`https://${ServiceDomainLocal}:9487/dutycheck`)
        .then((res) => {
          dataShift.duty = res.data.Duty
          dataShift.standby = res.data.Standby
        })
        .catch((error) => {
          console.log(error)
        })
    }

    async function loadHyperLink() {
      const res = await axios.get(`https://${ServiceDomainLocal}:9487/hyperlink/query`)
      essentialLinks.value = res.data
    }

    function addHyperLink() {
      const postData = {
        action: 'AddLink',
        newSet: hyperlinkSet
      }
      axios
        .post(`https://${ServiceDomainLocal}:9487/hyperlink`, postData)
        .then((res) => {
          console.log(res)
          if (res.status === 200) {
            hyperlinkSet.title = ''
            hyperlinkSet.caption = ''
            hyperlinkSet.link = ''
            isShowAddHyperLink.value = false
            loadHyperLink()
          } else {
            alert(res.response)
          }
        })
        .catch((error) => {
          console.log(error)
          alert(`existed item - ${hyperlinkSet.title}`)
        })
    }

    // for hyperlink setting table
    function callHyperlink() {
      loadHyperLink()
      rows.value = _.cloneDeep(essentialLinks.value)
      isShowHpyerLinkSetting.value = true
    }

    function updateHyperByTable() {
      console.log(rows.value)
      const postData = {
        action: 'updateLink',
        adjustSet: rows.value
      }
      axios
        .post(`https://${ServiceDomainLocal}:9487/hyperlink`, postData)
        .then((res) => {
          if (res.status === 200) {
            isShowHpyerLinkSetting.value = false
            loadHyperLink()
          } else {
            alert(res.response)
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function deleteHyperLink(targetSn, targetTitle) {
      console.log('hit deleteHyperLink')
      $q.dialog({
        title: 'Confirm',
        message: `Are you sure want to <span class="text-red">delete</span> <b>${targetTitle}</b>`,
        persistent: true,
        html: true,
        cancel: true,
        ok: {
          label: 'Delete'
        }
      }).onOk(() => {
        // do the remove by axios post
        console.log('do the remove by axios post')
        const postData = {
          action: 'removeLink',
          targetHyperLinkSn: targetSn,
          targetName: targetTitle
        }
        axios
          .post(`https://${ServiceDomainLocal}:9487/hyperlink`, postData)
          .then((res) => {
            if (res.status === 200) {
              console.log('in the axios post delete')
              console.log(rows.value)
              // adjust hyperlink setting table
              rows.value.forEach(function (item, index, object) {
                if (item.sn === targetSn) {
                  object.splice(index, 1)
                }
              })
              let seconds = 3
              const dialog = $q
                .dialog({
                  title: `${targetTitle} has been removed`,
                  message: `Auto closing in ${seconds} seconds`,
                  ok: true
                })
                .onOk(() => {
                  clearTimeout(timer)
                  loadHyperLink()
                })
                .onDismiss(() => {
                  clearTimeout(timer)
                })
              const timer = setInterval(() => {
                seconds--
                if (seconds > 0) {
                  dialog.update({
                    message: `Autoclosing in ${seconds} second${seconds > 1 ? 's' : ''}.`
                  })
                } else {
                  loadHyperLink()
                  clearInterval(timer)
                  dialog.hide()
                }
              }, 1000)
            } else {
              alert(res.response)
            }
          })
          .catch((error) => {
            console.log(error)
          })
      })
    }

    function searchButtonEvent() {
      console.log('hit searchButtonEvent')
      isSearchButtonOn.value = !isSearchButtonOn.value
      if (isLogin.group !== 'OPS') {
        // rollback the button status for history first
        isHistoryButtonOn.value = false
      }
    }

    function createTheList() {
      const step = ref(0) // loop step
      const loopShift = ref(CurShift.value) // store current shift on loop
      const loopDate = ref(Date.now())
      const tmpDateString = ref(date.formatDate(loopDate.value, 'YYYY-MM-DD'))
      const tmpISOString = ref(date.formatDate(loopDate.value, 'ddd'))
      for (step.value; step.value < 21; step.value++) {
        if (loopShift.value === 'M') {
          loopDate.value = date.subtractFromDate(loopDate.value, { days: 1 })
          loopShift.value = 'N'
          tmpDateString.value = date.formatDate(loopDate.value, 'YYYY-MM-DD')
          tmpISOString.value = date.formatDate(loopDate.value, 'ddd')
        } else if (loopShift.value === 'N') {
          loopShift.value = 'A'
        } else if (loopShift.value === 'A') {
          loopShift.value = 'M'
        }
        reviewList.value.push([
          `${tmpISOString.value}, ${tmpDateString.value} ${loopShift.value}`,
          step.value,
          tmpDateString.value,
          loopShift.value,
          false // to check if this shift is N shift, default is N shift
        ])
      }
      // // N shift will display next two shift option on the review dropdown button, so use this method to hidden the option
      // if (loopShift.value === 'N') {
      //   reviewList.value[0][4] = true
      //   reviewList.value[1][4] = true
      // }
    }

    function clickToWindowOpenReviewPage(targetDate, targetShift) {
      window.open(`https://${ServiceDomainLocal}:8082/healthMap`, '_blank')
    }

    function openNewPage(target) {
      console.log(target)
      if (target === 'kpi') {
        const postData = {
          dbSn: 34,
          action: 'updateCounter'
        }
        axios
          .post(`https://${ServiceDomainLocal}:9487/hyperlink`, postData)
          .then((res) => {
            if (res.status === 200) {
              // https://okta.opsware.xyz:8082/kpiReview
              window.open(`https://${ServiceDomainLocal}:9488/kpiReview`, '_blank')
            }
          })
          .catch((error) => {
            console.log(error)
          })
      } else {
        const postData = {
          dbSn: target.sn,
          action: 'updateCounter'
        }
        axios
          .post(`https://${ServiceDomainLocal}:9487/hyperlink`, postData)
          .then((res) => {
            if (res.status === 200) {
              if (target.title === 'NXG route profiles') {
                const newTargetLinkForNxgProfile = `${target.link}?user=${isLogin.value}`
                window.open(newTargetLinkForNxgProfile, '_blank')
              } else {
                window.open(target.link, '_blank')
              }
            }
          })
          .catch((error) => {
            console.log(error)
          })
      }
    }

    function adjustFavorite() {
      console.log('hit adjustFavorite')
      // get link table
      axios
        .get('https://okta.opsware.xyz:9487/hyperlink/query')
        .then((response) => {
          console.log(response)
          const optionsArray = ref(
            Object.entries(response.data).map(function (item, index, object) {
              return { label: item[1].title, value: item[1].sn }
            })
          )
          // check cur setting for this user
          const enableOptionsArray = ref(
            Object.entries(controllerSet[6].isExtend).map(function (item, index, object) {
              return item[1].sn
            })
          )
          // display the dialog
          $q.dialog({
            title: 'Choose your favorite hyperlink by yourself',
            message: 'Multiple links is allow, but suggest is less than 3 links',
            options: {
              type: 'checkbox',
              model: enableOptionsArray.value,
              items: optionsArray.value
            },
            cancel: true,
            persistent: true
          }).onOk((data) => {
            console.log('>>>> OK, received', data)
            updateFavoriteLink(data)
          })
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function updateFavoriteLink(targetArray) {
      const postData = reactive({
        currentUser: isLogin.value,
        currentFavoriteLink: targetArray
      })
      axios
        .post(
          `https://${ServiceDomainLocal}:9487/controller/updateFavoriteLink`,
          postData
        )
        .then((res) => {
          if (res.status === 200) {
            loadControllerSetting()
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function updateTheOnShiftList() {
      isShowOnShiftList.value = true
    }

    function reloadShiftInfo() {
      // when cancel or page reload will trigger this
      console.log(CurData.value)
      axios
        .get(`https://${ServiceDomainLocal}:9486/shiftTable/${CurData.value}/${CurShift.value}`)
        .then((res) => {
          if (res.data[1] === CurShift.value && res.data[2] === CurData.value) {
            onShiftResult.value = res.data[0]
            shiftDict.shift_leader = res.data[3].shift_leader
            shiftDict.title_handover = res.data[3].title_handover
            shiftDict.title_alert_handler = res.data[3].title_alert_handler
            shiftDict.title_message_handler = res.data[3].title_message_handler
            shiftDict.title_request_handler = res.data[3].title_request_handler
          } else {
            $q.notify({
              message: 'Shift teammates is not ready, Please click here to update',
              color: 'red-6',
              progress: true,
              html: true,
              actions: [
                {
                  icon: 'manage_accounts',
                  color: 'white',
                  handler: () => {
                    updateTheOnShiftList()
                  }
                }
              ]
            })
          }
        })
        .catch((error) => {
          console.log(error)
        })
    }

    function updateShiftInfo() {
      isShiftInfoUpdating.value = true
      const postData = reactive({
        date: CurData.value,
        shift: CurShift.value,
        shiftList: onShiftResult.value,
        shiftDetail: shiftDict
      })
      axios
        .post(`https://${ServiceDomainLocal}:9487/shiftTable`, postData)
        .then((res) => {
          console.log(res)
          isShiftInfoUpdating.value = false
          isShowOnShiftList.value = false
          $q.notify({
            message: 'Shift teammates info has been updated to <b>DB</b> & <b>Skype</b>',
            color: 'brown-6',
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
        .catch((error) => {
          console.log(error)
        })
    }

    function adjustCreateTicketSet(passObject) {
      if (passObject.action === 'cancel') {
        console.log('trigger CANCEL')
        createTicketSet.isShow = false
        // createTicketSet.isDialogShow = true
      } else if (passObject.action === 'added') {
        createTicketSet.refreshKey++
        createTicketSet.isDialogShow = false
        createTicketSet.isShow = false
      } else {
        console.log(passObject)
        console.log('not yet')
      }
    }

    // use this function to avoid the component (DHSCreateNewTicketPage) data gone
    function checkNewTicketStatus() {
      if (createTicketSet.isShow) {
        createTicketSet.isDialogShow = false
      } else {
        createTicketSet.isShow = true
      }
    }

    async function pullApiFunction() {
      // rollback the dict first
      PullApiDict.curShiftMember = []
      PullApiDict.nextShiftMember = []
      PullApiDict.curShift = ''

      // start the button loading
      PullApiDict.isLoading = true
      await axios
        .get(`https://${ServiceDomainLocal}:9487/dutycheck/ops`)
        .then((response) => {
          console.log(response)
          onShiftResult.value = response.data.curShiftMember
          PullApiDict.curShiftMember = response.data.curShiftMember
          PullApiDict.nextShiftMember = response.data.nextShiftMember
          PullApiDict.curShift = response.data.curShift
          PullApiDict.nextShift = response.data.nextShift
          shiftDict.shift_leader = response.data.curShiftMember[0]
        })
        .catch((error) => {
          console.log(error)
        })
      PullApiDict.isLoading = false
    }

    function historyButtonEvent() {
      console.log('hit historyButtonEvent')
      isHistoryButtonOn.value = !isHistoryButtonOn.value
      // set default for search button
      isSearchButtonOn.value = false
    }

    // let ops user change the shift leader
    function changeShiftLeader(targetName) {
      console.log('hit changeShiftLeader')
      shiftDict.shift_leader = targetName
    }

    function changeTitle(source, targetName) {
      switch (source) {
        case 'handover':
          if (shiftDict.title_handover.includes(targetName)) {
            shiftDict.title_handover.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_handover.push(targetName)
          }
          break
        case 'alert':
          if (shiftDict.title_alert_handler.includes(targetName)) {
            shiftDict.title_alert_handler.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_alert_handler.push(targetName)
          }
          break
        case 'message':
          if (shiftDict.title_message_handler.includes(targetName)) {
            shiftDict.title_message_handler.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_message_handler.push(targetName)
          }
          break
        case 'request':
          if (shiftDict.title_request_handler.includes(targetName)) {
            shiftDict.title_request_handler.forEach(function (item, index, object) {
              if (item === targetName) {
                object.splice(index, 1)
              }
            })
          } else {
            shiftDict.title_request_handler.push(targetName)
          }
          break
      }
    }

    // query backend server
    initIntervalQuery()

    onMounted(() => {
      scriptContainer.value = document.createElement('script')
      scriptContainer.value.setAttribute('src', 'https://apis.google.com/js/api.js')
      document.head.appendChild(scriptContainer.value)
    })

    onBeforeUnmount(() => {
      clearInterval(selfinitTime.value)
    })

    watch(
      () => isLogin.status,
      (curValue, oldValue) => {
        if (curValue !== true) {
          console.log('need to reload')
        } else {
          initIntervalQuery()
        }
      }
    )

    return {
      ServiceDomainLocal,
      essentialLinks,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value
      },
      init,
      CurData,
      CurShift,
      isLogin,
      buttonLogout,
      isSync,
      getScrollTarget,
      setVerticalScrollPosition,
      router,
      localDataSync,
      selfTime,
      selfinitTime,
      scrollToTheTitle,
      controllerSet,
      closeAllTicketStatusBar,
      createNewNote,
      saveControllerSetting,
      loadControllerSetting,
      dataShift,
      loadDateShift,
      loadHyperLink,
      addHyperLink,
      isShowAddHyperLink,
      isShowHpyerLinkSetting,
      hyperlinkSet,
      columns,
      rows,
      callHyperlink,
      updateHyperByTable,
      options,
      deleteHyperLink,
      searchButtonEvent,
      historyButtonEvent,
      isSearchButtonOn,
      isHistoryButtonOn,
      createTheList,
      reviewList,
      clickToWindowOpenReviewPage,
      openNewPage,
      adjustFavorite,
      updateTheOnShiftList,
      isShowOnShiftList,
      shiftList,
      onShiftResult,
      reloadShiftInfo,
      updateShiftInfo,
      isShiftInfoUpdating,
      createTicketSet,
      adjustCreateTicketSet,
      checkNewTicketStatus,
      pullApiFunction,
      PullApiDict,
      changeShiftLeader,
      shiftDict,
      changeTitle
    }
  }
})
</script>

<style lang="scss">
.customChildAutoHeigth {
  height: 100% !important;
}

.customChildMinHeight {
  min-height: 400px !important;
}

.customEllipsis {
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  overflow: hidden !important;
}

div.custom-border-display {
  &.otrs {
    outline: 0.2rem solid #afeeee;
  }

  &.note {
    outline: 0.2rem solid #fffdd0;
  }

  &.jira {
    outline: 0.2rem solid #ffe4e1;
  }

  &.jsmNet {
    border-bottom: 0.2rem dashed #ffe4e1;
  }
}
</style>
