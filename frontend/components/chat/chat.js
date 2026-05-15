Component({
  properties: {
    initialMessage: {
      type: String,
      value: ''
    }
  },

  data: {
    messages: [],
    inputValue: '',
    isLoading: false,
    isRecording: false,
    recordingDuration: 0,
    quickReplies: [],
    showQuickReplies: true,
    contextIntent: null
  },

  lifetimes: {
    attached() {
      this.initChat();
      this.generateWelcomeMessage();
    }
  },

  methods: {
    initChat() {
      const app = getApp();
      const context = app.globalData.conversationContext;

      if (context && context.messages && context.messages.length > 0) {
        this.setData({ messages: context.messages });

        if (context.intent) {
          this.setData({
            contextIntent: context.intent,
            showQuickReplies: false
          });
        }
      }

      this.setData({
        quickReplies: [
          { id: 'book', text: '📅 预约训练' },
          { id: 'coach', text: '🏃 查看教练' },
          { id: 'schedule', text: '📋 我的日程' },
          { id: 'feedback', text: '💬 训练反馈' }
        ]
      });
    },

    generateWelcomeMessage() {
      const app = getApp();
      const welcomeMsg = app.generateWelcomeMessage();

      const welcomeMessage = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: welcomeMsg,
        timestamp: Date.now()
      };

      this.addMessage(welcomeMessage);
    },

    addMessage(message) {
      const messages = [...this.data.messages, message];
      this.setData({ messages });

      this.updateContext();
    },

    updateContext() {
      const app = getApp();
      const lastMessage = this.data.messages[this.data.messages.length - 1];

      app.globalData.conversationContext = {
        messages: this.data.messages,
        intent: this.data.contextIntent,
        entities: {},
        lastUpdated: Date.now()
      };

      app.saveConversationContext();
    },

    onInputFocus() {
      this.setData({ showQuickReplies: false });
    },

    onInputBlur() {
      if (!this.data.inputValue) {
        this.setData({ showQuickReplies: true });
      }
    },

    onInputChange(e) {
      this.setData({ inputValue: e.detail.value });
    },

    onInputConfirm(e) {
      const value = e.detail.value.trim();
      if (value) {
        this.sendMessage(value);
      }
    },

    onQuickReplyTap(e) {
      const { replyId, replyText } = e.currentTarget.dataset;

      switch (replyId) {
        case 'book':
          this.sendMessage('我想预约训练');
          break;
        case 'coach':
          this.sendMessage('查看教练');
          break;
        case 'schedule':
          this.sendMessage('查看我的日程');
          break;
        case 'feedback':
          this.sendMessage('查看训练反馈');
          break;
        default:
          this.sendMessage(replyText);
      }
    },

    sendMessage(content) {
      if (!content.trim()) return;

      const userMessage = {
        id: `msg_${Date.now()}`,
        role: 'user',
        content: content.trim(),
        timestamp: Date.now()
      };

      this.addMessage(userMessage);
      this.setData({ inputValue: '', isLoading: true, showQuickReplies: false });

      this.processMessage(content);
    },

    processMessage(content) {
      const app = getApp();
      const lowerContent = content.toLowerCase();

      if (lowerContent.includes('预约') || lowerContent.includes('book')) {
        this.setData({ contextIntent: 'booking' });
        this.handleBookingIntent(content);
      } else if (lowerContent.includes('教练') || lowerContent.includes('coach')) {
        this.setData({ contextIntent: 'coach_list' });
        this.handleCoachListIntent(content);
      } else if (lowerContent.includes('日程') || lowerContent.includes('schedule')) {
        this.setData({ contextIntent: 'schedule' });
        this.handleScheduleIntent(content);
      } else if (lowerContent.includes('反馈') || lowerContent.includes('feedback')) {
        this.setData({ contextIntent: 'feedback' });
        this.handleFeedbackIntent(content);
      } else {
        this.sendToAI(content);
      }
    },

    handleBookingIntent(content) {
      const lowerContent = content.toLowerCase();

      if (lowerContent.includes('取消') || lowerContent.includes('cancel')) {
        this.addTypingIndicator();
        setTimeout(() => {
          this.removeTypingIndicator();
          this.addMessage({
            id: `msg_${Date.now()}`,
            role: 'assistant',
            content: '好的，要取消预约的话，请先告诉我您的预约日期或者直接去"我的日程"页面操作。',
            timestamp: Date.now()
          });
          this.setData({ isLoading: false });
        }, 1000);
      } else if (lowerContent.includes('改') || lowerContent.includes('change')) {
        this.addTypingIndicator();
        setTimeout(() => {
          this.removeTypingIndicator();
          this.addMessage({
            id: `msg_${Date.now()}`,
            role: 'assistant',
            content: '好的，要修改预约请告诉我您想改到哪一天和时间。',
            timestamp: Date.now()
          });
          this.setData({ isLoading: false });
        }, 1000);
      } else {
        this.addTypingIndicator();
        app.getRecommendedCoaches().then(coaches => {
          setTimeout(() => {
            this.removeTypingIndicator();
            this.addMessage({
              id: `msg_${Date.now()}`,
              role: 'assistant',
              content: `好的，要预约训练吗？我可以帮您推荐合适的教练。请问您有什么特别的偏好吗？比如：\n\n1. 新手友好型教练\n2. 技术提升型教练\n3. 耐力训练教练`,
              timestamp: Date.now(),
              suggestions: [
                { id: 'beginner', text: '新手友好' },
                { id: 'advanced', text: '进阶专业' },
                { id: 'any', text: '都可以' }
              ]
            });
            this.setData({ isLoading: false, showQuickReplies: true });
          }, 1500);
        }).catch(() => {
          this.removeTypingIndicator();
          this.addMessage({
            id: `msg_${Date.now()}`,
            role: 'assistant',
            content: '好的，要预约训练请告诉我您想预约哪位教练，以及preferred的时间。',
            timestamp: Date.now()
          });
          this.setData({ isLoading: false });
        });
      }
    },

    handleCoachListIntent(content) {
      this.addTypingIndicator();
      setTimeout(() => {
        this.removeTypingIndicator();
        this.addMessage({
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: '好的，让我为您展示我们的教练团队。您可以查看每位教练的专长和用户评价。',
          timestamp: Date.now(),
          action: { type: 'navigate', path: '/pages/coach-list/coach-list' }
        });
        this.setData({ isLoading: false });
      }, 1000);
    },

    handleScheduleIntent(content) {
      this.addTypingIndicator();
      setTimeout(() => {
        this.removeTypingIndicator();
        this.addMessage({
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: '好的，让我查看您的日程安排。',
          timestamp: Date.now(),
          action: { type: 'navigate', path: '/pages/schedule/schedule' }
        });
        this.setData({ isLoading: false });
      }, 1000);
    },

    handleFeedbackIntent(content) {
      this.addTypingIndicator();
      setTimeout(() => {
        this.removeTypingIndicator();
        this.addMessage({
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: '好的，让我查看您的训练反馈记录。',
          timestamp: Date.now(),
          action: { type: 'navigate', path: '/pages/feedback/feedback' }
        });
        this.setData({ isLoading: false });
      }, 1000);
    },

    sendToAI(content) {
      const app = getApp();

      app.sendAIMessage(content).then(response => {
        this.removeTypingIndicator();
        this.addMessage({
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: response.message,
          timestamp: Date.now(),
          suggestions: response.suggestions
        });
        this.setData({ isLoading: false });
      }).catch(() => {
        this.removeTypingIndicator();
        this.addMessage({
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: '抱歉，AI服务暂时不可用，请稍后再试。',
          timestamp: Date.now()
        });
        this.setData({ isLoading: false });
      });
    },

    addTypingIndicator() {
      const typingMessage = {
        id: 'typing',
        role: 'assistant',
        content: '...',
        isTyping: true,
        timestamp: Date.now()
      };
      this.addMessage(typingMessage);
    },

    removeTypingIndicator() {
      const messages = this.data.messages.filter(m => !m.isTyping);
      this.setData({ messages });
    },

    onSuggestionTap(e) {
      const { suggestionText } = e.currentTarget.dataset;
      if (suggestionText) {
        this.sendMessage(suggestionText);
      }
    },

    onActionTap(e) {
      const { actionType, actionPath } = e.currentTarget.dataset;
      if (actionType === 'navigate' && actionPath) {
        wx.switchTab({ url: actionPath });
      }
    },

    onVoiceRecord() {
      if (this.data.isRecording) {
        this.stopRecording();
      } else {
        this.startRecording();
      }
    },

    startRecording() {
      wx.startRecord({
        success: () => {
          this.setData({ isRecording: true, recordingDuration: 0 });

          this.recordingTimer = setInterval(() => {
            this.setData({
              recordingDuration: this.data.recordingDuration + 1
            });
          }, 1000);
        },
        fail: () => {
          wx.showToast({
            title: '语音功能暂不可用',
            icon: 'none'
          });
        }
      });
    },

    stopRecording() {
      wx.stopRecord();
      clearInterval(this.recordingTimer);

      this.setData({
        isRecording: false,
        recordingDuration: 0
      });

      setTimeout(() => {
        this.addMessage({
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: '语音识别功能开发中，请先使用文字输入。',
          timestamp: Date.now()
        });
        this.setData({ isLoading: false });
      }, 500);
    },

    onClose() {
      this.triggerEvent('close');
    },

    onScrollToBottom() {
      this.setData({ scrollTop: 9999 });
    }
  },

  detached() {
    if (this.recordingTimer) {
      clearInterval(this.recordingTimer);
    }
  }
});