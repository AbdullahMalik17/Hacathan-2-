import React from 'react';
import { View, Text } from 'react-native';
import { AgentAvatar } from './AgentAvatar';
import { cn } from '../../utils/cn';

interface AgentMessageProps {
  message: string;
  isUser: boolean;
  timestamp: string;
}

export function AgentMessage({ message, isUser, timestamp }: AgentMessageProps) {
  return (
    <View
      className={cn(
        'flex-row mb-4 w-full',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      {!isUser && <AgentAvatar size="sm" className="mr-2 self-end mb-1" />}
      
      <View
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-3',
          isUser
            ? 'bg-primary rounded-br-none'
            : 'bg-secondary rounded-bl-none'
        )}
      >
        <Text
          className={cn(
            'text-base leading-5',
            isUser ? 'text-primary-foreground' : 'text-foreground'
          )}
        >
          {message}
        </Text>
        <Text
          className={cn(
            'text-[10px] mt-1 opacity-70',
            isUser ? 'text-primary-foreground text-right' : 'text-muted-foreground'
          )}
        >
          {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </View>
  );
}
