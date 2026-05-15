const app = getApp()

Page({
  data: {
    messages: [],
    inputText: '',
    scrollToView: '',
    userAvatar: '/assets/icons/default-avatar.png',
    showQuickActions: true,
    isLoading: false,
    voiceRecording: false
  },

  onLoad() {
    this.loadWelcomeMessage()
    this.loadMessageHistory()
  },

  onShow() {
    this.updateScroll()
  },

  async loadWelcomeMessage() {
    const openid = app.globalData.openid
    if (!openid) return

    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/ai/welcome`,
        method: 'POST',
        data: { openid }
      })

      if (res.data.welcome_message) {
        const welcomeMsg = {
          id: 'welcome-' + Date.now(),
          role: 'assistant',
          content: res.data.welcome_message,
          time: this.formatTime(new Date())
        }
        this.setData({
          messages: [welcomeMsg],
          showQuickActions: true
        })
      }
    } catch (err) {
      console.error('Failed to load welcome message:', err)
      this.setData({
        messages: [{
          id: 'welcome-default',
          role: 'assistant',
          content: '您好！我是您的赛艇AI助手。有什么可以帮助您的吗？',
          time: this.formatTime(new Date())
        }]
      })
    }
  },

  loadMessageHistory() {
    const context = wx.getStorageSync('ai_context') || {}
    if (context.messages && context.messages.length > 0) {
      this.setData({ messages: context.messages })
    }
  },

  saveMessageHistory() {
    const context = wx.getStorageSync('ai_context') || {}
    context.messages = this.data.messages
    wx.setStorageSync('ai_context', context)
  },

  onInputChange(e) {
    this.setData({ inputText: e.detail.value })
  },

  async onSendMessage() {
    const text = this.data.inputText.trim()
    if (!text || this.data.isLoading) return

    const userMsg = {
      id: 'user-' + Date.now(),
      role: 'user',
      content: text,
      time: this.formatTime(new Date())
    }

    this.setData({
      messages: [...this.data.messages, userMsg],
      inputText: '',
      showQuickActions: false,
      isLoading: true
    })

    this.saveMessageHistory()
    this.scrollToBottom()

    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/ai/chat`,
        method: 'POST',
        data: {
          openid: app.globalData.openid,
          message: text,
          context: this.data.messages.slice(-10)
        }
      })

      const aiMsg = {
        id: 'ai-' + Date.now(),
        role: 'assistant',
        content: res.data.response,
        time: this.formatTime(new Date())
      }

      this.setData({
        messages: [...this.data.messages, aiMsg],
        isLoading: false,
        showQuickActions: true
      })
    } catch (err) {
      console.error('AI chat error:', err)
      this.setData({ isLoading: false })
      wx.showToast({ title: 'AI响应失败', icon: 'error' })
    }

    this.saveMessageHistory()
    this.scrollToBottom()
  },

  onVoiceInput() {
    if (this.data.voiceRecording) {
      this.stopVoiceRecording()
      return
    }

    this.startVoiceRecording()
  },

  startVoiceRecording() {
    wx.startRecord({
      success: () => {
        this.setData({ voiceRecording: true })
      },
      fail: (err) => {
        wx.showToast({ title: '语音识别失败', icon: 'error' })
      }
    })

    setTimeout(() => {
      if (this.data.voiceRecording) {
        this.stopVoiceRecording()
      }
    }, 60000)
  },

  stopVoiceRecording() {
    wx.stopRecord()
    this.setData({ voiceRecording: false })
  },

  onQuickAction(e) {
    const action = e.currentTarget.dataset.action
    switch (action) {
      case 'book':
        wx.navigateTo({ url: '/pages/booking/index' })
        break
      case 'coach':
        wx.switchTab({ url: '/pages/coach-list/index' })
        break
      case 'history':
        wx.navigateTo({ url: '/pages/feedback/index' })
        break
    }
  },

  scrollToBottom() {
    this.setData({ scrollToView: 'scroll-bottom' })
  },

  formatTime(date) {
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${hours}:${minutes}`
  }
})