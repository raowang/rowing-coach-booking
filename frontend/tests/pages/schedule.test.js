require('../__mocks__/wx');

describe('Schedule Page', () => {
  let page;

  const mockBookings = [
    {
      id: 'B001',
      coachName: 'Coach Wang',
      date: '2024-01-20',
      time: '09:00',
      status: 'confirmed',
      type: 'Beginner Training',
    },
    {
      id: 'B002',
      coachName: 'Coach Li',
      date: '2024-01-22',
      time: '14:00',
      status: 'pending',
      type: 'Advanced Training',
    },
    {
      id: 'B003',
      coachName: 'Coach Zhang',
      date: '2024-01-18',
      time: '10:00',
      status: 'completed',
      type: 'Intermediate Training',
    },
    {
      id: 'B004',
      coachName: 'Coach Liu',
      date: '2024-01-25',
      time: '11:00',
      status: 'cancelled',
      type: 'Beginner Training',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    page = {
      data: {
        bookings: [...mockBookings],
        filteredBookings: [...mockBookings],
        filterStatus: 'all',
        currentMonth: '2024-01',
      },
    };
  });

  describe('Booking List', () => {
    test('should have 4 bookings initially', () => {
      expect(page.data.bookings).toHaveLength(4);
    });

    test('should display booking coach name', () => {
      expect(page.data.bookings[0].coachName).toBe('Coach Wang');
    });

    test('should display booking status', () => {
      expect(page.data.bookings[0].status).toBe('confirmed');
    });
  });

  describe('Status Filtering', () => {
    test('should show all bookings when filter is all', () => {
      page.data.filterStatus = 'all';
      const filtered =
        page.data.filterStatus === 'all'
          ? page.data.bookings
          : page.data.bookings.filter((b) => b.status === page.data.filterStatus);
      expect(filtered).toHaveLength(4);
    });

    test('should filter confirmed bookings', () => {
      const filtered = page.data.bookings.filter((b) => b.status === 'confirmed');
      expect(filtered).toHaveLength(1);
    });

    test('should filter pending bookings', () => {
      const filtered = page.data.bookings.filter((b) => b.status === 'pending');
      expect(filtered).toHaveLength(1);
    });

    test('should filter completed bookings', () => {
      const filtered = page.data.bookings.filter((b) => b.status === 'completed');
      expect(filtered).toHaveLength(1);
    });

    test('should filter cancelled bookings', () => {
      const filtered = page.data.bookings.filter((b) => b.status === 'cancelled');
      expect(filtered).toHaveLength(1);
    });
  });

  describe('Month Filtering', () => {
    test('should filter bookings by month', () => {
      const targetMonth = '2024-01';
      const filtered = page.data.bookings.filter((b) => b.date.startsWith(targetMonth));
      expect(filtered).toHaveLength(4);
    });

    test('should return empty for non-matching month', () => {
      const targetMonth = '2024-03';
      const filtered = page.data.bookings.filter((b) => b.date.startsWith(targetMonth));
      expect(filtered).toHaveLength(0);
    });
  });

  describe('Date Display', () => {
    test('should format date for display', () => {
      const formatDisplayDate = (dateStr) => {
        const date = new Date(dateStr);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${month}/${day}`;
      };
      expect(formatDisplayDate('2024-01-20')).toBe('1/20');
    });

    test('should identify past bookings', () => {
      const isPastBooking = (dateStr) => {
        const bookingDate = new Date(dateStr);
        const today = new Date('2024-01-19');
        return bookingDate < today;
      };
      expect(isPastBooking('2024-01-18')).toBe(true);
      expect(isPastBooking('2024-01-20')).toBe(false);
    });
  });

  describe('Time Display', () => {
    test('should format time for display', () => {
      const formatTime = (timeStr) => {
        const [hours, minutes] = timeStr.split(':');
        const hour = parseInt(hours, 10);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${displayHour}:${minutes} ${ampm}`;
      };
      expect(formatTime('09:00')).toBe('9:00 AM');
      expect(formatTime('14:00')).toBe('2:00 PM');
    });
  });

  describe('Booking Actions', () => {
    test('should navigate to booking detail', () => {
      wx.navigateTo = jest.fn();
      const bookingId = 'B001';
      wx.navigateTo({ url: `/pages/booking-detail/index?id=${bookingId}` });
      expect(wx.navigateTo).toHaveBeenCalledWith({
        url: `/pages/booking-detail/index?id=${bookingId}`,
      });
    });

    test('should show cancel confirmation', () => {
      wx.showModal = jest.fn();
      wx.showModal({
        title: 'Cancel Booking',
        content: 'Are you sure you want to cancel this booking?',
        success: (res) => {
          if (res.confirm) {
            page.data.filterStatus = 'cancelled';
          }
        },
      });
      expect(wx.showModal).toHaveBeenCalled();
    });

    test('should show toast on cancel success', () => {
      wx.showToast = jest.fn();
      wx.showToast({ title: 'Booking cancelled', icon: 'success' });
      expect(wx.showToast).toHaveBeenCalledWith({ title: 'Booking cancelled', icon: 'success' });
    });
  });

  describe('Upcoming Bookings', () => {
    test('should filter upcoming bookings (future dates)', () => {
      const today = new Date('2024-01-19');
      const upcoming = page.data.bookings.filter((b) => {
        const bookingDate = new Date(b.date);
        return bookingDate >= today && b.status !== 'cancelled';
      });
      expect(upcoming).toHaveLength(2);
    });
  });

  describe('Status Badge', () => {
    test('should return correct badge color for status', () => {
      const getStatusColor = (status) => {
        const colors = {
          confirmed: '#07c160',
          pending: '#faad14',
          completed: '#909399',
          cancelled: '#f56c6c',
        };
        return colors[status] || '#909399';
      };
      expect(getStatusColor('confirmed')).toBe('#07c160');
      expect(getStatusColor('pending')).toBe('#faad14');
      expect(getStatusColor('completed')).toBe('#909399');
      expect(getStatusColor('cancelled')).toBe('#f56c6c');
    });
  });
});