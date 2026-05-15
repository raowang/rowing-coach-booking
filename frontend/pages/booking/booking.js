Page({
  data: {
    step: 1,
    coachId: null,
    coach: null,
    selectedDate: null,
    selectedTimeSlot: null,
    availableDates: [],
    availableTimeSlots: [],
    bookingNote: '',
    isLoading: false,
    isSubmitting: false,
    bookingResult: null,
    memberSuggestions: [],
    showSuggestions: false
  },

  onLoad(options) {
    if (options.coachId) {
      this.setData({ coachId: options.coachId });
      this.loadCoach(options.coachId);
    }
    this.generateAvailableDates();
    this.loadMemberSuggestions();
  },

  loadCoach(coachId) {
    this.setData({ isLoading: true });
    const app = getApp();

    app.getCoaches({ id: coachId }).then(coaches => {
      if (coaches && coaches.length > 0) {
        this.setData({
          coach: coaches[0],
          isLoading: false
        });
        this.loadCoachTimeSlots();
      } else {
        this.setData({ isLoading: false });
        wx.showToast({
          title: '教练不存在',
          icon: 'none'
        });
      }
    }).catch(err => {
      console.error('Failed to load coach', err);
      this.setData({ isLoading: false });
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    });
  },

  loadCoachTimeSlots() {
    const coach = this.data.coach;
    if (!coach || !coach.timeSlots) return;

    const timeSlots = coach.timeSlots.map(slot => ({
      id: slot.id,
      time: slot.time,
      available: slot.available
    }));

    this.setData({ availableTimeSlots: timeSlots });
  },

  generateAvailableDates() {
    const dates = [];
    const today = new Date();

    for (let i = 0; i < 14; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);

      const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
      const dayName = dayNames[date.getDay()];

      dates.push({
        date: date.toISOString().split('T')[0],
        day: date.getDate(),
        month: date.getMonth() + 1,
        dayName: dayName,
        isToday: i === 0,
        isWeekend: date.getDay() === 0 || date.getDay() === 6
      });
    }

    this.setData({ availableDates: dates });
  },

  loadMemberSuggestions() {
    const app = getApp();
    const memberProfile = app.globalData.memberProfile;

    if (memberProfile && memberProfile.historySuggestions) {
      this.setData({
        memberSuggestions: memberProfile.historySuggestions,
        showSuggestions: true
      });
    }
  },

  onDateSelect(e) {
    const { date } = e.currentTarget.dataset;
    this.setData({ selectedDate: date, selectedTimeSlot: null });
    this.updateTimeSlotsForDate(date);
  },

  updateTimeSlotsForDate(date) {
    const app = getApp();
    const coach = this.data.coach;

    if (!coach) return;

    const timeSlots = coach.timeSlotsByDate?.[date] || coach.timeSlots || [];

    const formattedSlots = timeSlots.map(slot => ({
      id: slot.id,
      time: slot.time,
      available: slot.available
    }));

    this.setData({ availableTimeSlots: formattedSlots });
  },

  onTimeSlotSelect(e) {
    const { slotId } = e.currentTarget.dataset;
    const slot = this.data.availableTimeSlots.find(s => s.id === slotId);

    if (slot && slot.available) {
      this.setData({ selectedTimeSlot: slot });
    } else {
      wx.showToast({
        title: '该时段已满',
        icon: 'none'
      });
    }
  },

  onNoteInput(e) {
    this.setData({ bookingNote: e.detail.value });
  },

  onSuggestionTap(e) {
    const { suggestion } = e.currentTarget.dataset;
    if (suggestion) {
      this.setData({
        bookingNote: suggestion,
        showSuggestions: false
      });
    }
  },

  onToggleSuggestions() {
    this.setData({ showSuggestions: !this.data.showSuggestions });
  },

  onNextStep() {
    if (!this.data.selectedDate) {
      wx.showToast({
        title: '请选择日期',
        icon: 'none'
      });
      return;
    }

    if (!this.data.selectedTimeSlot) {
      wx.showToast({
        title: '请选择时间',
        icon: 'none'
      });
      return;
    }

    this.setData({ step: 2 });
  },

  onPrevStep() {
    if (this.data.step > 1) {
      this.setData({ step: this.data.step - 1 });
    }
  },

  onSubmitBooking() {
    if (this.data.isSubmitting) return;

    this.setData({ isSubmitting: true });

    const app = getApp();
    const bookingData = {
      coach_id: this.data.coachId,
      date: this.data.selectedDate,
      time_slot_id: this.data.selectedTimeSlot.id,
      note: this.data.bookingNote
    };

    app.createBooking(bookingData).then(result => {
      this.setData({
        bookingResult: result,
        isSubmitting: false,
        step: 3
      });

      wx.showToast({
        title: '预约成功',
        icon: 'success'
      });
    }).catch(err => {
      console.error('Failed to create booking', err);
      this.setData({ isSubmitting: false });
      wx.showToast({
        title: '预约失败，请重试',
        icon: 'none'
      });
    });
  },

  onViewSchedule() {
    wx.switchTab({
      url: '/pages/schedule/schedule'
    });
  },

  onBackToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  },

  onShareAppMessage() {
    return {
      title: '预约赛艇训练',
      path: '/pages/booking/booking'
    };
  }
});