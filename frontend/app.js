App({
  globalData: {
    userInfo: null,
    memberProfile: null,
    accessToken: null,
    openId: null,
    apiBaseUrl: 'https://api.rowing-center.com',
    aiServiceUrl: 'https://api.rowing-center.com/ai',
    wsUrl: 'wss://api.rowing-center.com/ws/chat',
    conversationContext: {
      messages: [],
      intent: null,
      entities: {},
      lastUpdated: null
    }
  },

  onLaunch(options) {
    console.log('App launched', options);
    this.checkLoginStatus();
    this.initAIContext();
  },

  onShow(options) {
    console.log('App showed', options);
  },

  onHide() {
    console.log('App hidden');
    this.saveConversationContext();
  },

  checkLoginStatus() {
    const token = wx.getStorageSync('access_token');
    const userInfo = wx.getStorageSync('user_info');

    if (token && userInfo) {
      this.globalData.accessToken = token;
      this.globalData.userInfo = userInfo;
      this.refreshMemberProfile();
    } else {
      wx.redirectTo({
        url: '/pages/login/index'
      });
    }
  },

  initAIContext() {
    const context = wx.getStorageSync('conversation_context');
    if (context && context.lastUpdated) {
      const now = Date.now();
      const thirtyMinutes = 30 * 60 * 1000;
      if (now - context.lastUpdated < thirtyMinutes) {
        this.globalData.conversationContext = context;
      }
    }
  },

  saveConversationContext() {
    wx.setStorageSync('conversation_context', this.globalData.conversationContext);
  },

  refreshMemberProfile() {
    wx.request({
      url: `${this.globalData.apiBaseUrl}/member/profile`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${this.globalData.accessToken}`
      },
      success: (res) => {
        if (res.data.code === 0) {
          this.globalData.memberProfile = res.data.data;
          wx.setStorageSync('member_profile', res.data.data);
        }
      },
      fail: (err) => {
        console.error('Failed to refresh member profile', err);
      }
    });
  },

  loginWithWeChat(code) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/auth/wechat`,
        method: 'POST',
        data: { code },
        success: (res) => {
          if (res.data.code === 0) {
            const { access_token, member, openid } = res.data.data;
            this.globalData.accessToken = access_token;
            this.globalData.openId = openid;
            this.globalData.userInfo = member;
            this.globalData.memberProfile = member;

            wx.setStorageSync('access_token', access_token);
            wx.setStorageSync('user_info', member);
            wx.setStorageSync('member_profile', member);

            resolve(member);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  sendAIMessage(message, context) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.aiServiceUrl}/chat`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          message,
          context: context || this.globalData.conversationContext,
          member_id: this.globalData.memberProfile?.id
        },
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  generateWelcomeMessage() {
    const now = new Date();
    const hour = now.getHours();
    const member = this.globalData.memberProfile;

    let greeting = '';
    if (hour < 6) {
      greeting = '夜深了，还在坚持训练？';
    } else if (hour < 9) {
      greeting = '早上好！';
    } else if (hour < 12) {
      greeting = '上午好！';
    } else if (hour < 14) {
      greeting = '中午好！';
    } else if (hour < 18) {
      greeting = '下午好！';
    } else if (hour < 22) {
      greeting = '晚上好！';
    } else {
      greeting = '夜深了，注意休息哦';
    }

    if (member && member.birthday) {
      const today = `${now.getMonth() + 1}-${now.getDate()}`;
      const birthday = member.birthday.split('-').slice(1).join('-');
      if (today === birthday) {
        return `🎂 ${member.name}，生日快乐！今天来训练，我们准备了小礼物哦～`;
      }
    }

    if (member && member.membership_expiry) {
      const expiryDate = new Date(member.membership_expiry);
      const daysUntilExpiry = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));
      if (daysUntilExpiry <= 7 && daysUntilExpiry > 0) {
        greeting += ` 您的会籍还有${daysUntilExpiry}天到期，记得续期哦～`;
      }
    }

    if (member && member.name) {
      if (member.training_count > 10) {
        greeting += ` ${member.name}，上次训练后进步很大，继续保持！`;
      } else if (member.training_count > 0) {
        greeting += ` ${member.name}，欢迎回来！今天想预约训练吗？`;
      } else {
        greeting += ` ${member.name}，这是您第一次来吗？有什么可以帮您的？`;
      }
    }

    return greeting;
  },

  getCoaches(params = {}) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/coaches`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`
        },
        data: params,
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  getRecommendedCoaches() {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/coaches/recommended`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`
        },
        data: {
          member_id: this.globalData.memberProfile?.id
        },
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  getBookingSchedule(status = null) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/bookings`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`
        },
        data: {
          member_id: this.globalData.memberProfile?.id,
          status
        },
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  createBooking(bookingData) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/bookings`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`,
          'Content-Type': 'application/json'
        },
        data: {
          ...bookingData,
          member_id: this.globalData.memberProfile?.id
        },
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  cancelBooking(bookingId, reason = '') {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/bookings/${bookingId}/cancel`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`,
          'Content-Type': 'application/json'
        },
        data: { reason },
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  getTrainingFeedback(bookingId) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/bookings/${bookingId}/feedback`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`
        },
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  },

  getTrainingHistory(params = {}) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/trainings/history`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${this.globalData.accessToken}`
        },
        data: {
          member_id: this.globalData.memberProfile?.id,
          ...params
        },
        success: (res) => {
          if (res.data.code === 0) {
            resolve(res.data.data);
          } else {
            reject(new Error(res.data.message));
          }
        },
        fail: reject
      });
    });
  }
});