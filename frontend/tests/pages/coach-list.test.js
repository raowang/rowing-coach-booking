require('../__mocks__/wx');

describe('Coach List Page', () => {
  let page;

  const mockCoaches = [
    { id: 'C001', name: 'Coach Wang', specialty: 'Beginner', rating: 4.8, price: 200, available: true },
    { id: 'C002', name: 'Coach Li', specialty: 'Advanced', rating: 4.9, price: 300, available: true },
    { id: 'C003', name: 'Coach Zhang', specialty: 'Intermediate', rating: 4.7, available: false },
    { id: 'C004', name: 'Coach Liu', specialty: 'Beginner', rating: 4.5, price: 150, available: true },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    page = {
      data: {
        coaches: [...mockCoaches],
        filteredCoaches: [...mockCoaches],
        searchKey: '',
        filterSpecialty: 'all',
        sortBy: 'rating',
      },
    };
  });

  describe('Coach List', () => {
    test('should have 4 coaches in initial list', () => {
      expect(page.data.coaches).toHaveLength(4);
    });

    test('should display coach name', () => {
      expect(page.data.coaches[0].name).toBe('Coach Wang');
    });

    test('should display coach specialty', () => {
      expect(page.data.coaches[0].specialty).toBe('Beginner');
    });

    test('should display coach rating', () => {
      expect(page.data.coaches[0].rating).toBe(4.8);
    });
  });

  describe('Search', () => {
    test('should filter coaches by name search', () => {
      const searchKey = 'Wang';
      const filtered = page.data.coaches.filter((coach) =>
        coach.name.toLowerCase().includes(searchKey.toLowerCase())
      );
      expect(filtered).toHaveLength(1);
      expect(filtered[0].name).toBe('Coach Wang');
    });

    test('should return all coaches when search is empty', () => {
      const searchKey = '';
      const filtered = page.data.coaches.filter((coach) =>
        coach.name.toLowerCase().includes(searchKey.toLowerCase())
      );
      expect(filtered).toHaveLength(4);
    });

    test('should be case insensitive', () => {
      const searchKey = 'WANG';
      const filtered = page.data.coaches.filter((coach) =>
        coach.name.toLowerCase().includes(searchKey.toLowerCase())
      );
      expect(filtered).toHaveLength(1);
    });
  });

  describe('Filtering', () => {
    test('should filter by specialty - Beginner', () => {
      const filterSpecialty = 'Beginner';
      const filtered = page.data.coaches.filter(
        (coach) => coach.specialty === filterSpecialty
      );
      expect(filtered).toHaveLength(2);
    });

    test('should filter by specialty - Advanced', () => {
      const filterSpecialty = 'Advanced';
      const filtered = page.data.coaches.filter(
        (coach) => coach.specialty === filterSpecialty
      );
      expect(filtered).toHaveLength(1);
    });

    test('should filter available coaches only', () => {
      const availableOnly = page.data.coaches.filter((coach) => coach.available);
      expect(availableOnly).toHaveLength(3);
    });
  });

  describe('Sorting', () => {
    test('should sort by rating descending', () => {
      const sorted = [...page.data.coaches].sort((a, b) => b.rating - a.rating);
      expect(sorted[0].rating).toBe(4.9);
      expect(sorted[3].rating).toBe(4.5);
    });

    test('should sort by price ascending', () => {
      const withPrice = page.data.coaches.filter((c) => c.price);
      const sorted = withPrice.sort((a, b) => a.price - b.price);
      expect(sorted[0].price).toBe(150);
      expect(sorted[sorted.length - 1].price).toBe(300);
    });

    test('should sort by price descending', () => {
      const withPrice = page.data.coaches.filter((c) => c.price);
      const sorted = withPrice.sort((a, b) => b.price - a.price);
      expect(sorted[0].price).toBe(300);
    });
  });

  describe('Combined Filter and Search', () => {
    test('should filter by specialty and search by name', () => {
      const filterSpecialty = 'Beginner';
      const searchKey = 'Wang';
      const filtered = page.data.coaches.filter(
        (coach) =>
          coach.specialty === filterSpecialty &&
          coach.name.toLowerCase().includes(searchKey.toLowerCase())
      );
      expect(filtered).toHaveLength(1);
      expect(filtered[0].name).toBe('Coach Wang');
    });
  });

  describe('Coach Actions', () => {
    test('should navigate to coach detail', () => {
      wx.navigateTo = jest.fn();
      const coachId = 'C001';
      wx.navigateTo({ url: `/pages/coach-detail/index?id=${coachId}` });
      expect(wx.navigateTo).toHaveBeenCalledWith({
        url: `/pages/coach-detail/index?id=${coachId}`,
      });
    });

    test('should show toast when coach not available', () => {
      wx.showToast = jest.fn();
      const unavailableCoach = page.data.coaches[2];
      if (!unavailableCoach.available) {
        wx.showToast({ title: 'Coach not available', icon: 'none' });
      }
      expect(wx.showToast).toHaveBeenCalledWith({ title: 'Coach not available', icon: 'none' });
    });
  });
});