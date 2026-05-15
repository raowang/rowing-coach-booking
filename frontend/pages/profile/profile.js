Page({
  data: {
    member: null,
    stats: {
      totalTrainings: 0,
      thisMonth: 0,
      consecutiveDays: 0,
      totalHours: 0
    },
    membership: {
      type: '',
      expiryDate: '',
      daysRemaining: 0,
      status: ''
    },
    achievements: [],
    recentActivities: []
  },

  onLoad() {
    this.loadMemberProfile();
    this.loadMemberStats();
    this.loadAchievements();
    this.loadRecentActivities();
  },

  onShow() {
    this.refreshData();
  },

  loadMemberProfile() {
    const app = getApp();
    const member = app.globalData.memberProfile || app.globalData.userInfo;

    if (member) {
      let membershipStatus = 'active';
      let daysRemaining = 0;

      if (member.membership_expiry) {
        const expiryDate = new Date(member.membership_expiry);
        const today = new Date();
        daysRemaining = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));

        if (daysRemaining < 0) {
          membershipStatus = 'expired';
        } else if (daysRemaining <= 7) {
          membershipStatus = 'expiring';
        }
      }

      this.setData({
        member: member,
        membership: {
          type: member.membership_type || '年度会员',
          expiryDate: member.membership_expiry || '',
          daysRemaining: daysRemaining,
          status: membershipStatus
        }
      });
    }
  },

  loadMemberStats() {
    const app = getApp();
    app.getTrainingHistory({ limit: 100 }).then(history => {
      const totalTrainings = history.length;
      const thisMonth = history.filter(item => {
        const itemDate = new Date(item.date);
        const now = new Date();
        return itemDate.getMonth() === now.getMonth() &&
               itemDate.getFullYear() === now.getFullYear();
      }).length;

      const totalHours = history.reduce((sum, item) => sum + (item.duration || 0), 0) / 60;

      let consecutiveDays = 0;
      if (history.length > 0) {
        const sortedHistory = history.sort((a, b) => new Date(b.date) - new Date(a.date));
        let lastDate = null;
        let count = 0;

        for (const item of sortedHistory) {
          const itemDate = new Date(item.date).toDateString();
          if (lastDate === null) {
            lastDate = itemDate;
            count = 1;
          } else if (itemDate === lastDate) {
            continue;
          } else {
            const diff = new Date(lastDate) - new Date(itemDate);
            if (diff === 86400000) {
              count++;
              lastDate = itemDate;
            } else {
              break;
            }
          }
        }
        consecutiveDays = count;
      }

      this.setData({
        stats: {
          totalTrainings,
          thisMonth,
          consecutiveDays,
          totalHours: Math.round(totalHours)
        }
      });
    }).catch(err => {
      console.error('Failed to load member stats', err);
    });
  },

  loadAchievements() {
    const achievements = [
      {
        id: 'first_training',
        icon: '🎯',
        title: '初次训练',
        desc: '完成第一次训练',
        unlocked: true,
        progress: 1,
        total: 1
      },
      {
        id: 'ten_trainings',
        icon: '🔥',
        title: '坚持不懈',
        desc: '完成10次训练',
        unlocked: this.data.stats?.totalTrainings >= 10,
        progress: Math.min(this.data.stats?.totalTrainings || 0, 10),
        total: 10
      },
      {
        id: 'week_streak',
        icon: '💪',
        title: '一周坚持',
        desc: '连续训练7天',
        unlocked: this.data.stats?.consecutiveDays >= 7,
        progress: Math.min(this.data.stats?.consecutiveDays || 0, 7),
        total: 7
      },
      {
        id: 'monthly_master',
        icon: '🏆',
        title: '月度大师',
        desc: '单月完成15次训练',
        unlocked: this.data.stats?.thisMonth >= 15,
        progress: Math.min(this.data.stats?.thisMonth || 0, 15),
        total: 15
      }
    ];

    this.setData({ achievements });
  },

  loadRecentActivities() {
    const app = getApp();
    app.getTrainingHistory({ limit: 5 }).then(history => {
      this.setData({ recentActivities: history });
    }).catch(err => {
      console.error('Failed to load recent activities', err);
    });
  },

  refreshData() {
    this.loadMemberProfile();
    this.loadMemberStats();
    this.loadAchievements();
  },

  onEditProfile() {
    wx.navigateTo({
      url: '/pages/profile/edit'
    });
  },

  onMembershipTap() {
    wx.showModal({
      title: '会籍信息',
      content: `会籍类型：${this.data.membership.type}\n到期日期：${this.data.membership.expiryDate}\n状态：${this.data.membership.status === 'active' ? '有效' : this.data.membership.status === 'expiring' ? '即将到期' : '已过期'}`,
      confirmText: '联系客服',
      cancelText: '关闭',
      success: (res) => {
        if (res.confirm) {
          wx.makePhoneCall({
            phoneNumber: '400-888-8888'
          });
        }
      }
    });
  },

  onTrainingHistoryTap() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    });
  },

  onSettingsTap() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    });
  },

  onHelpTap() {
    wx.navigateTo({
      url: '/pages/help/help'
    });
  },

  onShareAppMessage() {
    return {
      title: '我的赛艇中心主页',
      path: '/pages/profile/profile'
    };
  }
});