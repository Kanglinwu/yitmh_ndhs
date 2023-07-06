<!-- @format -->

<template>
  <q-dialog v-model="isShowKpiDetail" full-width>
    <q-card>
      <q-card-section>
        <div class="text-h6">
          Detail - {{ kpiDetailWho }} - {{ kpiDetailLevel }} on {{ kpiDetailDuration }}
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div v-for="x in kpiDetail" :key="x.sourceSn">
          <section v-if="kpiDetailLevel == 'handlerR'">
            <li>
              <span class="text-subtitle1 text-red-4">{{ x.date }}</span> -
              <span class="text-subtitle1 q-pl-xs">
                {{ x.title }}
              </span>
            </li>
          </section>
          <section v-else>
            <li>
              <span class="text-subtitle1 text-red-4">{{ x.date }}</span> -
              <span class="text-subtitle1" v-if="x.status">
                <q-icon color="green" name="done" />
              </span>
              <span class="text-subtitle1" v-else>
                <q-icon color="red" name="close" />
              </span>
              -
              <span class="text-subtitle1">
                {{ x.title }}
              </span>
            </li>
          </section>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="bg-white text-teal">
        <q-btn flat label="OK" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <!-- <q-select
    class="q-ma-md q-pd-md"
    v-model="whichMonth"
    :options="monthOptions"
    label="KPI"
  /> -->
  <div class="q-pa-md q-ma-md">
    <div class="q-gutter-sm">
      <div class="row">2021</div>
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="2021"
        label="Total"
      />
      <br />
      <div class="row">2022</div>
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="2022"
        label="Total"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202201"
        label="January"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202202"
        label="February"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202203"
        label="March"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202204"
        label="April"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202205"
        label="May"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202206"
        label="June"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202207"
        label="July"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202208"
        label="August"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202209"
        label="September"
      />
      <q-radio
        v-model="whichMonth"
        checked-icon="task_alt"
        unchecked-icon="panorama_fish_eye"
        val="202210"
        label="October"
      />
    </div>
  </div>
  <div class="q-ma-md">
    <q-table
      :rows="summaryTable"
      :columns="columns"
      :pagination="pagination"
      dense
      separator="cell"
      row-key="name"
    >
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            <q-badge
              :color="pplColor(props.row.name)[0]"
              :text-color="pplColor(props.row.name)[1]"
              :label="props.row.name"
            />
          </q-td>
          <q-td key="handlerR" :props="props">
            <span
              v-if="props.row.handlerR !== 0 && props.row.name !== 'Total'"
              class="cursor-pointer text-blue"
              @click="checkDetail('handlerR', props.row.name, props.row.date)"
              >{{ props.row.handlerR }}
              <span class="text-italic text-grey-6">
                ({{
                  Math.round((props.row.handlerR / totalData.handlerR) * 10000) / 100.0
                }}%)
              </span>
            </span>
            <span v-else>
              {{ props.row.handlerR }}
            </span>
          </q-td>
          <q-td key="handlerT" :props="props">
            <span
              v-if="props.row.handlerT !== 0 && props.row.name !== 'Total'"
              class="cursor-pointer text-blue"
              @click="checkDetail('handlerT', props.row.name, props.row.date)"
              >{{ props.row.handlerT }}
              <span class="text-italic text-grey-6">
                ({{
                  Math.round((props.row.handlerT / totalData.handlerT) * 10000) / 100.0
                }}%)
              </span>
            </span>
            <span v-else>
              {{ props.row.handlerT }}
            </span>
          </q-td>
          <q-td key="handlerTs" :props="props">
            <span
              v-if="props.row.handlerTs !== 0 && props.row.name !== 'Total'"
              class="cursor-pointer text-blue"
              @click="checkDetail('handlerTs', props.row.name, props.row.date)"
              >{{ props.row.handlerTs }}
              <span class="text-italic text-grey-6">
                ({{
                  Math.round((props.row.handlerTs / totalData.handlerTs) * 10000) / 100.0
                }}%)
              </span>
            </span>
            <span v-else>
              {{ props.row.handlerTs }}
            </span>
          </q-td>
          <q-td key="handlerTp" :props="props">
            <span
              v-if="props.row.handlerTp !== 0 && props.row.name !== 'Total'"
              class="cursor-pointer text-blue"
              @click="checkDetail('handlerTp', props.row.name, props.row.date)"
              >{{ props.row.handlerTp }}
              <span class="text-italic text-grey-6">
                ({{
                  Math.round((props.row.handlerTp / totalData.handlerTp) * 10000) / 100.0
                }}%)
              </span>
            </span>
            <span v-else>
              {{ props.row.handlerTp }}
            </span>
          </q-td>
          <q-td key="handleraT" :props="props">
            <span
              v-if="props.row.handleraT !== 0 && props.row.name !== 'Total'"
              class="cursor-pointer text-blue"
              @click="checkDetail('handleraT', props.row.name, props.row.date)"
              >{{ props.row.handleraT }}
              <span class="text-italic text-grey-6">
                ({{
                  Math.round((props.row.handleraT / totalData.handleraT) * 10000) / 100.0
                }}%)
              </span>
            </span>
            <span v-else>
              {{ props.row.handleraT }}
            </span>
          </q-td>
          <q-td key="handleraTs" :props="props">
            <span
              v-if="props.row.handleraTs !== 0 && props.row.name !== 'Total'"
              class="cursor-pointer text-blue"
              @click="checkDetail('handleraTs', props.row.name, props.row.date)"
              >{{ props.row.handleraTs }}
              <span class="text-italic text-grey-6">
                ({{
                  Math.round((props.row.handleraTs / totalData.handleraTs) * 10000) /
                  100.0
                }}%)
              </span>
            </span>
            <span v-else>
              {{ props.row.handleraTs }}
            </span>
          </q-td>
          <q-td key="handleraTp" :props="props">
            <span
              v-if="props.row.handleraTp !== 0 && props.row.name !== 'Total'"
              class="cursor-pointer text-blue"
              @click="checkDetail('handleraTp', props.row.name, props.row.date)"
              >{{ props.row.handleraTp }}
              <span class="text-italic text-grey-6">
                ({{
                  Math.round((props.row.handleraTp / totalData.handleraTp) * 10000) /
                  100.0
                }}%)
              </span>
            </span>
            <span v-else>
              {{ props.row.handleraTp }}
            </span>
          </q-td>
          <q-td key="score" :props="props">
            <span v-if="props.row.name !== 'Total'" class="text-bold">{{
              props.row.score
            }}</span>
            <span v-else class="text-italic"> None </span>
          </q-td>
        </q-tr>
      </template>
      <!-- <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <div>
            <q-badge
              :color="pplColor(props.value)[0]"
              :text-color="pplColor(props.value)[1]"
              :label="props.value"
            />
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-handlerR="props">
        <q-td :props="props">
          <span class="cursor-pointer text-blue" @click="checkDetail">{{
            props.value
          }}</span>
        </q-td>
      </template> -->
    </q-table>
    <div class="row">
      <Bar
        class="col"
        v-if="loaded"
        :chart-options="chartOptions"
        :chart-data="chartData"
        :chart-id="chartId"
        :dataset-id-key="datasetIdKey"
        :plugins="plugins"
        :css-classes="cssClasses"
        :styles="styles"
        :width="width"
        :height="height"
      />
    </div>
    <div class="row">
      <Bar
        class="col"
        v-if="loaded && chartData2.datasets.length !== 0"
        :chart-options="chartOptions2"
        :chart-data="chartData2"
        :chart-id="chartId"
        :dataset-id-key="datasetIdKey"
        :plugins="plugins"
        :css-classes="cssClasses"
        :styles="styles"
        :width="width"
        :height="height"
      />
      <Bar
        class="col"
        v-if="loaded && chartData3.datasets.length !== 0"
        :chart-options="chartOptions3"
        :chart-data="chartData3"
        :chart-id="chartId"
        :dataset-id-key="datasetIdKey"
        :plugins="plugins"
        :css-classes="cssClasses"
        :styles="styles"
        :width="width"
        :height="height"
      />
      <Bar
        class="col"
        v-if="loaded && chartData4.datasets.length !== 0"
        :chart-options="chartOptions4"
        :chart-data="chartData4"
        :chart-id="chartId"
        :dataset-id-key="datasetIdKey"
        :plugins="plugins"
        :css-classes="cssClasses"
        :styles="styles"
        :width="width"
        :height="height"
      />
    </div>
    <div class="row">
      <Bar
        class="col"
        v-if="loaded && chartData5.datasets.length !== 0"
        :chart-options="chartOptions5"
        :chart-data="chartData5"
        :chart-id="chartId"
        :dataset-id-key="datasetIdKey"
        :plugins="plugins"
        :css-classes="cssClasses"
        :styles="styles"
        :width="width"
        :height="height"
      />
      <Bar
        class="col"
        v-if="loaded && chartData6.datasets.length !== 0"
        :chart-options="chartOptions6"
        :chart-data="chartData6"
        :chart-id="chartId"
        :dataset-id-key="datasetIdKey"
        :plugins="plugins"
        :css-classes="cssClasses"
        :styles="styles"
        :width="width"
        :height="height"
      />
      <Bar
        class="col"
        v-if="loaded && chartData7.datasets.length !== 0"
        :chart-options="chartOptions7"
        :chart-data="chartData7"
        :chart-id="chartId"
        :dataset-id-key="datasetIdKey"
        :plugins="plugins"
        :css-classes="cssClasses"
        :styles="styles"
        :width="width"
        :height="height"
      />
    </div>
  </div>
  <!-- <div v-if="loaded" class="q-ma-md q-pd-md text-center">
    <div class="row">
      <span class="col-12 text-center bg-blue-grey-5 text-subtitle1 text-white">
        {{ whichMonth }}
      </span>
    </div>
    <div v-for="i in sortChartDataSet" :key="i.label" class="row">
      <span class="col-1" :style="'background-color:' + i.backgroundColor"> </span>
      <span class="col"> {{ i.label }}</span>
      <span class="col"> {{ i.data[0] }}</span>
    </div>
  </div> -->
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { ref, onMounted, computed, watch, reactive } from 'vue'
import axios from 'axios'
import _ from 'lodash'
import { useStore } from 'vuex'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'BarChart',
  components: { Bar },
  props: {
    chartId: {
      type: String,
      default: 'bar-chart'
    },
    datasetIdKey: {
      type: String,
      default: 'label'
    },
    width: {
      type: Number,
      default: 400
    },
    height: {
      type: Number,
      default: 400
    },
    cssClasses: {
      default: '',
      type: String
    },
    styles: {
      type: Object,
      default: () => {}
    },
    plugins: {
      type: Array,
      default: () => []
    }
  },
  setup() {
    const $store = useStore()
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const loaded = ref(false)
    const initialState = {
      datasets: [],
      labels: []
    }
    const initialStateTotal = {
      name: '',
      handlerR: 0,
      handlerT: 0,
      handlerTs: 0,
      handlerTp: 0,
      handleraT: 0,
      handleraTs: 0,
      handleraTp: 0,
      score: 0
    }
    const chartData = reactive({ ...initialState })
    const chartData2 = reactive({ ...initialState })
    const chartData3 = reactive({ ...initialState })
    const chartData4 = reactive({ ...initialState })
    const chartData5 = reactive({ ...initialState })
    const chartData6 = reactive({ ...initialState })
    const chartData7 = reactive({ ...initialState })
    const totalData = reactive({ ...initialStateTotal })
    const summaryTable = ref([])
    const whichMonth = ref('2022')
    const isShowKpiDetail = ref(false)
    const kpiDetail = ref([])
    const kpiDetailWho = ref('')
    const kpiDetailLevel = ref('')
    const kpiDetailDuration = ref('')
    const chartOptions = reactive({
      responsive: true,
      maintainAspectRatio: false,
      // maxBarThickness: 100,
      minBarLength: 5,
      indexAxis: 'y',
      scales: {
        y: {
          display: false
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          align: 'start'
          // labels: {
          //   generateLabels: () => {
          //     return sortChartDataSet.value.map((element, index, array) => ({
          //       text: `${element.label} - Total: ${element.data[0]}`,
          //       fillStyle: element.backgroundColor
          //     }))
          //   }
          // }
        },
        title: {
          display: true,
          text: 'Regular operation - handler'
        }
      }
    })
    const chartOptions2 = reactive({
      responsive: true,
      maintainAspectRatio: false,
      // maxBarThickness: 100,
      minBarLength: 5,
      indexAxis: 'y',
      scales: {
        y: {
          display: false
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          align: 'start'
          // labels: {
          //   generateLabels: () => {
          //     return sortChartDataSet.value.map((element, index, array) => ({
          //       text: `${element.label} - Total: ${element.data[0]}`,
          //       fillStyle: element.backgroundColor
          //     }))
          //   }
          // }
        },
        title: {
          display: true,
          text: 'Troubleshooting - handler'
        }
      }
    })
    const chartOptions3 = reactive({
      responsive: true,
      maintainAspectRatio: false,
      // maxBarThickness: 100,
      minBarLength: 5,
      indexAxis: 'y',
      scales: {
        y: {
          display: false
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          align: 'start'
          // labels: {
          //   generateLabels: () => {
          //     return sortChartDataSet.value.map((element, index, array) => ({
          //       text: `${element.label} - Total: ${element.data[0]}`,
          //       fillStyle: element.backgroundColor
          //     }))
          //   }
          // }
        },
        title: {
          display: true,
          text: 'Troubleshooting - handler_second'
        }
      }
    })
    const chartOptions4 = reactive({
      responsive: true,
      maintainAspectRatio: false,
      // maxBarThickness: 100,
      minBarLength: 5,
      indexAxis: 'y',
      scales: {
        y: {
          display: false
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          align: 'start'
          // labels: {
          //   generateLabels: () => {
          //     return sortChartDataSet.value.map((element, index, array) => ({
          //       text: `${element.label} - Total: ${element.data[0]}`,
          //       fillStyle: element.backgroundColor
          //     }))
          //   }
          // }
        },
        title: {
          display: true,
          text: 'Troubleshooting - participant'
        }
      }
    })
    const chartOptions5 = reactive({
      responsive: true,
      maintainAspectRatio: false,
      // maxBarThickness: 100,
      minBarLength: 5,
      indexAxis: 'y',
      scales: {
        y: {
          display: false
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          align: 'start'
          // labels: {
          //   generateLabels: () => {
          //     return sortChartDataSet.value.map((element, index, array) => ({
          //       text: `${element.label} - Total: ${element.data[0]}`,
          //       fillStyle: element.backgroundColor
          //     }))
          //   }
          // }
        },
        title: {
          display: true,
          text: 'Advence troubleshooting - handler'
        }
      }
    })
    const chartOptions6 = reactive({
      responsive: true,
      maintainAspectRatio: false,
      // maxBarThickness: 100,
      minBarLength: 5,
      indexAxis: 'y',
      scales: {
        y: {
          display: false
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          align: 'start'
          // labels: {
          //   generateLabels: () => {
          //     return sortChartDataSet.value.map((element, index, array) => ({
          //       text: `${element.label} - Total: ${element.data[0]}`,
          //       fillStyle: element.backgroundColor
          //     }))
          //   }
          // }
        },
        title: {
          display: true,
          text: 'Advence troubleshooting - handler_second'
        }
      }
    })
    const chartOptions7 = reactive({
      responsive: true,
      maintainAspectRatio: false,
      // maxBarThickness: 100,
      minBarLength: 5,
      indexAxis: 'y',
      scales: {
        y: {
          display: false
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          align: 'start'
          // labels: {
          //   generateLabels: () => {
          //     return sortChartDataSet.value.map((element, index, array) => ({
          //       text: `${element.label} - Total: ${element.data[0]}`,
          //       fillStyle: element.backgroundColor
          //     }))
          //   }
          // }
        },
        title: {
          display: true,
          text: 'Advence troubleshooting - participant'
        }
      }
    })

    const columns = [
      {
        name: 'name',
        label: 'Name',
        field: 'name',
        align: 'left',
        sortable: true
      },
      {
        name: 'handlerR',
        label: 'Reqular operation - handler',
        align: 'left',
        field: 'handlerR',
        sortable: true
      },
      {
        name: 'handlerT',
        align: 'left',
        label: 'Troubleshooting - handler',
        field: 'handlerT',
        sortable: true
      },
      {
        name: 'handlerTs',
        align: 'left',
        label: 'Troubleshooting - handler_second',
        field: 'handlerTs',
        sortable: true
      },
      {
        name: 'handlerTp',
        align: 'left',
        label: 'Troubleshooting - participant',
        field: 'handlerTp',
        sortable: true
      },
      {
        name: 'handleraT',
        align: 'left',
        label: 'Advence troubleshooting - handler',
        field: 'handleraT',
        sortable: true
      },
      {
        name: 'handleraTs',
        align: 'left',
        label: 'Advence troubleshooting - handler_second',
        field: 'handleraTs',
        sortable: true
      },
      {
        name: 'handleraTp',
        align: 'left',
        label: 'Advence troubleshooting - participant',
        field: 'handleraTp',
        sortable: true
      },
      {
        name: 'score',
        align: 'left',
        label: 'calculaed score',
        field: 'score',
        sortable: true,
        required: true
      }
    ]

    const monthOptions = [
      {
        label: '2021 Total',
        value: '2021'
      },
      {
        label: '2021 January',
        value: '202101'
      },
      {
        label: '2021 February',
        value: '202102'
      },
      {
        label: '2021 March',
        value: '202103'
      },
      {
        label: '2021 April',
        value: '202104'
      },
      {
        label: '2021 May',
        value: '202105'
      },
      {
        label: '2021 June',
        value: '202106'
      },
      {
        label: '2021 July',
        value: '202107'
      },
      {
        label: '2021 August',
        value: '202108'
      },
      {
        label: '2021 September',
        value: '202109'
      },
      {
        label: '2021 October',
        value: '202110'
      },
      {
        label: '2021 November',
        value: '202111'
      },
      {
        label: '2021 December',
        value: '202112'
      }
    ]
    const sortChartDataSet = computed(() =>
      _.orderBy(
        chartData.datasets,
        [
          function (o) {
            return o.data[0]
          }
        ],
        ['desc']
      )
    )

    const sortChartDataSet2 = computed(() =>
      _.orderBy(
        chartData2.datasets,
        [
          function (o) {
            return o.data[0]
          }
        ],
        ['desc']
      )
    )
    const sortChartDataSet3 = computed(() =>
      _.orderBy(
        chartData3.datasets,
        [
          function (o) {
            return o.data[0]
          }
        ],
        ['desc']
      )
    )
    const sortChartDataSet4 = computed(() =>
      _.orderBy(
        chartData4.datasets,
        [
          function (o) {
            return o.data[0]
          }
        ],
        ['desc']
      )
    )
    const sortChartDataSet5 = computed(() =>
      _.orderBy(
        chartData5.datasets,
        [
          function (o) {
            return o.data[0]
          }
        ],
        ['desc']
      )
    )
    const sortChartDataSet6 = computed(() =>
      _.orderBy(
        chartData6.datasets,
        [
          function (o) {
            return o.data[0]
          }
        ],
        ['desc']
      )
    )
    const sortChartDataSet7 = computed(() =>
      _.orderBy(
        chartData7.datasets,
        [
          function (o) {
            return o.data[0]
          }
        ],
        ['desc']
      )
    )

    const displayTable = computed(() =>
      _.filter(chartData.datasets, function (o) {
        return o
      })
    )

    function pplColor(targetName) {
      // 'Aiden', 'Albert', 'Alex', 'Asky', 'Bayu', 'Bob', 'Cadalora', 'Cyril',
      // 'Daniel', 'Danny', 'Eric', 'Gary', 'Huck', 'Ivan', 'Keven', 'Larry',
      // 'Thurston', 'Rorschach'
      switch (targetName) {
        case 'Aiden':
          // FFCDD2
          // EF9A9A
          return ['red-2', 'dark']
        case 'Albert':
          // F8BBD0
          // F48FB1
          return ['pink-2', 'dark']
        case 'Alex':
          // E1BEE7
          // CE93D8
          return ['purple-2', 'dark']
        case 'Asky':
          // D1C4E9
          // B39DDB
          return ['deep-purple-2', 'dark']
        case 'Bayu':
          // C5CAE9
          // 9FA8DA
          return ['indigo-2', 'dark']
        case 'Bob':
          // BBDEFB
          // 90CAF9
          return ['blue-2', 'dark']
        case 'Cadalora':
          // B3E5FC
          // 81D4FA
          return ['light-blue-2', 'dark']
        case 'Cyril':
          // B2EBF2
          // 80DEEA
          return ['cyan-2', 'dark']
        case 'Daniel':
          // F0F4C3
          // E6EE9C
          return ['lime-2', 'dark']
        case 'Danny':
          // FB8C00
          // FFE0B2
          return ['orange-7', 'white']
        case 'Eric':
          // DCEDC8
          // C5E1A5
          return ['light-green-2', 'dark']
        case 'Gary':
          // FFF9C4
          // FFF176
          return ['yellow-2', 'dark']
        case 'Huck':
          // FFECB3
          // FFE082
          return ['amber-2', 'dark']
        case 'Ivan':
          // D7CCC8
          // BCAAA4
          return ['brown-2', 'dark']
        case 'Keven':
          // FFCCBC
          // FFAB91
          return ['deep-orange-2', 'dark']
        case 'Larry':
          // C8E6C9
          // A5D6A7
          return ['green-2', 'dark']
        case 'Thurston':
          // CFD8DC
          // B0BEC5
          return ['blue-grey-2', 'dark']
        case 'Rorschach':
          // D32F2F
          // B71C1C
          return ['red-8', 'white']
        default:
          // F5F5F5
          // E0E0E0
          return ['grey-2', 'dark']
      }
    }

    async function checkDetail(targetLevel, targetPpl, targetDate) {
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/kpi/detail/${targetPpl}/${targetLevel}/${targetDate}`
      )
      isShowKpiDetail.value = true
      kpiDetailWho.value = targetPpl
      kpiDetailLevel.value = targetLevel
      kpiDetailDuration.value = targetDate
      kpiDetail.value = _.cloneDeep(res.data)
    }

    async function rePullData(curValue) {
      const res = await axios.get(
        `https://${ServiceDomainLocal}:9487/kpi/query/${curValue}`
      )
      Object.assign(chartData, res.data[0])
      Object.assign(chartData2, res.data[1])
      Object.assign(chartData3, res.data[2])
      Object.assign(chartData4, res.data[3])
      Object.assign(chartData5, res.data[4])
      Object.assign(chartData6, res.data[5])
      Object.assign(chartData7, res.data[6])
      Object.assign(totalData, res.data[8])
      summaryTable.value = _.cloneDeep(res.data[7])
      chartData.datasets = sortChartDataSet.value
      chartData2.datasets = sortChartDataSet2.value
      chartData3.datasets = sortChartDataSet3.value
      chartData4.datasets = sortChartDataSet4.value
      chartData5.datasets = sortChartDataSet5.value
      chartData6.datasets = sortChartDataSet6.value
      chartData7.datasets = sortChartDataSet7.value
    }

    onMounted(async () => {
      try {
        const res = await axios.get(
          `https://${ServiceDomainLocal}:9487/kpi/query/${whichMonth.value}`
        )
        summaryTable.value = _.cloneDeep(res.data[7])
        Object.assign(chartData, res.data[0])
        Object.assign(chartData2, res.data[1])
        Object.assign(chartData3, res.data[2])
        Object.assign(chartData4, res.data[3])
        Object.assign(chartData5, res.data[4])
        Object.assign(chartData6, res.data[5])
        Object.assign(chartData7, res.data[6])
        Object.assign(totalData, res.data[8])
        chartData.datasets = sortChartDataSet.value
        chartData2.datasets = sortChartDataSet2.value
        chartData3.datasets = sortChartDataSet3.value
        chartData4.datasets = sortChartDataSet4.value
        chartData5.datasets = sortChartDataSet5.value
        chartData6.datasets = sortChartDataSet6.value
        chartData7.datasets = sortChartDataSet7.value
        loaded.value = true
      } catch (e) {
        console.log(e)
      }
    })

    watch(
      () => whichMonth.value,
      (curValue, oldValue) => {
        loaded.value = false
        Object.assign(chartData, initialState)
        Object.assign(chartData2, initialState)
        Object.assign(chartData3, initialState)
        Object.assign(chartData4, initialState)
        Object.assign(chartData5, initialState)
        Object.assign(chartData6, initialState)
        Object.assign(chartData7, initialState)
        Object.assign(totalData, initialStateTotal)
        summaryTable.value = []
        rePullData(curValue)
        loaded.value = true
      }
    )

    return {
      loaded,
      chartData,
      chartOptions,
      displayTable,
      sortChartDataSet,
      whichMonth,
      monthOptions,
      chartData2,
      chartData3,
      chartData4,
      chartData5,
      chartData6,
      chartData7,
      chartOptions2,
      chartOptions3,
      chartOptions4,
      chartOptions5,
      chartOptions6,
      chartOptions7,
      summaryTable,
      columns,
      pagination: ref({
        sortBy: 'score',
        descending: true,
        rowsPerPage: 20
      }),
      pplColor,
      checkDetail,
      isShowKpiDetail,
      kpiDetail,
      kpiDetailWho,
      kpiDetailLevel,
      kpiDetailDuration,
      totalData
    }
  }
}
</script>
