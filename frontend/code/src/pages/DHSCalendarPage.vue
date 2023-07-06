<!-- @format -->
<template>
  <q-card class="customChildAutoHeigth">
    <q-item class="bg-blue-grey-1 q-py-none row items-center">
      <span class="col-6">Calendar</span>
      <span class="col-6 text-right q-gutter-xs">
        <q-btn
          size="sm"
          push
          color="white"
          text-color="primary"
          round
          disabled
          icon="add_circle"
          @click="addCalendar"
        />
        <q-btn
          size="sm"
          push
          color="white"
          text-color="primary"
          round
          disabled
          icon="remove_circle"
          @click="delCalendar"
        />
      </span>
    </q-item>
    <FullCalendar class="q-pa-md q-mb-xl" :options="calendarOptions" />
    <q-item class="bg-blue-grey-1 absolute-bottom q-py-none text-caption">
      <q-item-section>
        <q-item-label class="text-right"
          ><b>Google Account</b>: ytops.alerts@gmail.com | <b>Calendar ID</b>:
          iogs6k5epliqpnv3vg220o29co@group.calendar.google.com</q-item-label
        >
      </q-item-section>
    </q-item>
  </q-card>
</template>

<script>
import '@fullcalendar/core/vdom' // solves problem with Vite
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'
import googleCalendarPlugin from '@fullcalendar/google-calendar'
import { defineComponent, onMounted, ref } from 'vue'
import { scroll } from 'quasar'
import { useStore } from 'vuex'
import axios from 'axios'

export default defineComponent({
  name: 'DHSCalendarPage',
  components: {
    FullCalendar // make the <FullCalendar> tag available
  },
  setup() {
    const $store = useStore()
    const mappingList = ref([])
    const targetString = ref('')
    const ServiceDomainLocal = $store.state.fixedConfig.serviceDomain // dynamic change the domain by vuex
    const { getScrollTarget, setVerticalScrollPosition } = scroll // scroll function

    function addCalendar() {
      console.log('hit addCalendar')
      alert('Not yet')
    }
    function delCalendar() {
      console.log('hit delCalendar')
      alert('Not yet')
    }

    onMounted(async () => {
      await axios
        .get(`https://${ServiceDomainLocal}:9487/mtn/query/all`)
        .then((res) => {
          mappingList.value = res.data
        })
        .catch((error) => {
          console.log(error)
        })
    })

    return {
      addCalendar,
      delCalendar,
      calendarOptions: {
        plugins: [dayGridPlugin, interactionPlugin, googleCalendarPlugin, listPlugin],
        contentHeight: 'auto',
        initialView: 'listDay',
        googleCalendarApiKey: 'AIzaSyA_EH-gpXx9NTFHGBbcMgYOF27n2SP8hak',
        events: {
          googleCalendarId: 'iogs6k5epliqpnv3vg220o29co@group.calendar.google.com'
        },
        views: {
          listDay: {
            buttonText: 'Today'
          },
          listWeek: {
            buttonText: 'This week'
          }
        },
        headerToolbar: {
          start: 'title', // will normally be on the left. if RTL, will be on the right
          center: '',
          end: 'listDay,listWeek,prev,next' // will normally be on the right. if RTL, will be on the left
        },
        eventClick: function (arg) {
          arg.jsEvent.preventDefault()
          mappingList.value.forEach(function (item, index, object) {
            if (Object.keys(item)[0] === arg.event._def.publicId) {
              if (Object.values(item)[0].toString().length === 8) {
                // otrs ticket
                targetString.value = `otrs${Object.values(item)[0]}`
              } else {
                // jira ticket
                console.log(Object.values(item))
                targetString.value = `jira${Object.values(item)[0]}`
              }
            }
          })

          if (targetString.value !== '') {
            const ele = document.getElementById(targetString.value)
            const target = getScrollTarget(ele)
            const offset = ele.offsetTop - 55
            const duration = 200
            ele.classList.add('ballon', 'bg-yellow-1')
            setVerticalScrollPosition(target, offset, duration)
            window.setTimeout(() => ele.classList.remove('ballon', 'bg-yellow-1'), 11000)
          } else {
            console.log(arg.event)
          }
        }
      }
    }
  }
})
</script>

<style>
h2[id^='fc-dom'] {
  font-size: 1em !important;
}

div.fc-header-toolbar.fc-toolbar {
  margin-bottom: 0 !important;
}
</style>
