// Dummy coach data for development
const dummyCoaches = [
  {
    id: '1',
    name: '张教练',
    avatarUrl: '/miniprogram/assets/images/coach-1.png',
    title: '国家级赛艇教练',
    tags: ['新手友好', '技术提升'],
    rating: 4.9,
    training_count: 328,
    experience: 12,
    description: '曾执教省队，擅长零基础教学，注重技术细节。',
    available: true
  },
  {
    id: '2',
    name: '李教练',
    avatarUrl: '/miniprogram/assets/images/coach-2.png',
    title: '国际认证教练',
    tags: ['进阶专业', '耐力训练'],
    rating: 4.8,
    training_count: 256,
    experience: 8,
    description: '专注于竞速训练，帮助多名学员取得省级比赛前三。',
    available: true
  },
  {
    id: '3',
    name: '王教练',
    avatarUrl: '/miniprogram/assets/images/coach-3.png',
    title: '青少年赛艇教练',
    tags: ['耐心教学', '新手友好'],
    rating: 4.7,
    training_count: 189,
    experience: 6,
    description: '专长青少年培训，性格温和有耐心。',
    available: false
  },
  {
    id: '4',
    name: '陈教练',
    avatarUrl: '/miniprogram/assets/images/coach-4.png',
    title: '体能与技术教练',
    tags: ['技术提升', '耐力训练'],
    rating: 4.9,
    training_count: 412,
    experience: 15,
    description: '全面提升学员体能与技术，注重科学训练方法。',
    available: true
  },
  {
    id: '5',
    name: '刘教练',
    avatarUrl: '/miniprogram/assets/images/coach-5.png',
    title: '女子赛艇教练',
    tags: ['新手友好', '耐心教学'],
    rating: 4.6,
    training_count: 167,
    experience: 5,
    description: '专注于女子赛艇培训，教学细致入微。',
    available: true
  }
];

const dummyRecommendedCoaches = [
  {
    id: '1',
    name: '张教练',
    avatarUrl: '/miniprogram/assets/images/coach-1.png',
    title: '国家级赛艇教练',
    tags: ['新手友好', '技术提升'],
    rating: 4.9,
    training_count: 328,
    reason: '根据您的新手身份，为您推荐张教练，擅长零基础教学。'
  },
  {
    id: '4',
    name: '陈教练',
    avatarUrl: '/miniprogram/assets/images/coach-4.png',
    title: '体能与技术教练',
    tags: ['技术提升', '耐力训练'],
    rating: 4.9,
    training_count: 412,
    reason: '您近期训练强度提升较快，陈教练擅长综合训练提升。'
  }
];

Page({
  data: {
    coaches: [],
    recommendedCoaches: [],
    filterTags: [],
    selectedFilter: null,
    searchKeyword: '',
    isLoading: false,
    isLoadingMore: false,
    page: 1,
    pageSize: 10,
    hasMore: true,
    showRecommendationModal: false,
    currentRecommendation: null,
    useMockData: true  // Set to false when API is available
  },

  onLoad(options) {
    this.loadFilterTags();
    this.loadCoaches();
    this.loadRecommendedCoaches();

    if (options.recommended === 'true') {
      this.showRecommendationModal = true;
    }
  },

  onShow() {
    this.refreshData();
  },

  loadFilterTags() {
    const tags = [
      { id: 'all', name: '全部', icon: '🌟' },
      { id: 'beginner', name: '新手友好', icon: '🌱' },
      { id: 'advanced', name: '进阶专业', icon: '🚀' },
      { id: 'technique', name: '技术提升', icon: '🎯' },
      { id: 'endurance', name: '耐力训练', icon: '💪' },
      { id: 'patient', name: '耐心教学', icon: '🙏' }
    ];
    this.setData({ filterTags: tags });
  },

  loadCoaches(refresh = false) {
    if (this.data.isLoading) return;

    if (refresh) {
      this.setData({ page: 1, coaches: [], hasMore: true });
    }

    this.setData({ isLoading: true });

    // Use mock data in development
    if (this.data.useMockData) {
      setTimeout(() => {
        const newCoaches = refresh ? dummyCoaches : [...this.data.coaches, ...dummyCoaches];
        this.setData({
          coaches: newCoaches,
          hasMore: false,
          isLoading: false,
          isLoadingMore: false
        });
      }, 500);
      return;
    }

    const app = getApp();
    const params = {
      page: this.data.page,
      pageSize: this.data.pageSize
    };

    if (this.data.selectedFilter && this.data.selectedFilter !== 'all') {
      params.tag = this.data.selectedFilter;
    }

    if (this.data.searchKeyword) {
      params.keyword = this.data.searchKeyword;
    }

    app.getCoaches(params).then(data => {
      const newCoaches = refresh ? data.list : [...this.data.coaches, ...data.list];
      this.setData({
        coaches: newCoaches,
        hasMore: data.list.length >= this.data.pageSize,
        isLoading: false,
        isLoadingMore: false
      });
    }).catch(err => {
      console.error('Failed to load coaches', err);
      this.setData({ isLoading: false, isLoadingMore: false });
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    });
  },

  loadRecommendedCoaches() {
    // Use mock data in development
    if (this.data.useMockData) {
      setTimeout(() => {
        this.setData({ recommendedCoaches: dummyRecommendedCoaches });
      }, 500);
      return;
    }

    const app = getApp();
    app.getRecommendedCoaches().then(coaches => {
      this.setData({ recommendedCoaches: coaches });
    }).catch(err => {
      console.error('Failed to load recommended coaches', err);
    });
  },

  refreshData() {
    this.loadCoaches(true);
    this.loadRecommendedCoaches();
  },

  onFilterTap(e) {
    const { filterId } = e.currentTarget.dataset;
    this.setData({ selectedFilter: filterId });
    this.loadCoaches(true);
  },

  onSearchInput(e) {
    this.setData({ searchKeyword: e.detail.value });
  },

  onSearchConfirm() {
    this.loadCoaches(true);
  },

  onCoachTap(e) {
    const { coachId } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/booking/booking?coachId=${coachId}`
    });
  },

  onRecommendedCoachTap(e) {
    const { coachId } = e.currentTarget.dataset;
    const coach = this.data.recommendedCoaches.find(c => c.id === coachId);
    if (coach) {
      this.setData({
        showRecommendationModal: true,
        currentRecommendation: coach
      });
    }
  },

  onCloseRecommendationModal() {
    this.setData({
      showRecommendationModal: false,
      currentRecommendation: null
    });
  },

  onBookRecommendedCoach() {
    const coach = this.data.currentRecommendation;
    if (coach) {
      wx.navigateTo({
        url: `/pages/booking/booking?coachId=${coach.id}`
      });
    }
  },

  onScrollToLower() {
    if (!this.data.isLoadingMore && this.data.hasMore) {
      this.setData({
        page: this.data.page + 1,
        isLoadingMore: true
      });
      this.loadCoaches();
    }
  },

  onPullDownRefresh() {
    this.refreshData();
    wx.stopPullDownRefresh();
  },

  onShareAppMessage() {
    return {
      title: '赛艇中心 - 专业教练团队',
      path: '/pages/coach-list/coach-list'
    };
  }
});