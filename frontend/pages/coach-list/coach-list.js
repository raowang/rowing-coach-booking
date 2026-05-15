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
    currentRecommendation: null
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