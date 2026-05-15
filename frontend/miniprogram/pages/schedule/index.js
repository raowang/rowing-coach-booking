const app = getApp()

Page({
  data: {
    currentStatus: 'upcoming',
    bookings: []
  },

  onShow() {
    this.loadBookings()
  },

  onPullDownRefresh() {
    this.loadBookings()
    wx.stopPullDownRefresh()
  },

  async loadBookings() {
    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/bookings`,
        method: 'GET',
        data: {
          openid: app.globalData.openid,
          status: this.getStatusParam()
        }
      })

      if (res.data.items) {
        this.setData({ bookings: this.processBookings(res.data.items) })
      }
    } catch (err) {
      console.error('Failed to load bookings:', err)
    }
  },

  getStatusParam() {
    switch (this.data.currentStatus) {
      case 'upcoming': return 'confirmed,in_progress'
      case 'pending': return 'pending'
      case 'history': return 'completed,cancelled,rejected'
      default: return undefined
    }
  },

  processBookings(bookings) {
    return bookings.map(b => ({
      ...b,
      scheduled_time_text: this.formatDateTime(b.scheduled_time),
      status_text: this.getStatusText(b.status),
      coach_photo: b.coach?.photo_url || '/assets/icons/default-coach.png'
    }))
  },

  formatDateTime(dt) {
    const d = new Date(dt)
    const date = `${d.getMonth() + 1}月${d.getDate()}日`
    const time = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
    return `${date} ${time}`
  },

  getStatusText(status) {
    const map = {
      pending: '待确认',
      confirmed: '已确认',
      in_progress: '进行中',
      completed: '已完成',
      cancelled: '已取消',
      rejected: '已拒绝'
    }
    return map[status] || status
  },

  onStatusChange(e) {
    const status = e.currentTarget.dataset.status
    this.setData({ currentStatus: status })
    this.loadBookings()
  },

  onCancelBooking(e) {
    const bookingId = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认取消',
      content: '确定要取消这个预约吗？',
      success: async (res) => {
        if (res.confirm) {
          await this.cancelBooking(bookingId)
        }
      }
    })
  },

  async cancelBooking(bookingId) {
    try {
      await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/bookings/${bookingId}/cancel`,
        method: 'POST',
        data: { openid: app.globalData.openid }
      })
      wx.showToast({ title: '已取消' })
      this.loadBookings()
    } catch (err) {
      wx.showToast({ title: '取消失败', icon: 'error' })
    }
  },

  onContactCoach(e) {
    const phone = e.currentTarget.dataset.phone
    wx.makePhoneCall({ phoneNumber: phone })
  },

  onViewFeedback(e) {
    const bookingId = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/feedback/index?booking_id=${bookingId}` })
  },

  onRebook(e) {
    const coachId = e.currentTarget.dataset.coachId
    wx.navigateTo({ url: `/pages/booking/index?coach_id=${coachId}` })
  },

  onBookNow() {
    wx.switchTab({ url: '/pages/coach-list/index' })
  }
})