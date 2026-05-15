const app = getApp()

Page({
  data: {
    feedback: null,
    bookingId: null
  },

  onLoad(options) {
    if (options.booking_id) {
      this.setData({ bookingId: options.booking_id })
      this.loadFeedback(options.booking_id)
    }
  },

  async loadFeedback(bookingId) {
    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/training-records/${bookingId}`,
        method: 'GET',
        data: { openid: app.globalData.openid }
      })

      if (res.data) {
        this.setData({
          feedback: {
            ...res.data,
            training_date: this.formatDate(res.data.training_time)
          }
        })
      }
    } catch (err) {
      console.error('Failed to load feedback:', err)
      wx.showToast({ title: '加载失败', icon: 'error' })
    }
  },

  formatDate(dt) {
    const d = new Date(dt)
    return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
  },

  onBookAgain() {
    const coachId = this.data.feedback?.coach_id
    if (coachId) {
      wx.navigateTo({ url: `/pages/booking/index?coach_id=${coachId}` })
    }
  },

  onShareAppMessage() {
    return {
      title: '我的训练反馈 - 赛艇预约',
      path: `/pages/feedback/index?booking_id=${this.data.bookingId}`
    }
  }
})