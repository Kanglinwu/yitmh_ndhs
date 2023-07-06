<!-- @format -->

<template>
  <h2>VueJS + Google Calendar Example</h2>
  <button id="authorizeButtonId" @click="gLoginBtn">Authorize</button>
  <pre id="content" style="white-space: pre-wrap"></pre>
  <hr />
  <q-btn label="Create new calendar event" @click="createNewEvent"></q-btn>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
// import axios from 'axios'

export default defineComponent({
  name: 'test',
  setup() {
    const items = ref()
    const authorized = ref(false)
    const scriptContainer = ref()
    const selfTime = ref(null)

    onMounted(() => {
      scriptContainer.value = document.createElement('script')
      scriptContainer.value.setAttribute('src', 'https://apis.google.com/js/api.js')
      document.head.appendChild(scriptContainer.value)
    })

    function startSelfTimer() {
      selfTime.value = setInterval(() => {
        if (window.gapi !== undefined) {
          console.log('loaded finished')
          stopSelfTimer()
        } else {
          console.log('next run')
        }
      }, 3000)
    }

    function stopSelfTimer() {
      console.log('hit stop the setinterval')
      clearInterval(selfTime.value)
    }

    function gLoginBtn() {
      console.log('hit gLoginBtn')
      window.gapi.load('client:auth2', initClient)
    }

    function initClient() {
      // try to connect the google api client by .init with these informations
      window.gapi.client
        .init({
          apiKey: 'AIzaSyA_EH-gpXx9NTFHGBbcMgYOF27n2SP8hak',
          clientId:
            '720665971425-fspvrljso647ridnig69ol3j368glqsc.apps.googleusercontent.com',
          discoveryDocs: [
            'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'
          ],
          scope: 'https://www.googleapis.com/auth/calendar.readonly'
        })
        .then(
          function () {
            // Listen for sign-in state changes.
            window.gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus)

            // Handle the initial sign-in state.
            updateSigninStatus(window.gapi.auth2.getAuthInstance().isSignedIn.get())
          },
          function (error) {
            appendPre(JSON.stringify(error, null, 2))
          }
        )
    }

    function updateSigninStatus(isSignedIn) {
      if (isSignedIn) {
        // if user already login then do the action
        listUpcomingEvents()
      } else {
        // user does not login, so signin now
        window.gapi.auth2.getAuthInstance().signIn()
      }
    }

    // what the action you want
    function listUpcomingEvents() {
      window.gapi.client.calendar.events
        .list({
          calendarId: 'primary',
          timeMin: new Date().toISOString(),
          showDeleted: false,
          singleEvents: true,
          maxResults: 10,
          orderBy: 'startTime'
        })
        .then(function (response) {
          console.log(response.result.items)
          appendPre('Upcoming events:')
        })
    }

    // when get result, append to html body
    function appendPre(message) {
      const pre = document.getElementById('content')
      const textContent = document.createTextNode(message + '\n')
      pre.appendChild(textContent)
    }

    function createNewEvent() {
      const event = {
        summary: 'OPS-Gary do the API test from new handover system',
        description: "A chance to hear more about Google's developer products.",
        start: {
          dateTime: '2021-11-28T09:00:00',
          timeZone: 'Asia/Taipei'
        },
        end: {
          dateTime: '2021-11-28T10:00:00',
          timeZone: 'Asia/Taipei'
        },
        reminders: {
          useDefault: false,
          overrides: [
            { method: 'email', minutes: 10 },
            { method: 'popup', minutes: 10 }
          ]
        }
      }

      window.gapi.client.calendar.events
        .insert({
          calendarId: 'primary',
          resource: event
        })
        .then(function (response) {
          console.log(response)
        })
    }

    // when page load, run this function to make sure google api is already.
    startSelfTimer()

    return {
      items,
      authorized,
      selfTime,
      startSelfTimer,
      stopSelfTimer,
      gLoginBtn,
      createNewEvent
    }
  }
})
</script>

<style>
body {
  font-family: 'Open Sans', sans-serif;
  font-size: 14px;
  font-weight: 300;
  line-height: 1em;
}

.authentification {
  margin: 20px;
  text-align: center;
}

hr {
  border: 1px solid black;
  margin: 30px;
}

pre {
  outline: 1px solid #ccc;
  padding: 5px;
  margin: 5px;
  overflow-x: auto;
}

.string {
  color: green;
}

.number {
  color: purple;
}

.boolean {
  color: blue;
}

.null {
  color: magenta;
}

.key {
  color: black;
}
</style>
