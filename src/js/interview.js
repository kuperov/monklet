'use strict'

import DOMPurify from 'dompurify'
import { marked } from 'marked'

function format_local_time(isoString) {
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
  constructor(el, iv_code, init_msgs, init_status, static_url) {
    this.static_url = static_url
    this.interviewCode = iv_code
    this.initial_status = init_status

    // reconnection/backoff parameters
    this.originalReconnectDelayMS = 1000
    this.reconnectDelayMS = this.originalReconnectDelayMS  // grows exponentially
    this.maxReconnectDelayMS = 30 * 1000
    this.socketTimeoutMS = 5 * 1000
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 7
    this.chatSocketTimeout = null

    this.chatHistoryBody = el.querySelector('.chat-history-body')
    this.formSendMessage = el.querySelector('.form-send-message')
    this.messageInput = el.querySelector('.message-input')
    this.messageList = el.querySelector('.chat-history')
    this.sendButton = el.querySelector('.send-msg-btn')
    this.historyFooter = el.querySelector('.chat-history-footer')
    this.statusElement = el.querySelector('.status-banner')

    // clear messages
    while (this.messageList.firstChild) {
      this.messageList.removeChild(this.messageList.firstChild);
    }

    // populate initial messages
    init_msgs.forEach(msg => {
      if (msg.sender != 'system') {
        this.add_message(msg);
      }
    })

    this.ps = new PerfectScrollbar(this.chatHistoryBody, {
      wheelPropagation: false,
      suppressScrollX: true
    })

    if (init_status != 'complete') {
      this.connect_web_socket()
    } else {
      this.set_status('complete')
    }
  }

  show_banner(banner_text) {
    this.statusElement.textContent = banner_text
    this.statusElement.style.display = 'block'
    this.formSendMessage.style.visibility = 'hidden'
  }

  show_input() {
    this.statusElement.style.display = 'none'
    this.formSendMessage.style.visibility = 'visible'
    this.messageInput.focus()
  }

  bind_send_events() {
    this.messageInput.addEventListener('keyup', this._keyUpHandler.bind(this))
    this.formSendMessage.addEventListener('submit', this._submitFormHandler.bind(this))
  }

  unbind_send_events() {
    this.messageInput.removeEventListener('keyup', this._keyUpHandler.bind(this))
    this.formSendMessage.removeEventListener('submit', this._submitFormHandler.bind(this))
  }

  set_status(status) {
    if (status == 'active') {
      this.reconnectAttempts = 0
      this.reconnectDelayMS = this.originalReconnectDelayMS
      this.show_input()
      this.bind_send_events()
      this.scroll_to_bottom()
    } else if (status == 'complete') {
      this.unbind_send_events()
      this.show_banner('Interview complete. Thank you.')
    } else if (status == 'connecting') {
      this.unbind_send_events()
      if (this.reconnectAttempts == 0) {
        this.show_banner('Connecting to server.')
      } else {
        this.show_banner(`Connecting to server (attempt #${this.reconnectAttempts+1}). Refresh the page if necessary.`)
      }
    } else if (status == 'maxretries') {
      this.unbind_send_events()
      this.show_banner('Unable to reconnect. Try refreshing the page.')
    } else {
      this.unbind_send_events()
      this.show_banner(`ERROR: invalid status "${status}".`)
    }
    this.status = status
  }

  add_user_message(msg, time, uuid, received) {
    const local_time = format_local_time(time);
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
    const message_html = DOMPurify.sanitize(marked.parse(msg))
    li.innerHTML = `<div class="d-flex overflow-hidden">
      <div class="chat-message-wrapper flex-grow-1">
        <div class="chat-message-text">
          ${message_html}
        </div>
        <div class="text-end text-muted mt-1">
          <i class='${checkmark} ri-14px ${checkmark_class} me-1'></i>
        </div>
      </div>
      <div class="user-avatar flex-shrink-0 ms-4">
        <div class="avatar avatar-sm">
          <img src="${this.static_url}img/avatars/generic.svg" alt="Avatar" class="rounded-circle">
        </div>
      </div>
    </div>`
    if (mode == 'create') {
      this.messageList.appendChild(li);
    }
  }

  add_remote_message(msg, time, uuid) {
    const local_time = format_local_time(time);
    let li = document.createElement('li');
    li.className = 'chat-message';
    li.setAttribute("id", uuid);
    const message_html = DOMPurify.sanitize(marked.parse(msg))
    li.innerHTML = `<div class="d-flex overflow-hidden">
        <div class="user-avatar flex-shrink-0 me-4">
          <div class="avatar avatar-sm">
            <img src="${this.static_url}img/avatars/bot.svg" alt="Avatar" class="rounded-circle">
          </div>
        </div>
        <div class="chat-message-wrapper flex-grow-1">
          <div class="chat-message-text mb-3">
            ${message_html}
          </div>
        </div>
      </div>`
    this.messageList.appendChild(li);
  }

  add_message(msg) {
    if (msg.sender == 'user') {
      this.add_user_message(msg.message, new Date(msg.sent_at), msg.uuid, true);
    } else {
      this.add_remote_message(msg.message, new Date(msg.sent_at), msg.uuid);
    }
  }

  scroll_to_bottom() {
    this.ps.update();
    const scroll_pos = this.messageList.scrollHeight - 0.9 * this.chatHistoryBody.clientHeight;
    this.chatHistoryBody.scrollTo(100, scroll_pos);
  }

  connect_web_socket() {
    this.set_status('connecting')
    //console.log('connecting to ws with backoff algo')
    const protocol = (window.location.protocol == 'https:') ? 'wss:' : 'ws:';
    const socket_addr = protocol + '//' + window.location.host + '/ws/interviews/' + this.interviewCode + '/';
    //console.log(socket_addr)
    this.chatSocket = new WebSocket(socket_addr);
    this.chatSocket.onmessage = this._socket_message_handler.bind(this)
    this.chatSocket.onclose = this._socket_close_handler.bind(this)
    this.chatSocket.onerror = this._socket_error_handler.bind(this)
    const interview = this
    this.chatSocketTimeout = setTimeout(() => {
      //console.log('WebSocket time out event');
      if (interview.chatSocket.readyState !== WebSocket.OPEN) {
        //console.error('WebSocket connection timed out');
        interview.disconnect_web_socket()
        interview.maybe_queue_reconnect_with_backoff()
      }
    }, this.socketTimeoutMS)
  }

  disconnect_web_socket() {
    //console.log('disconnect ws and any reconnect events')
    if (this.chatSocket == null)
      return
    this.chatSocket.onmessage = null
    this.chatSocket.onclose = null
    this.chatSocket.onerror = null
    this.chatSocket.close()
    this.chatSocket = null
  }

  maybe_queue_reconnect_with_backoff() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      this.reconnect_with_backoff()
    } else {
      console.error('Max reconnect attempts reached')
      this.set_status('maxretries')
    }
  }

  reconnect_with_backoff() {
    const interview = this
    //console.log(`Queueing reconnect attempt #${interview.reconnectAttempts}...`)
    setTimeout(() => {
        console.log(`Reconnect attempt #${interview.reconnectAttempts}...`);
        interview.reconnectDelayMS = Math.min(interview.reconnectDelayMS * 2, interview.maxReconnectDelayMS); // Double the delay
        interview.connect_web_socket()
    }, interview.reconnectDelayMS)
  }

  /* event handlers */

  _socket_message_handler(e) {
    //console.log('_socket_message_handler()')
    //console.log(this)
    const data = JSON.parse(e.data);
    if (data.sender == 'system') {
      if (data.message == 'Interview complete') {
        this.set_status("complete")
      } else if (data.message == 'connected') {
        this.set_status('active')
      }
    } else {
      this.add_message(data);
      this.scroll_to_bottom();
    }
  }

  _socket_close_handler(e) {
    // does not fire when chat is complete because handler should be removed first
    //console.error('Chat socket closed unexpectedly');
    //console.log(this)
    if (this.status == 'complete') {
      //console.log('_socketCloseHandler() should not fire when chat complete')
      return
    }
    this.set_status('connecting')
    this.disconnect_web_socket()
    this.maybe_queue_reconnect_with_backoff()
  }

  _socket_error_handler(error) {
    //console.error('WebSocket error', error)
    //console.log(this)
    this.chatSocket?.close()
    // Reconnect with exponential backoff
    this.maybe_queue_reconnect_with_backoff()
  }

  _submitFormHandler(e) {
    e.preventDefault();
    if (this.messageInput.value) {
      const message = this.messageInput.value;
      const uuid = crypto.randomUUID();
      this.add_user_message(message, new Date(), uuid, false);
      this.chatSocket.send(JSON.stringify({'message': message, 'sender': 'user', 'uuid': uuid}));
      this.messageInput.value = '';
      this.scroll_to_bottom();
    }
  }

  _keyUpHandler(e) {
    /* enter sends message, but shift+enter does newline without send */
    if ((e.keyCode === 13) && !e.shiftKey) {
      this.sendButton.click(e);
    }
  }

};

export { Interview }
