const app = getApp()

Page({
  data: {
    coach: null,
    coachId: null,
    aiRecommendReason: '',
    availableDates: [],
    availableTimes: [],
    selectedDate: '',
    selectedTime: '',
    canConfirm: false
  },

  onLoad(options) {
    if (options.coach_id) {
      this.setData({ coachId: options.coach_id })
      if (options.reason) {
        this.setData({ aiRecommendReason: decodeURIComponent(options.reason) })
      }
      this.loadCoach(options.coach_id)
    }
    this.generateAvailableDates()
  },

  async loadCoach(coachId) {
    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/coaches/${coachId}`,
        method: 'GET'
      })
      if (res.data) {
        this.setData({
          coach: res.data,
          coachId: res.data.id
        })
        this.loadSchedule()
      }
    } catch (err) {
      console.error('Failed to load coach:', err)
    }
  },

  generateAvailableDates() {
    const dates = []
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    const now = new Date()

    for (let i = 0; i < 14; i++) {
      const date = new Date(now)
      date.setDate(now.getDate() + i)
      dates.push({
        date: date.toISOString().split('T')[0],
        weekday: '周' + weekdays[date.getDay()],
        day: date.getDate(),
        month: (date.getMonth() + 1) + '月'
      })
    }
    this.setData({ availableDates: dates })
  },

  async loadSchedule() {
    if (!this.data.selectedDate) return

    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/schedules/available`,
        method: 'GET',
        data: {
          coach_id: this.data.coachId,
          date: this.data.selectedDate
        }
      })

      if (res.data.times) {
        this.setData({ availableTimes: res.data.times })
      }
    } catch (err) {
      console.error('Failed to load schedule:', err)
    }
  },

  onDateSelect(e) {
    const date = e.currentTarget.dataset.date
    this.setData({
      selectedDate: date,
      selectedTime: '',
      canConfirm: false
    })
    this.loadSchedule()
  },

  onTimeSelect(e) {
    const { time, available } = e.currentTarget.dataset
    if (!available) return

    this.setData({
      selectedTime: time,
      canConfirm: true
    })
  },

  async onConfirmBooking() {
    if (!this.data.canConfirm) return

    wx.showLoading({ title: '提交预约...' })

    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/bookings`,
        method: 'POST',
        data: {
          openid: app.globalData.openid,
          coach_id: this.data.coachId,
          scheduled_time: `${this.data.selectedDate} ${this.data.selectedTime}`,
          source: 'wechat_mini_program'
        }
      })

      wx.hideLoading()

      if (res.data.booking_id) {
        wx.showModal({
          title: '预约成功',
          content: '教练确认后您将收到微信通知',
          showCancel: false,
          success: () => {
            wx.switchTab({ url: '/pages/schedule/index' })
          }
        })
      } else if (res.data.error) {
        wx.showToast({ title: res.data.error, icon: 'error' })
      }
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '预约失败', icon: 'error' })
    }
  },

  onChangeCoach() {
    wx.switchTab({ url: '/pages/coach-list/index' })
  }
})