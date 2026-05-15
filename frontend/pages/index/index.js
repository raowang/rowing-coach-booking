Page({
  data: {
    greeting: '',
    quickActions: [],
    upcomingBookings: [],
    recommendedCoaches: [],
    showChat: false,
    isLoading: false
  },

  onLoad() {
    this.loadGreeting();
    this.loadQuickActions();
    this.loadUpcomingBookings();
    this.loadRecommendedCoaches();
  },

  onShow() {
    if (this.data.showChat) {
      return;
    }
    this.refreshData();
  },

  loadGreeting() {
    const app = getApp();
    const greeting = app.generateWelcomeMessage();
    this.setData({ greeting });
  },

  loadQuickActions() {
    const actions = [
      {
        id: 'booking',
        icon: '📅',
        title: '预约训练',
        desc: '快速预约教练',
        path: '/pages/booking/booking'
      },
      {
        id: 'coaches',
        icon: '🏃',
        title: '查看教练',
        desc: '了解教练团队',
        path: '/pages/coach-list/coach-list'
      },
      {
        id: 'schedule',
        icon: '📋',
        title: '我的日程',
        desc: '查看预约记录',
        path: '/pages/schedule/schedule'
      },
      {
        id: 'feedback',
        icon: '💬',
        title: '训练反馈',
        desc: '查看教练点评',
        path: '/pages/feedback/feedback'
      }
    ];
    this.setData({ quickActions: actions });
  },

  loadUpcomingBookings() {
    const app = getApp();
    app.getBookingSchedule('confirmed').then(bookings => {
      const upcoming = bookings.slice(0, 2);
      this.setData({ upcomingBookings: upcoming });
    }).catch(err => {
      console.error('Failed to load upcoming bookings', err);
    });
  },

  loadRecommendedCoaches() {
    const app = getApp();
    app.getRecommendedCoaches().then(coaches => {
      const recommended = coaches.slice(0, 3);
      this.setData({ recommendedCoaches: recommended });
    }).catch(err => {
      console.error('Failed to load recommended coaches', err);
    });
  },

  refreshData() {
    this.loadGreeting();
    this.loadUpcomingBookings();
    this.loadRecommendedCoaches();
  },

  onQuickActionTap(e) {
    const { path } = e.currentTarget.dataset;
    if (path) {
      wx.navigateTo({ url: path });
    }
  },

  onChatTap() {
    this.setData({ showChat: true });
  },

  onCloseChat() {
    this.setData({ showChat: false });
    this.refreshData();
  },

  onCoachTap(e) {
    const { coachId } = e.currentTarget.dataset;
    if (coachId) {
      wx.navigateTo({
        url: `/pages/booking/booking?coachId=${coachId}`
      });
    }
  },

  onBookingTap(e) {
    const { bookingId } = e.currentTarget.dataset;
    if (bookingId) {
      wx.navigateTo({
        url: `/pages/schedule/schedule?bookingId=${bookingId}`
      });
    }
  },

  onVoiceInput() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      success: (res) => {
        console.log('Voice file selected', res);
      },
      fail: (err) => {
        console.error('Voice input failed', err);
        wx.showToast({
          title: '语音功能开发中',
          icon: 'none'
        });
      }
    });
  },

  onPullDownRefresh() {
    this.refreshData();
    wx.stopPullDownRefresh();
  }
});