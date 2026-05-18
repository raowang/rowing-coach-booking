// Dummy schedule data
const dummyUpcomingBookings = [
  { id: 'b1', coachName: '张教练', coachAvatar: '/miniprogram/assets/images/coach-1.png', date: '2026-05-20', dateDay: '20', dateMonth: '5', timeSlot: '09:00-11:00', status: 'confirmed', statusText: '已确认', location: '2号航道' },
  { id: 'b2', coachName: '陈教练', coachAvatar: '/miniprogram/assets/images/coach-4.png', date: '2026-05-22', dateDay: '22', dateMonth: '5', timeSlot: '14:00-16:00', status: 'pending', statusText: '待确认', location: '1号航道' },
  { id: 'b3', coachName: '李教练', coachAvatar: '/miniprogram/assets/images/coach-2.png', date: '2026-05-25', dateDay: '25', dateMonth: '5', timeSlot: '10:00-12:00', status: 'confirmed', statusText: '已确认', location: '3号航道' }
];

const dummyCompletedBookings = [
  { id: 'b4', coachName: '张教练', coachAvatar: '/miniprogram/assets/images/coach-1.png', date: '2026-05-15', dateDay: '15', dateMonth: '5', timeSlot: '09:00-11:00', status: 'completed', statusText: '已完成', location: '2号航道', rating: 5 },
  { id: 'b5', coachName: '王教练', coachAvatar: '/miniprogram/assets/images/coach-3.png', date: '2026-05-10', dateDay: '10', dateMonth: '5', timeSlot: '14:00-16:00', status: 'completed', statusText: '已完成', location: '1号航道', rating: 4 },
  { id: 'b6', coachName: '陈教练', coachAvatar: '/miniprogram/assets/images/coach-4.png', date: '2026-05-05', dateDay: '05', dateMonth: '5', timeSlot: '10:00-12:00', status: 'completed', statusText: '已完成', location: '3号航道', rating: 5 }
];

const dummyCancelledBookings = [
  { id: 'b7', coachName: '刘教练', coachAvatar: '/miniprogram/assets/images/coach-5.png', date: '2026-05-08', dateDay: '08', dateMonth: '5', timeSlot: '09:00-11:00', status: 'cancelled', statusText: '已取消', location: '2号航道', cancelReason: '天气原因取消' }
];

Page({
  data: {
    activeTab: 'upcoming',
    tabs: [
      { id: 'upcoming', name: '即将到来' },
      { id: 'completed', name: '已完成' },
      { id: 'cancelled', name: '已取消' }
    ],
    bookings: [],
    upcomingBookings: [],
    completedBookings: [],
    cancelledBookings: [],
    isLoading: false,
    selectedBooking: null,
    showCancelModal: false,
    cancelReason: '',
    isCancelling: false,
    useMockData: true
  },

  onLoad(options) {
    if (options.bookingId) {
      this.loadBookingDetail(options.bookingId);
    }
  },

  onShow() {
    this.loadBookings();
  },

  loadBookings() {
    this.setData({ isLoading: true });

    if (this.data.useMockData) {
      setTimeout(() => {
        this.setData({
          upcomingBookings: dummyUpcomingBookings,
          completedBookings: dummyCompletedBookings,
          cancelledBookings: dummyCancelledBookings,
          bookings: dummyUpcomingBookings,
          isLoading: false
        });
      }, 500);
      return;
    }

    const app = getApp();

    Promise.all([
      app.getBookingSchedule('pending'),
      app.getBookingSchedule('confirmed'),
      app.getBookingSchedule('in_progress'),
      app.getBookingSchedule('completed'),
      app.getBookingSchedule('cancelled')
    ]).then(results => {
      const pending = results[0] || [];
      const confirmed = results[1] || [];
      const inProgress = results[2] || [];
      const completed = results[3] || [];
      const cancelled = results[4] || [];

      const upcoming = [...pending, ...confirmed, ...inProgress].sort((a, b) => {
        return new Date(a.date) - new Date(b.date);
      });

      this.setData({
        upcomingBookings: upcoming,
        completedBookings: completed.sort((a, b) => {
          return new Date(b.date) - new Date(a.date);
        }),
        cancelledBookings: cancelled.sort((a, b) => {
          return new Date(b.date) - new Date(a.date);
        }),
        bookings: upcoming,
        isLoading: false
      });
    }).catch(err => {
      console.error('Failed to load bookings', err);
      this.setData({ isLoading: false });
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    });
  },

  loadBookingDetail(bookingId) {
    const app = getApp();
    app.getBookingSchedule().then(bookings => {
      const booking = bookings.find(b => b.id === bookingId);
      if (booking) {
        this.setData({ selectedBooking: booking });
      }
    }).catch(err => {
      console.error('Failed to load booking detail', err);
    });
  },

  onTabChange(e) {
    const { tabId } = e.currentTarget.dataset;
    this.setData({ activeTab: tabId });

    switch (tabId) {
      case 'upcoming':
        this.setData({ bookings: this.data.upcomingBookings });
        break;
      case 'completed':
        this.setData({ bookings: this.data.completedBookings });
        break;
      case 'cancelled':
        this.setData({ bookings: this.data.cancelledBookings });
        break;
    }
  },

  onBookingTap(e) {
    const { bookingId } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/feedback/feedback?bookingId=${bookingId}`
    });
  },

  onCancelTap(e) {
    const { bookingId } = e.currentTarget.dataset;
    const booking = this.data.upcomingBookings.find(b => b.id === bookingId);

    if (booking) {
      this.setData({
        selectedBooking: booking,
        showCancelModal: true,
        cancelReason: ''
      });
    }
  },

  onCloseCancelModal() {
    this.setData({
      showCancelModal: false,
      selectedBooking: null,
      cancelReason: ''
    });
  },

  onCancelReasonInput(e) {
    this.setData({ cancelReason: e.detail.value });
  },

  onConfirmCancel() {
    if (this.data.isCancelling) return;

    const booking = this.data.selectedBooking;
    if (!booking) return;

    this.setData({ isCancelling: true });

    const app = getApp();
    app.cancelBooking(booking.id, this.data.cancelReason).then(() => {
      wx.showToast({
        title: '取消成功',
        icon: 'success'
      });

      this.setData({
        isCancelling: false,
        showCancelModal: false
      });

      this.loadBookings();
    }).catch(err => {
      console.error('Failed to cancel booking', err);
      this.setData({ isCancelling: false });
      wx.showToast({
        title: '取消失败',
        icon: 'none'
      });
    });
  },

  onReminderTap(e) {
    const { bookingId } = e.currentTarget.dataset;
    const booking = this.data.upcomingBookings.find(b => b.id === bookingId);

    if (booking) {
      wx.showModal({
        title: '设置提醒',
        content: `将在训练前1小时提醒您：${booking.coachName} - ${booking.date}`,
        confirmText: '确定',
        success: (res) => {
          if (res.confirm) {
            wx.showToast({
              title: '提醒已设置',
              icon: 'success'
            });
          }
        }
      });
    }
  },

  onAddToCalendar(e) {
    const { bookingId } = e.currentTarget.dataset;
    const booking = this.data.upcomingBookings.find(b => b.id === bookingId);

    if (booking) {
      const startDate = new Date(`${booking.date}T${booking.timeSlot}:00`);
      const endDate = new Date(startDate.getTime() + 2 * 60 * 60 * 1000);

      wx.addPhoneCalendar({
        title: `赛艇训练 - ${booking.coachName}`,
        startTime: Math.floor(startDate.getTime() / 1000),
        endTime: Math.floor(endDate.getTime() / 1000),
        notes: `预约编号: ${booking.id}`,
        success: () => {
          wx.showToast({
            title: '已添加到日历',
            icon: 'success'
          });
        },
        fail: () => {
          wx.showToast({
            title: '添加失败',
            icon: 'none'
          });
        }
      });
    }
  },

  onPullDownRefresh() {
    this.loadBookings();
    wx.stopPullDownRefresh();
  },

  onShareAppMessage() {
    return {
      title: '我的训练日程',
      path: '/pages/schedule/schedule'
    };
  }
});