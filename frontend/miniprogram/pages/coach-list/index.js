const app = getApp()

Page({
  data: {
    coaches: [],
    searchKey: '',
    currentFilter: 'all',
    loading: false,
    page: 1,
    pageSize: 10,
    noMore: false,
    showRecommendation: false,
    recommendation: null
  },

  onLoad() {
    this.loadCoaches()
    this.loadAIRecommendation()
  },

  async loadCoaches() {
    if (this.data.loading || this.data.noMore) return

    this.setData({ loading: true })

    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/coaches`,
        method: 'GET',
        data: {
          page: this.data.page,
          page_size: this.data.pageSize,
          search: this.data.searchKey,
          teaching_style: this.data.currentFilter === 'all' ? undefined : this.data.currentFilter
        }
      })

      if (res.data && res.data.items) {
        this.setData({
          coaches: this.data.page === 1 ? res.data.items : [...this.data.coaches, ...res.data.items],
          loading: false,
          noMore: res.data.items.length < this.data.pageSize
        })
      } else {
        this.setData({ loading: false })
      }
    } catch (err) {
      console.log('Coaches not available (backend offline)')
      this.setData({ loading: false, noMore: true })
    }
  },

  async loadAIRecommendation() {
    try {
      const res = await wx.request({
        url: `${app.globalData.serverUrl}/api/v1/ai/recommend-coach`,
        method: 'POST',
        data: { openid: app.globalData.openid }
      })

      if (res.data && res.data.recommendation) {
        this.setData({
          showRecommendation: true,
          recommendation: res.data.recommendation
        })
      }
    } catch (err) {
      console.log('AI recommendation not available (backend offline)')
    }
  },

  onSearch(e) {
    this.setData({
      searchKey: e.detail.value,
      page: 1,
      noMore: false
    })
    this.loadCoaches()
  },

  onFilterChange(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({
      currentFilter: filter,
      page: 1,
      noMore: false
    })
    this.loadCoaches()
  },

  onLoadMore() {
    if (!this.data.noMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 })
      this.loadCoaches()
    }
  },

  onCoachTap(e) {
    const coachId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/booking/index?coach_id=${coachId}`
    })
  },

  onRecommendationTap() {
    if (this.data.recommendation) {
      wx.navigateTo({
        url: `/pages/booking/index?coach_id=${this.data.recommendation.coach_id}&reason=${encodeURIComponent(this.data.recommendation.reason)}`
      })
    }
  }
})