Component({
  properties: {
    coach: {
      type: Object,
      value: {}
    },
    compact: {
      type: Boolean,
      value: false
    },
    showBookButton: {
      type: Boolean,
      value: true
    }
  },

  data: {},

  methods: {
    onTap() {
      this.triggerEvent('tap', { coachId: this.data.coach.id });
    },

    onBook() {
      this.triggerEvent('book', { coachId: this.data.coach.id });
    }
  }
});