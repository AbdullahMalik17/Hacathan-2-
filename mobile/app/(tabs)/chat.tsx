import React, { useState, useRef, useEffect } from 'react';
import { View, FlatList, KeyboardAvoidingView, Platform, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AgentMessage } from '../../components/agent/AgentMessage';
import { ChatInput } from '../../components/agent/ChatInput';
import { QuickActionChips } from '../../components/agent/QuickActionChips';
import { AgentTypingIndicator } from '../../components/agent/AgentTypingIndicator';
import { AgentAvatar } from '../../components/agent/AgentAvatar';
import { apiService } from '../../services/api';
import { useToast } from '../../context/ToastContext';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
  suggestions?: string[];
}

export default function ChatScreen() {
  const { showToast } = useToast();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m **Abdullah Junior**, your AI assistant. How can I help you today?\n\nTry asking me about:\n- System status\n- Pending approvals\n- Creating tasks\n- Scheduling content',
      isUser: false,
      timestamp: new Date().toISOString(),
      suggestions: ['Check status', 'Pending approvals', 'Help'],
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [currentSuggestions, setCurrentSuggestions] = useState<string[]>([
    'Check status',
    'Pending approvals',
    'What\'s urgent?',
    'Help',
  ]);
  const [isConnected, setIsConnected] = useState(true);
  const flatListRef = useRef<FlatList>(null);

  // Check connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      await apiService.health();
      setIsConnected(true);
    } catch {
      setIsConnected(false);
    }
  };

  const handleSend = async (text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      // Call real API
      const response = await apiService.sendChatMessage(text);

      const agentMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        isUser: false,
        timestamp: response.data.timestamp || new Date().toISOString(),
        suggestions: response.data.suggestions,
      };

      setMessages((prev) => [...prev, agentMsg]);

      // Update suggestions if provided
      if (response.data.suggestions && response.data.suggestions.length > 0) {
        setCurrentSuggestions(response.data.suggestions);
      }

      // Show toast for actions
      if (response.data.action_taken === 'task_created') {
        showToast('Task created successfully!', 'success');
      }

      setIsConnected(true);
    } catch (error: any) {
      console.error('Chat error:', error);

      // Show offline/error message
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: isConnected
          ? 'Sorry, I encountered an error processing your request. Please try again.'
          : 'I\'m currently offline. Please check your connection and try again.',
        isUser: false,
        timestamp: new Date().toISOString(),
        suggestions: ['Retry', 'Check status'],
      };

      setMessages((prev) => [...prev, errorMsg]);
      setCurrentSuggestions(['Retry', 'Check status', 'Help']);

      if (error.message?.includes('Network') || error.code === 'ERR_NETWORK') {
        setIsConnected(false);
        showToast('Connection lost. Check your network.', 'error');
      }
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickAction = (action: string) => {
    handleSend(action);
  };

  return (
    <SafeAreaView className="flex-1 bg-background" edges={['top']}>
      {/* Header */}
      <View className="flex-row items-center justify-center p-3 border-b border-border bg-card/50">
        <AgentAvatar size="sm" status={isTyping ? 'typing' : isConnected ? 'online' : 'offline'} />
        <View className="ml-3">
          <Text className="text-foreground font-semibold">Abdullah Junior</Text>
          <Text className="text-muted-foreground text-xs">
            {isTyping ? 'Typing...' : isConnected ? 'Online' : 'Offline'}
          </Text>
        </View>
      </View>

      {/* Connection Warning */}
      {!isConnected && (
        <View className="bg-destructive/20 px-4 py-2">
          <Text className="text-destructive text-center text-sm">
            Offline - Some features may be unavailable
          </Text>
        </View>
      )}

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        className="flex-1"
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <AgentMessage
              message={item.text}
              isUser={item.isUser}
              timestamp={item.timestamp}
            />
          )}
          contentContainerStyle={{ padding: 16, paddingBottom: 8 }}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          ListFooterComponent={
            isTyping ? (
              <View className="ml-2 mb-4">
                <AgentTypingIndicator />
              </View>
            ) : null
          }
        />

        <View className="border-t border-border bg-card/30">
          <QuickActionChips
            onSelect={handleQuickAction}
            disabled={isTyping}
            suggestions={currentSuggestions}
          />
          <ChatInput onSend={handleSend} disabled={isTyping} />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
