const app = getApp()

Page({
  data: {
    member: {}
  },

  onShow() {
    this.loadMemberInfo()
  },

  async loadMemberInfo() {
    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/members/me`,
        method: 'GET',
        data: { openid: app.globalData.openid }
      })

      if (res.data) {
        this.setData({
          member: {
            ...res.data,
            skill_level_text: this.getSkillLevelText(res.data.skill_level),
            membership_period: this.formatMembershipPeriod(res.data)
          }
        })
      }
    } catch (err) {
      console.error('Failed to load member info:', err)
    }
  },

  getSkillLevelText(level) {
    const map = {
      beginner: '初学者',
      intermediate: '进阶',
      advanced: '高级'
    }
    return map[level] || '初学者'
  },

  formatMembershipPeriod(member) {
    if (!member.membership_start || !member.membership_end) return '未知'
    const start = new Date(member.membership_start)
    const end = new Date(member.membership_end)
    const startText = `${start.getMonth() + 1}月${start.getDate()}日`
    const endText = `${end.getMonth() + 1}月${end.getDate()}日`
    return `${startText} - ${endText}`
  },

  onEditProfile() {
    wx.showToast({ title: '编辑功能开发中' })
  },

  onMenuTap(e) {
    const type = e.currentTarget.dataset.type
    switch (type) {
      case 'teaching-style':
        this.showTeachingStylePicker()
        break
      case 'notification':
        wx.showToast({ title: '通知设置开发中' })
        break
      case 'about':
        wx.showToast({ title: '关于我们' })
        break
      case 'help':
        wx.showToast({ title: '帮助反馈开发中' })
        break
    }
  },

  showTeachingStylePicker() {
    wx.showActionSheet({
      itemList: ['耐心型', '专业型', '严格型', '不限'],
      success: (res) => {
        const styles = ['patient', 'professional', 'strict', 'any']
        this.updatePreference('teaching_style_preference', styles[res.tapIndex])
      }
    })
  },

  async updatePreference(key, value) {
    try {
      await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/members/preferences`,
        method: 'PUT',
        data: {
          openid: app.globalData.openid,
          [key]: value
        }
      })
      this.loadMemberInfo()
      wx.showToast({ title: '已更新' })
    } catch (err) {
      wx.showToast({ title: '更新失败', icon: 'error' })
    }
  },

  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync()
          wx.reLaunch({ url: '/pages/index/index' })
        }
      }
    })
  }
})