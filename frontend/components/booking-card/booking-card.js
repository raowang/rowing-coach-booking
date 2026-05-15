Component({
  properties: {
    booking: {
      type: Object,
      value: {}
    },
    showActions: {
      type: Boolean,
      value: true
    }
  },

  data: {
    statusMap: {
      'pending': { text: '待确认', class: 'pending' },
      'confirmed': { text: '已确认', class: 'confirmed' },
      'in_progress': { text: '进行中', class: 'in_progress' },
      'completed': { text: '已完成', class: 'completed' },
      'cancelled': { text: '已取消', class: 'cancelled' }
    }
  },

  methods: {
    onTap() {
      this.triggerEvent('tap', { bookingId: this.data.booking.id });
    },

    onCancel() {
      this.triggerEvent('cancel', { bookingId: this.data.booking.id });
    },

    onReminder() {
      this.triggerEvent('reminder', { bookingId: this.data.booking.id });
    },

    onCalendar() {
      this.triggerEvent('calendar', { bookingId: this.data.booking.id });
    }
  }
});