Page({
  data: {
    bookingId: null,
    feedback: null,
    history: [],
    isLoading: false,
    selectedTab: 'detail',
    tabs: [
      { id: 'detail', name: '本次反馈' },
      { id: 'history', name: '历史记录' }
    ],
    aiSuggestions: [],
    showBookingModal: false,
    recommendedSlots: []
  },

  onLoad(options) {
    if (options.bookingId) {
      this.setData({ bookingId: options.bookingId });
      this.loadFeedback(options.bookingId);
    }
    this.loadHistory();
  },

  onShow() {
    if (this.data.bookingId) {
      this.loadFeedback(this.data.bookingId);
    }
  },

  loadFeedback(bookingId) {
    this.setData({ isLoading: true });

    const app = getApp();
    app.getTrainingFeedback(bookingId).then(feedback => {
      this.setData({
        feedback: feedback,
        aiSuggestions: feedback.aiSuggestions || [],
        isLoading: false
      });
    }).catch(err => {
      console.error('Failed to load feedback', err);
      this.setData({ isLoading: false });
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    });
  },

  loadHistory() {
    const app = getApp();
    app.getTrainingHistory({ limit: 20 }).then(history => {
      const historyWithFeedback = history.filter(item => item.feedback || item.rating);
      this.setData({ history: historyWithFeedback });
    }).catch(err => {
      console.error('Failed to load history', err);
    });
  },

  onTabChange(e) {
    const { tabId } = e.currentTarget.dataset;
    this.setData({ selectedTab: tabId });
  },

  onHistoryItemTap(e) {
    const { bookingId } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/feedback/feedback?bookingId=${bookingId}`
    });
  },

  onViewSuggestions() {
    const suggestions = this.data.aiSuggestions;
    if (suggestions.length > 0) {
      wx.showModal({
        title: 'AI改善建议',
        content: suggestions.join('\n\n'),
        showCancel: false,
        confirmText: '知道了'
      });
    }
  },

  onBookAgain() {
    const feedback = this.data.feedback;
    if (!feedback) return;

    const app = getApp();
    app.getRecommendedCoaches().then(coaches => {
      const recommended = coaches.filter(c => c.id === feedback.coachId);
      const coach = recommended.length > 0 ? recommended[0] : coaches[0];

      if (coach) {
        wx.navigateTo({
          url: `/pages/booking/booking?coachId=${coach.id}&suggestedDate=${this.getSuggestedDate()}`,
          fail: () => {
            wx.switchTab({
              url: '/pages/coach-list/coach-list'
            });
          }
        });
      }
    }).catch(() => {
      wx.switchTab({
        url: '/pages/coach-list/coach-list'
      });
    });
  },

  getSuggestedDate() {
    const now = new Date();
    const suggestedDate = new Date(now);
    suggestedDate.setDate(now.getDate() + 3);

    const year = suggestedDate.getFullYear();
    const month = String(suggestedDate.getMonth() + 1).padStart(2, '0');
    const day = String(suggestedDate.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  },

  onShareAppMessage() {
    return {
      title: '我的训练反馈',
      path: '/pages/feedback/feedback'
    };
  },

  onPullDownRefresh() {
    if (this.data.bookingId) {
      this.loadFeedback(this.data.bookingId);
    }
    this.loadHistory();
    wx.stopPullDownRefresh();
  }
});