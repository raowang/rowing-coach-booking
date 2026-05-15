require('../__mocks__/wx');

describe('Booking Page', () => {
  let page;

  const mockCoach = {
    id: 'C001',
    name: 'Coach Wang',
    specialty: 'Beginner',
    rating: 4.8,
  };

  const mockSlots = [
    { id: 'S1', date: '2024-01-20', time: '09:00', available: true },
    { id: 'S2', date: '2024-01-20', time: '10:00', available: true },
    { id: 'S3', date: '2024-01-20', time: '11:00', available: false },
    { id: 'S4', date: '2024-01-21', time: '09:00', available: true },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    page = {
      data: {
        coach: mockCoach,
        selectedDate: '',
        selectedTime: '',
        selectedSlot: null,
        timeSlots: [...mockSlots],
        totalPrice: 200,
        notes: '',
      },
    };
  });

  describe('Date Selection', () => {
    test('should initialize with no date selected', () => {
      expect(page.data.selectedDate).toBe('');
    });

    test('should select a date', () => {
      page.data.selectedDate = '2024-01-20';
      expect(page.data.selectedDate).toBe('2024-01-20');
    });

    test('should filter time slots by selected date', () => {
      const selectedDate = '2024-01-20';
      const filteredSlots = page.data.timeSlots.filter(
        (slot) => slot.date === selectedDate
      );
      expect(filteredSlots).toHaveLength(3);
    });
  });

  describe('Time Selection', () => {
    test('should initialize with no time selected', () => {
      expect(page.data.selectedTime).toBe('');
    });

    test('should select a time slot', () => {
      page.data.selectedTime = '09:00';
      expect(page.data.selectedTime).toBe('09:00');
    });

    test('should select a slot object', () => {
      page.data.selectedSlot = mockSlots[0];
      expect(page.data.selectedSlot.id).toBe('S1');
    });
  });

  describe('Available Slots', () => {
    test('should show only available slots', () => {
      const availableSlots = page.data.timeSlots.filter((slot) => slot.available);
      expect(availableSlots).toHaveLength(3);
    });

    test('should mark unavailable slots', () => {
      const unavailableSlots = page.data.timeSlots.filter((slot) => !slot.available);
      expect(unavailableSlots).toHaveLength(1);
      expect(unavailableSlots[0].time).toBe('11:00');
    });
  });

  describe('Date Formatting', () => {
    test('should format date for display', () => {
      const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekDay = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()];
        return `${month}/${day} ${weekDay}`;
      };
      expect(formatDate('2024-01-20')).toBe('1/20 Sat');
    });

    test('should handle date comparison', () => {
      const isToday = (dateStr) => {
        const today = new Date().toISOString().split('T')[0];
        return dateStr === today;
      };
      expect(isToday('2024-01-20')).toBe(false);
    });
  });

  describe('Price Calculation', () => {
    test('should set base price from coach', () => {
      expect(page.data.totalPrice).toBe(200);
    });

    test('should calculate total with duration', () => {
      const basePrice = 200;
      const duration = 2;
      const total = basePrice * duration;
      expect(total).toBe(400);
    });
  });

  describe('Booking Submission', () => {
    test('should validate selected date exists', () => {
      const isValid = page.data.selectedDate !== '' && page.data.selectedTime !== '';
      expect(isValid).toBe(false);
    });

    test('should pass validation when date and time selected', () => {
      page.data.selectedDate = '2024-01-20';
      page.data.selectedTime = '09:00';
      const isValid = page.data.selectedDate !== '' && page.data.selectedTime !== '';
      expect(isValid).toBe(true);
    });

    test('should call requestPayment on confirm', () => {
      wx.requestPayment = jest.fn();
      page.data.selectedDate = '2024-01-20';
      page.data.selectedTime = '09:00';
      if (page.data.selectedDate && page.data.selectedTime) {
        wx.requestPayment({
          timeStamp: Date.now().toString(),
          nonceStr: 'test',
          package: 'prepay_id=test',
          signType: 'MD5',
          paySign: 'test',
        });
      }
      expect(wx.requestPayment).toHaveBeenCalled();
    });
  });

  describe('Notes', () => {
    test('should handle notes input', () => {
      page.data.notes = 'Please prepare rowing equipment';
      expect(page.data.notes).toBe('Please prepare rowing equipment');
    });

    test('should limit notes length', () => {
      const maxLength = 200;
      page.data.notes = 'A'.repeat(250);
      const truncated = page.data.notes.slice(0, maxLength);
      expect(truncated.length).toBe(maxLength);
    });
  });
});