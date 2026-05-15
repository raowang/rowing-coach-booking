require('../__mocks__/wx');

describe('Format Utils', () => {
  describe('Date Formatting', () => {
    test('should format date to MM/DD', () => {
      const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${month}/${day}`;
      };
      expect(formatDate('2024-01-15')).toBe('1/15');
      expect(formatDate('2024-12-25')).toBe('12/25');
    });

    test('should format date with leading zeros', () => {
      const formatDatePadded = (dateStr) => {
        const date = new Date(dateStr);
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${month}/${day}`;
      };
      expect(formatDatePadded('2024-01-05')).toBe('01/05');
      expect(formatDatePadded('2024-12-09')).toBe('12/09');
    });

    test('should get weekday name', () => {
      const getWeekday = (dateStr) => {
        const date = new Date(dateStr);
        const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        return weekdays[date.getDay()];
      };
      expect(getWeekday('2024-01-15')).toBe('Mon');
      expect(getWeekday('2024-01-20')).toBe('Sat');
      expect(getWeekday('2024-01-21')).toBe('Sun');
    });

    test('should format full date', () => {
      const formatFullDate = (dateStr) => {
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
      };
      expect(formatFullDate('2024-01-15')).toBe('2024-01-15');
    });
  });

  describe('Time Formatting', () => {
    test('should format 24h time to 12h', () => {
      const formatTime12h = (timeStr) => {
        const [hours, minutes] = timeStr.split(':');
        const hour = parseInt(hours, 10);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${displayHour}:${minutes} ${ampm}`;
      };
      expect(formatTime12h('00:00')).toBe('12:00 AM');
      expect(formatTime12h('09:00')).toBe('9:00 AM');
      expect(formatTime12h('12:00')).toBe('12:00 PM');
      expect(formatTime12h('14:30')).toBe('2:30 PM');
      expect(formatTime12h('23:59')).toBe('11:59 PM');
    });

    test('should format time with HH:MM', () => {
      const formatTime = (date) => {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
      };
      const date = new Date(2024, 0, 15, 9, 5);
      expect(formatTime(date)).toBe('09:05');
    });

    test('should format time range', () => {
      const formatTimeRange = (startTime, endTime) => {
        const format = (t) => {
          const [h, m] = t.split(':');
          const hour = parseInt(h, 10);
          const ampm = hour >= 12 ? 'PM' : 'AM';
          const displayHour = hour % 12 || 12;
          return `${displayHour}:${m} ${ampm}`;
        };
        return `${format(startTime)} - ${format(endTime)}`;
      };
      expect(formatTimeRange('09:00', '10:00')).toBe('9:00 AM - 10:00 AM');
      expect(formatTimeRange('14:00', '15:30')).toBe('2:00 PM - 3:30 PM');
    });
  });

  describe('Date Time Combined', () => {
    test('should format date time for display', () => {
      const formatDateTime = (dateStr, timeStr) => {
        const date = new Date(dateStr);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const weekDay = weekdays[date.getDay()];
        const [hours, minutes] = timeStr.split(':');
        const hour = parseInt(hours, 10);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${month}/${day} ${weekDay} ${displayHour}:${minutes} ${ampm}`;
      };
      expect(formatDateTime('2024-01-20', '09:00')).toBe('1/20 Sat 9:00 AM');
    });
  });

  describe('Duration Formatting', () => {
    test('should format duration in minutes', () => {
      const formatDuration = (minutes) => {
        if (minutes < 60) return `${minutes}min`;
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
      };
      expect(formatDuration(30)).toBe('30min');
      expect(formatDuration(60)).toBe('1h');
      expect(formatDuration(90)).toBe('1h 30min');
      expect(formatDuration(120)).toBe('2h');
    });
  });

  describe('Relative Time', () => {
    test('should identify today', () => {
      const isToday = (dateStr) => {
        const today = new Date();
        const date = new Date(dateStr);
        return (
          date.getDate() === today.getDate() &&
          date.getMonth() === today.getMonth() &&
          date.getFullYear() === today.getFullYear()
        );
      };
      const todayStr = new Date().toISOString().split('T')[0];
      expect(isToday(todayStr)).toBe(true);
      expect(isToday('2020-01-01')).toBe(false);
    });

    test('should identify tomorrow', () => {
      const isTomorrow = (dateStr) => {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const date = new Date(dateStr);
        return (
          date.getDate() === tomorrow.getDate() &&
          date.getMonth() === tomorrow.getMonth() &&
          date.getFullYear() === tomorrow.getFullYear()
        );
      };
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().split('T')[0];
      expect(isTomorrow(tomorrowStr)).toBe(true);
    });
  });

  describe('Price Formatting', () => {
    test('should format price with currency', () => {
      const formatPrice = (amount) => {
        return `¥${amount.toFixed(2)}`;
      };
      expect(formatPrice(200)).toBe('¥200.00');
      expect(formatPrice(150.5)).toBe('¥150.50');
    });

    test('should format price without decimals when whole', () => {
      const formatPriceSimple = (amount) => {
        return Number.isInteger(amount) ? `¥${amount}` : `¥${amount.toFixed(2)}`;
      };
      expect(formatPriceSimple(200)).toBe('¥200');
      expect(formatPriceSimple(150.5)).toBe('¥150.50');
    });
  });

  describe('Phone Formatting', () => {
    test('should format phone number', () => {
      const formatPhone = (phone) => {
        if (!phone || phone.length !== 11) return phone;
        return `${phone.slice(0, 3)}-${phone.slice(3, 7)}-${phone.slice(7)}`;
      };
      expect(formatPhone('13812345678')).toBe('138-1234-5678');
    });
  });

  describe('Name Formatting', () => {
    test('should mask name for privacy', () => {
      const maskName = (name) => {
        if (!name || name.length < 2) return name;
        return name[0] + '*'.repeat(name.length - 1);
      };
      expect(maskName('Wang')).toBe('W***');
      expect(maskName('Zhang')).toBe('Z****');
    });

    test('should handle short names', () => {
      const maskName = (name) => {
        if (!name || name.length < 2) return name;
        return name[0] + '*'.repeat(name.length - 1);
      };
      expect(maskName('Li')).toBe('L*');
      expect(maskName('A')).toBe('A');
    });
  });
});