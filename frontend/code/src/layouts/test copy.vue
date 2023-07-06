<!-- @format -->

<template>
  <h2>VueJS + Google Calendar Example</h2>
  <button id="authorizeButtonId" @click="gLoginBtn">Authorize</button>
  <button id="signoutButtonId">Sign Out</button>
  <pre id="content" style="white-space: pre-wrap"></pre>
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
      window.gapi.load('client', gStart)
    }

    function gStart() {
      // 2. Initialize the JavaScript client library.
      window.gapi.client
        .init({
          apiKey: 'AIzaSyA_EH-gpXx9NTFHGBbcMgYOF27n2SP8hak',
          // Your API key will be automatically added to the Discovery Document URLs.
          discoveryDocs: [
            'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'
          ],
          // clientId and scope are optional if auth is not required.
          clientId:
            '720665971425-fspvrljso647ridnig69ol3j368glqsc.apps.googleusercontent.com',
          scope: 'https://www.googleapis.com/auth/calendar.readonly'
        })
        .then((ele) => {
          // 3. Initialize and make the API request.
          console.log('hit first then ele')
          console.log(ele)
        })
        .then(
          function (response) {
            console.log('hit response')
            console.log(response.result)
          },
          function (reason) {
            console.log('hit reason')
            console.log('Error: ')
            console.log(reason)
          }
        )
    }

    // function handleClientLoad() {
    //   window.gapi.load('client:auth2', initClient)
    // }

    // function initClient() {
    //   window.gapi.client
    //     .init({
    //       apiKey: API_KEY,
    //       clientId: CLIENT_ID,
    //       discoveryDocs: DISCOVERY_DOCS,
    //       scope: SCOPES
    //     })
    //     .then(
    //       function () {
    //         // Listen for sign-in state changes.
    //         window.gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus)

    //         // Handle the initial sign-in state.
    //         updateSigninStatus(window.gapi.auth2.getAuthInstance().isSignedIn.get())
    //         authorizeButton.onclick = handleAuthClick
    //         signoutButton.onclick = handleSignoutClick
    //       },
    //       function (error) {
    //         appendPre(JSON.stringify(error, null, 2))
    //       }
    //     )
    // }

    // function handleAuthClick(event) {
    //   window.gapi.auth2.getAuthInstance().signIn()
    // }

    // function handleSignoutClick(event) {
    //   window.gapi.auth2.getAuthInstance().signOut()
    // }

    // function updateSigninStatus(isSignedIn) {
    //   if (isSignedIn) {
    //     listUpcomingEvents()
    //   } else {
    //     console.log('hit updateSigninStatus')
    //   }
    // }

    // function listUpcomingEvents() {
    //   window.gapi.client.calendar.events
    //     .list({
    //       calendarId: 'primary',
    //       timeMin: new Date().toISOString(),
    //       showDeleted: false,
    //       singleEvents: true,
    //       maxResults: 10,
    //       orderBy: 'startTime'
    //     })
    //     .then(function (response) {
    //       const events = ref(response.result.items)
    //       appendPre('Upcoming events:')

    //       if (events.value.length > 0) {
    //         for (const i = ref(0); i.value < events.value.length; i.value++) {
    //           const event = ref(events[i.value].value)
    //           const when = ref(event.value.start.dateTime)
    //           if (!when.value) {
    //             when.value = event.value.start.date
    //           }
    //           appendPre(event.value.summary + ' (' + when.value + ')')
    //         }
    //       } else {
    //         appendPre('No upcoming events found.')
    //       }
    //     })
    // }

    // function appendPre(message) {
    //   const pre = document.getElementById('content')
    //   const textContent = document.createTextNode(message + '\n')
    //   pre.appendChild(textContent)
    // }

    startSelfTimer()

    return {
      items,
      authorized,
      selfTime,
      startSelfTimer,
      stopSelfTimer,
      gLoginBtn,
      gStart
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
