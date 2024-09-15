'use strict'

function formatLocalTime(isoString) {
  const utcDate = new Date(isoString);
  let hours = utcDate.getHours();
  let minutes = utcDate.getMinutes();
  let ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0' + minutes : minutes;
  return `${hours}:${minutes} ${ampm}`;
};

class Interview {
  constructor(el, interviewCode, initialMessages, completeHook, startHook, static_url) {
    this._el = el
    this.static_url = static_url
    this.completeHook = completeHook
    this.startHook = startHook
    this.interviewCode = interviewCode

    this.chatHistoryBody = el.querySelector('.chat-history-body')
    this.formSendMessage = el.querySelector('.form-send-message')
    this.messageInput = el.querySelector('.message-input')
    this.messageList = el.querySelector('.chat-history')
    this.sendButton = el.querySelector('.send-msg-btn')
    this.historyFooter = el.querySelector('.chat-history-footer')

    initialMessages.forEach(msg => {
      this.add_message(msg);
    })

    this.ps = new PerfectScrollbar(this.chatHistoryBody, {
      wheelPropagation: false,
      suppressScrollX: true
    });
    this.scrollToBottom();

    this.messageInput.focus()
    this._bindEvents()  // gets ref to socket

    this.connectWebSocket() // connect to chat
  }

  init_chat() {
    // clear elements
    while (this.messageList.firstChild) {
      this.messageList.removeChild(myLi.firstChild);
    }
    // show input elements
    this.historyFooter.style.visibility = 'visible';
    this.startHook();
  }

  disable_chat() {
    // hide input elements
    this.historyFooter.style.visibility = 'hidden';
    this.completeHook();
  }

  add_user_message(msg, time, uuid, received) {
    const local_time = formatLocalTime(time);
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
          <img src="${this.static_url}img/avatars/generic.svg" alt="Avatar" class="rounded-circle">
        </div>
      </div>
    </div>`;
    if (mode == 'create') {
      this.messageList.appendChild(li);
    }
  }

  add_remote_message(msg, time, uuid) {
    const local_time = formatLocalTime(time);
    let li = document.createElement('li');
    li.className = 'chat-message';
    li.setAttribute("id", uuid);
    li.innerHTML = `<div class="d-flex overflow-hidden">
        <div class="user-avatar flex-shrink-0 me-4">
          <div class="avatar avatar-sm">
            <img src="${this.static_url}img/avatars/bot.svg" alt="Avatar" class="rounded-circle">
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
    this.chatHistoryBody.scrollTo(100, scroll_pos);
  }

  connectWebSocket() {
    const interview = this
    const protocol = (window.location.protocol == 'https:') ? 'wss:' : 'ws:';
    const socket_addr = protocol + '//' + window.location.host + '/ws/interviews/' + this.interviewCode + '/';
    this.chatSocket = new WebSocket(socket_addr);

    this.chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.sender == 'system' && data.message == 'Interview complete') {
          interview.disable_chat()
        } else {
          interview.add_message(data);
          interview.scrollToBottom();
        }
    }

    this.chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    }
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
};

export { Interview }
