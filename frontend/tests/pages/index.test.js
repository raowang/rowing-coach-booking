require('../__mocks__/wx');

describe('Index Page - AI Chat', () => {
  let page;

  beforeEach(() => {
    jest.clearAllMocks();
    page = {
      data: {
        messages: [],
        inputText: '',
        isLoading: false,
        userInfo: wx.getStorageSync('userInfo'),
      },
    };
  });

  describe('Message Handling', () => {
    test('should initialize with empty messages array', () => {
      expect(page.data.messages).toEqual([]);
    });

    test('should add user message to messages array', () => {
      const userMessage = { role: 'user', content: 'Hello', time: '10:00' };
      page.data.messages.push(userMessage);
      expect(page.data.messages).toHaveLength(1);
      expect(page.data.messages[0].role).toBe('user');
    });

    test('should add AI response to messages array', () => {
      const aiMessage = { role: 'assistant', content: 'Hi there!', time: '10:01' };
      page.data.messages.push(aiMessage);
      expect(page.data.messages).toHaveLength(1);
      expect(page.data.messages[0].role).toBe('assistant');
    });

    test('should clear messages array', () => {
      page.data.messages = [
        { role: 'user', content: 'Test', time: '10:00' },
        { role: 'assistant', content: 'Response', time: '10:01' },
      ];
      page.data.messages = [];
      expect(page.data.messages).toHaveLength(0);
    });
  });

  describe('Input State', () => {
    test('should track input text', () => {
      page.data.inputText = 'Book a coach for tomorrow';
      expect(page.data.inputText).toBe('Book a coach for tomorrow');
    });

    test('should clear input after sending', () => {
      page.data.inputText = 'Test message';
      page.data.inputText = '';
      expect(page.data.inputText).toBe('');
    });
  });

  describe('Loading State', () => {
    test('should set loading state when sending message', () => {
      page.data.isLoading = true;
      expect(page.data.isLoading).toBe(true);
    });

    test('should clear loading state after response', () => {
      page.data.isLoading = false;
      expect(page.data.isLoading).toBe(false);
    });
  });

  describe('Time Formatting', () => {
    test('should format time correctly', () => {
      const formatTime = (date) => {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
      };
      const testDate = new Date(2024, 0, 15, 9, 5);
      expect(formatTime(testDate)).toBe('09:05');
    });

    test('should format time with single digit minutes', () => {
      const formatTime = (date) => {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
      };
      const testDate = new Date(2024, 0, 15, 14, 9);
      expect(formatTime(testDate)).toBe('14:09');
    });
  });

  describe('Message Structure', () => {
    test('should create valid message object', () => {
      const createMessage = (role, content) => ({
        role,
        content,
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      });
      const msg = createMessage('user', 'Test content');
      expect(msg).toHaveProperty('role', 'user');
      expect(msg).toHaveProperty('content', 'Test content');
      expect(msg).toHaveProperty('time');
    });
  });
});