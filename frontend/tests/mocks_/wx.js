const wx = {
  getStorageSync: jest.fn((key) => {
    const store = {
      userInfo: { id: 'test-user-1', name: 'Test User' },
      token: 'test-token-123',
    };
    return store[key];
  }),
  setStorageSync: jest.fn(),
  getStorage: jest.fn(),
  setStorage: jest.fn(),
  navigateTo: jest.fn(),
  redirectTo: jest.fn(),
  reLaunch: jest.fn(),
  switchTab: jest.fn(),
  navigateBack: jest.fn(),
  request: jest.fn(),
  uploadFile: jest.fn(),
  downloadFile: jest.fn(),
  showToast: jest.fn(),
  showModal: jest.fn(),
  showLoading: jest.fn(),
  hideLoading: jest.fn(),
  showActionSheet: jest.fn(),
  getFormId: jest.fn(),
  login: jest.fn(),
  getUserProfile: jest.fn(),
  getUserInfo: jest.fn(),
  getLocation: jest.fn(),
  chooseLocation: jest.fn(),
  requestPayment: jest.fn(),
  createCanvasContext: jest.fn(),
  createRewardedVideoAd: jest.fn(),
  eventCenter: {
    on: jest.fn(),
    off: jest.fn(),
    trigger: jest.fn(),
  },
  getApp: jest.fn(() => ({
    globalData: { openId: 'test-openid' },
  })),
  canIUse: jest.fn(() => true),
  getSystemInfoSync: jest.fn(() => ({
    platform: 'devtools',
    version: '7.0.0',
  })),
};

global.wx = wx;

module.exports = wx;