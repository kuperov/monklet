'use strict'

function _formatLocalTime(isoString) {
  const utcDate = new Date(isoString);
  let hours = utcDate.getHours();
  let minutes = utcDate.getMinutes();
  let ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0' + minutes : minutes;
  return `${hours}:${minutes} ${ampm}`;
};

class Simulator {
  constructor(el, apiEndpoint, static_url) {
    this.el = el
    this.apiEndpoint = apiEndpoint
    this.staticURL = static_url
    this.interviewList = el.querySelector('.interview-list')
    this.botList = el.querySelector('.interview-list')

    this.chatHistoryBody = el.querySelector('.chat-history-body')
    this.formSendMessage = el.querySelector('.form-send-message')
    this.messageInput = el.querySelector('.message-input')
    this.messageList = el.querySelector('.chat-history')
    this.sendButton = el.querySelector('.send-msg-btn')
    this.historyFooter = el.querySelector('.chat-history-footer')
    this.leftPane = el.querySelector('.simulator-left-pane')
    this.botName = el.querySelector('.bot-name')
    this.botVersion = el.querySelector('.bot-version')

    this.leftPane_ps = new PerfectScrollbar(this.leftPane, {
      wheelPropagation: false,
      suppressScrollX: true
    });

    this.ps = new PerfectScrollbar(this.chatHistoryBody, {
      wheelPropagation: false,
      suppressScrollX: true
    });

    this.interview_code = null
    this._bindEvents()

    this._refreshInterviews().catch(error => {
      alert("Error loading interviews: "+error);
    })
  }

  async _refreshInterviews() {
    const response = await fetch(this.apiEndpoint + 'test_interviews');
    if (!response.ok) {
      throw new Error(`Failed to get interviews (status ${response.status})`);
    }
    const interviews = await response.json();
    while (this.interviewList.firstChild) {
      this.interviewList.removeChild(this.interviewList.firstChild)
    }
    // replace the heading we removed
    const hd_text = `${interviews.length} test ` + (interviews.length == 1 ? 'interview' : 'interviews')
    const heading = document.createElement('li')
    heading.className = "chat-bot-list-item chat-bot-list-item-title mt-0"
    heading.innerHTML = `<h5 class="text-primary mb-0">${hd_text}</h5>`
    this.interviewList.appendChild(heading)
    // one entry per interview
    await interviews.forEach(iv => {
      /* {
        "interview": "ab606492-1bb3-4a98-b297-1d39e922a163",
        "names": "Percival & Bob",
        "bot_name": "Percival",
        "version": 1,
        "last_text": "Lorem ipsum.",
        "updated_at": "13 hours ago",
        "status": "complete"
      }, */
      this._addInterview(iv['interview'], iv['names'], iv['bot_name'], iv['bot_version'], iv['last_text'], iv['updated_at'], iv['status'])
    })
    this.leftPane_ps.update()
  }

  _addInterview(interview_code, names, bot_name, bot_version, last_text, updated_at, status) {
    const li = document.createElement('li')
    const simulator = this
    li.className = 'chat-bot-list-item mb-1'
    li.innerHTML = `
            <a class="d-flex align-items-center">
              <div class="flex-shrink-0 avatar">
                <img src="${this.staticURL}img/avatars/bot.svg" alt="Avatar" class="rounded-circle">
              </div>
              <div class="chat-bot-info flex-grow-1 ms-4">
                <div class="d-flex justify-content-between align-items-center">
                  <h6 class="chat-bot-name text-truncate fw-normal m-0">${names}</h6>
                  <small class="text-muted">${updated_at}</small>
                </div>
                <small class="chat-bot-status text-truncate">${last_text}</small>
              </div>
            </a>`
    li.onclick = () => { simulator.startInterview(interview_code, bot_name, bot_version, status) }
    this.interviewList.appendChild(li)
  }

  async startInterview(interview_code, bot_name, bot_version, status) {
    this.interviewCode = interview_code
    // stop current interview
    this._clearMessages()
    await this._loadMessages(interview_code)
    // set up header
    if (bot_name) {
      this.botName.textContent = bot_name
    }
    if (bot_version) {
      this.botVersion.textContent = `Version ${bot_version}`
    }
    // load menu items

    // connect interview
    this.messageInput.focus()
    this.connectWebSocket() // connect to chat
    console.log('status = '+status)
    if (status == 'complete') {
      this.disable_chat()
    } else {
      this.enable_chat()
    }
    this.scrollToBottom()
  }

  connectWebSocket() {
    const simulator = this
    const protocol = (window.location.protocol == 'https:') ? 'wss:' : 'ws:';
    const socket_addr = protocol + '//' + window.location.host + '/ws/interviews/' + this.interviewCode + '/';
    this.chatSocket = new WebSocket(socket_addr);

    this.chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.sender == 'system' && data.message == 'Interview complete') {
          simulator.disable_chat()
        } else {
          simulator.add_message(data);
          simulator.scrollToBottom();
        }
    }

    this.chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    }
  }

  async _loadMessages(interview_code) {
    const response = await fetch(`/interviews/${interview_code}/messages`);
    if (!response.ok) {
      throw new Error(`Failed to get interviews (status ${response.status})`);
    }
    const interviews = await response.json();
    await interviews.forEach(msg => { this.add_message(msg) })
  }

  _clearMessages() {
    this.chatHistoryBody.scrollTo(0, 0)
    while (this.messageList.firstChild) {
      this.messageList.removeChild(this.messageList.firstChild)
    }
  }

  init_chat() {
    // clear elements
    while (self.messageList.firstChild) {
      self.messageList.removeChild(myLi.firstChild);
    }
    this.enable_chat()
  }

  enable_chat() {
    // show input elements
    this.historyFooter.style.visibility = 'visible';
    //self.startHook();
  }

  disable_chat() {
    // hide input elements
    this.historyFooter.style.visibility = 'hidden';
    //self.completeHook();
  }

  add_user_message(msg, time, uuid, received) {
    const local_time = _formatLocalTime(time);
    if (uuid) {
      var li = document.getElementById(uuid);
    }
    let mode = li ? 'update' : 'create';
    if (!li) {
      li = document.createElement('li');
      li.setAttribute("id", uuid);
    }
    let checkmark = received ? 'ri-check-double-line' : 'ri-check-line';
    let checkmark_class = received ? 'text-success' : 'text-secondary';
    li.className = "chat-message chat-message-right";
    li.innerHTML = `<div class="d-flex overflow-hidden">
      <div class="chat-message-wrapper flex-grow-1">
        <div class="chat-message-text">
        <p class="mb-0">${msg}</p>
        </div>
        <div class="text-end text-muted mt-1">
          <i class='${checkmark} ri-14px ${checkmark_class} me-1'></i>
          <small>${local_time}</small>
        </div>
      </div>
      <div class="user-avatar flex-shrink-0 ms-4">
        <div class="avatar avatar-sm">
          <img src="${this.staticURL}img/avatars/generic.svg" alt="Avatar" class="rounded-circle">
        </div>
      </div>
    </div>`;
    if (mode == 'create') {
      this.messageList.appendChild(li);
    }
  }

  add_remote_message(msg, time, uuid) {
    const local_time = _formatLocalTime(time);
    let li = document.createElement('li');
    li.className = 'chat-message';
    li.setAttribute("id", uuid);
    li.innerHTML = `<div class="d-flex overflow-hidden">
        <div class="user-avatar flex-shrink-0 me-4">
          <div class="avatar avatar-sm">
            <img src="${this.staticURL}img/avatars/bot.svg" alt="Avatar" class="rounded-circle">
          </div>
        </div>
        <div class="chat-message-wrapper flex-grow-1">
          <div class="chat-message-text">
            <p class="mb-0">${msg}</p>
          </div>
          <div class="text-muted mt-1">
            <small>${local_time}</small>
          </div>
        </div>
      </div>`;
    this.messageList.appendChild(li);
  }

  add_message(msg) {
    if (msg.sender == 'user') {
      this.add_user_message([msg.message], msg.sent_at, msg.uuid, true);
    } else {
      this.add_remote_message([msg.message], msg.sent_at, msg.uuid);
    }
  }

  scrollToBottom() {
    this.ps.update();
    const scroll_pos = this.messageList.scrollHeight - 0.9 * this.chatHistoryBody.clientHeight;
    this.chatHistoryBody.scrollTo(0, scroll_pos);
  }

  _bindEvents() {
    const interview = this
    this.messageInput.onkeyup = function(e) {
      /* enter sends message */
      if (e.keyCode === 13) {
        interview.sendButton.click(e);
      }
    }

    this.formSendMessage.addEventListener('submit', e => {
      e.preventDefault();
      if (interview.messageInput.value) {
        const message = interview.messageInput.value;
        const uuid = crypto.randomUUID();
        interview.add_user_message([message], new Date(), uuid, false);
        interview.chatSocket.send(JSON.stringify({'message': message, 'sender': 'user', 'uuid': uuid}));
        interview.messageInput.value = '';
        interview.scrollToBottom();
      }
    })
  }
}

export { Simulator }
