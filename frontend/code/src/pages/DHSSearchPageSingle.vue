<template>
    <div class="q-pa-md">
        <section class="row q-px-lg">
            <q-input square outlined v-model="localSet.keyword1" @keyup.enter="startSearch" label="Keyword?" />
            <q-btn color="black" label="Search" @click="startSearch" />
        </section>
    </div>
    <div class="row q-px-lg">
        <q-table flat bordered class="my-sticky-header-table col" :rows="sortTicketSet" :columns="columns"
            :pagination="pagination">
            <template v-slot:body="props">
                <q-tr :props="props">
                    <q-td key="title" :props="props">
                        <q-list>
                            <q-item>
                                <q-item-section>
                                    <q-item-label>
                                        <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                            label="Title" />{{ props.row.title }}
                                    </q-item-label>
                                    <q-item-label caption>
                                        <section class="q-mb-xs">
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Category" />{{ props.row.category }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="BizUnit" />{{ props.row.bizUnit }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Infra" />{{ props.row.infra }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Create at" />{{ props.row.createdTime }}
                                        </section>
                                        <q-badge class="q-mr-xs q-mb-xs text-caption" color="green-2" text-color="black"
                                            label="Description" />
                                        <q-badge v-if="props.row.raw === 2"
                                            class="q-mr-xs q-mb-xs text-caption cursor-pointer" color="yellow-4"
                                            text-color="black" label="Mail"
                                            @click="popupEmailContent(props.row.sn, 'OPS')" />
                                        <q-badge v-else class="q-mr-xs q-mb-xs text-caption disabled" color="green-2"
                                            text-color="black" label="Internal" />
                                        <q-badge class="q-mr-xs q-mb-xs text-caption cursor-pointer" color="yellow-4"
                                            text-color="black" label="History"
                                            @click="popupComments(props.row.sn, 'OPS')" />
                                        <section class="q-pa-xs" v-html="props.row.description"></section>
                                    </q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-td>
                </q-tr>
            </template>
        </q-table>
        <q-table flat bordered class="my-sticky-header-table col" :rows="sortSysTicketSet" :columns="columnsSys"
            :pagination="pagination">
            <template v-slot:body="props">
                <q-tr :props="props">
                    <q-td key="title" :props="props">
                        <q-list>
                            <q-item>
                                <q-item-section>
                                    <q-item-label>
                                        <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                            label="Title" />{{ props.row.title }}
                                    </q-item-label>
                                    <q-item-label caption>
                                        <section class="q-mb-xs">
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Category" />{{ props.row.custom_category }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="BizUnit" />{{ props.row.custom_bizUnit }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Priority" />{{ props.row.custom_priority }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Create at" />{{ props.row.createdTime }}
                                        </section>
                                        <q-badge class="q-mr-xs q-mb-xs text-caption" color="green-2" text-color="black"
                                            label="Description" />
                                        <q-badge class="q-mr-xs q-mb-xs text-caption cursor-pointer" color="yellow-4"
                                            text-color="black" label="History"
                                            @click="popupComments(props.row.sn, 'SYS')" />
                                        <section class="q-pa-xs" v-html="props.row.description"></section>
                                    </q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-td>
                </q-tr>
            </template>
        </q-table>
    </div>
    <div class="row q-px-lg q-mb-lg">
        <q-table flat bordered class="my-sticky-header-table col" :rows="sortNetTicketSet" :columns="columnsNet"
            :pagination="pagination">
            <template v-slot:body="props">
                <q-tr :props="props">
                    <q-td key="title" :props="props">
                        <q-list>
                            <q-item>
                                <q-item-section>
                                    <q-item-label>
                                        <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                            label="Title" />{{ props.row.title }}
                                    </q-item-label>
                                    <q-item-label caption>
                                        <section class="q-mb-xs">
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Category" />{{ props.row.custom_category }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Infra" />{{ props.row.custom_infra }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Facilities" />{{ props.row.custom_facilities }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Vendor" />{{ props.row.custom_vendor }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Create at" />{{ props.row.createdTime }}
                                        </section>
                                        <q-badge class="q-mr-xs q-mb-xs text-caption" color="green-2" text-color="black"
                                            label="Description" />
                                        <q-badge class="q-mr-xs q-mb-xs text-caption cursor-pointer" color="yellow-4"
                                            text-color="black" label="History"
                                            @click="popupComments(props.row.sn, 'NET')" />
                                        <section class="q-pa-xs" v-html="props.row.description"></section>
                                    </q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-td>
                </q-tr>
            </template>
        </q-table>
        <q-table flat bordered class="my-sticky-header-table col" :rows="sortDbaTicketSet" :columns="columnsDba"
            :pagination="pagination">
            <template v-slot:body="props">
                <q-tr :props="props">
                    <q-td key="title" :props="props">
                        <q-list>
                            <q-item>
                                <q-item-section>
                                    <q-item-label>
                                        <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                            label="Title" />{{ props.row.title }}
                                    </q-item-label>
                                    <q-item-label caption>
                                        <section class="q-mb-xs">
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Category" />{{ props.row.custom_category }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="BizUnit" />{{ props.row.custom_bizUnit }}
                                            <q-badge class="q-mr-xs text-caption" color="green-2" text-color="black"
                                                label="Create at" />{{ props.row.createdTime }}
                                        </section>
                                        <q-badge class="q-mr-xs q-mb-xs text-caption" color="green-2" text-color="black"
                                            label="Description" />
                                        <q-badge class="q-mr-xs q-mb-xs text-caption cursor-pointer" color="yellow-4"
                                            text-color="black" label="History"
                                            @click="popupComments(props.row.sn, 'DBA')" />
                                        <section class="q-pa-xs" v-html="props.row.description"></section>
                                    </q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-td>
                </q-tr>
            </template>
        </q-table>
    </div>
</template>

<script>

import axios from 'axios'
import { useStore } from 'vuex'
import { useQuasar } from 'quasar'
import { reactive, ref, computed, onBeforeUnmount } from 'vue'
// import { onMounted, reactive, ref, computed } from 'vue'
import _ from 'lodash'

export default {
    name: 'SearchPage',
    setup() {
        const $store = useStore()
        const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
        const $q = useQuasar()
        const localSet = reactive({
            rows: [],
            rows_sys: [],
            rows_net: [],
            rows_dba: [],
            keyword1: '',
            keyword2: '',
            keyword3: ''
        })

        const timer = ref()

        const sortTicketSet = computed(() => _.orderBy(localSet.rows, 'mapping', ['desc'])) // order by noteSet.sequence
        const sortSysTicketSet = computed(() => _.orderBy(localSet.rows_sys, 'mapping', ['desc'])) // order by noteSet.sequence
        const sortNetTicketSet = computed(() => _.orderBy(localSet.rows_net, 'mapping', ['desc'])) // order by noteSet.sequence
        const sortDbaTicketSet = computed(() => _.orderBy(localSet.rows_dba, 'mapping', ['desc'])) // order by noteSet.sequence
        const pagination = ref({
            rowsPerPage: 0
        })
        const separator = ref('horizontal')
        const filter = ref('')
        const columns = [
            { name: 'title', label: 'Result on OPS JSM', align: 'left', field: 'title' }
        ]
        const columnsSys = [
            { name: 'title', label: 'Result on SYS JSM', align: 'left', field: 'title' }
        ]
        const columnsNet = [
            { name: 'title', label: 'Result on NET JSM', align: 'left', field: 'title' }
        ]
        const columnsDba = [
            { name: 'title', label: 'Result on DBA JSM', align: 'left', field: 'title' }
        ]

        async function startSearch() {
            $q.loading.show()
            try {
                const res = await axios.get(
                    `https://${ServiceDomainLocal}:9487/bpQuery/search/${localSet.keyword1}`
                )
                localSet.rows = _.cloneDeep(res.data.ops_result)
                localSet.rows_sys = _.cloneDeep(res.data.sys_result)
                localSet.rows_net = _.cloneDeep(res.data.net_result)
                localSet.rows_dba = _.cloneDeep(res.data.dba_result)
                $q.loading.hide()
            } catch (e) {
                console.log(e)
                $q.loading.hide()
                alert(e)
            }
        }

        function popupEmailContent(target, whichTeam) {
            axios
                .get(`https://${ServiceDomainLocal}:9487/bpQuery/checkEmail/${whichTeam}/${target}`)
                .then((res) => {
                    $q.dialog({
                        message: res.data,
                        html: true,
                        fullWidth: true
                    }).onOk(() => {
                        // console.log('OK')
                    }).onCancel(() => {
                        // console.log('Cancel')
                    }).onDismiss(() => {
                        // console.log('I am triggered on both OK and Cancel')
                    })
                })
                .catch((error) => {
                    alert(error)
                    console.log(error)
                })
        }

        function popupComments(target, whichTeam) {
            axios
                .get(`https://${ServiceDomainLocal}:9487/bpQuery/checkComments/${whichTeam}/${target}`)
                .then((res) => {
                    $q.dialog({
                        message: res.data,
                        html: true,
                        fullWidth: true
                    }).onOk(() => {
                        // console.log('OK')
                    }).onCancel(() => {
                        // console.log('Cancel')
                    }).onDismiss(() => {
                        // console.log('I am triggered on both OK and Cancel')
                    })
                })
                .catch((error) => {
                    alert(error)
                    console.log(error)
                })
        }

        onBeforeUnmount(() => {
            if (timer.value !== void 0) {
                clearTimeout(timer.value)
                $q.loading.hide()
            }
        })

        // onMounted(async () => {
        //     try {
        //         const res = await axios.get(
        //             `https://${ServiceDomainLocal}:9487/bpQuery/search/26691`
        //         )
        //         localSet.rows = _.cloneDeep(res.data.result)
        //     } catch (e) {
        //         console.log(e)
        //     }
        // })
        return { columns, columnsSys, columnsNet, columnsDba, localSet, pagination, startSearch, separator, filter, sortTicketSet, sortSysTicketSet, sortNetTicketSet, sortDbaTicketSet, popupEmailContent, popupComments }
    }
}
</script>
<style lang="sass">
.my-sticky-header-table
  /* height or max-height is important */
  height: 500px

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    /* bg color is important for th; just specify one */
    background-color: #c1f4cd

  thead tr th
    position: sticky
    z-index: 1
  thead tr:first-child th
    top: 0

  /* this is when the loading indicator appears */
  &.q-table--loading thead tr:last-child th
    /* height of all previous header rows */
    top: 48px
</style>
