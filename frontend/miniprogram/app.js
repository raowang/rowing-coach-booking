App({
  globalData: {
    userInfo: null,
    openid: '',
    serverUrl: 'http://localhost:8000',
    wechatAppId: ''
  },

  onLaunch() {
    this.checkLogin()
    this.initAIContext()
  },

  checkLogin() {
    const openid = wx.getStorageSync('openid')
    if (openid) {
      this.globalData.openid = openid
    } else {
      this.doWechatLogin()
    }
  },

  doWechatLogin() {
    wx.login({
      success: (res) => {
        if (res.code) {
          this.requestOpenid(res.code)
        }
      }
    })
  },

  requestOpenid(code) {
    wx.request({
      url: `${this.globalData.serverUrl}/api/v1/auth/wechat`,
      method: 'POST',
      data: { code },
      success: (res) => {
        if (res.data.openid) {
          this.globalData.openid = res.data.openid
          wx.setStorageSync('openid', res.data.openid)
        }
      }
    })
  },

  initAIContext() {
    const context = wx.getStorageSync('ai_context') || {}
    if (!context.sessionId) {
      context.sessionId = this.generateSessionId()
      context.messages = []
      wx.setStorageSync('ai_context', context)
    }
  },

  generateSessionId() {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }
})