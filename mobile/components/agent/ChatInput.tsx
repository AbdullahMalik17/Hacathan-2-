import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity } from 'react-native';
import { Send, Mic } from 'lucide-react-native';
import { cn } from '../../utils/cn';

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
    }
  };

  return (
    <View className="flex-row items-center p-3 bg-card border-t border-border">
      <View className="flex-1 flex-row items-center bg-secondary rounded-full px-4 py-2 mr-2">
        <TextInput
          className="flex-1 text-foreground max-h-24 text-base"
          placeholder="Message Abdullah Junior..."
          placeholderTextColor="#94A3B8"
          value={text}
          onChangeText={setText}
          multiline
          maxLength={500}
          editable={!disabled}
        />
      </View>
      <TouchableOpacity
        onPress={handleSend}
        disabled={!text.trim() || disabled}
        className={cn(
          'h-10 w-10 rounded-full items-center justify-center',
          text.trim() && !disabled ? 'bg-primary' : 'bg-secondary'
        )}
      >
        {text.trim() ? (
          <Send size={20} color="white" />
        ) : (
          <Mic size={20} color="#94A3B8" />
        )}
      </TouchableOpacity>
    </View>
  );
}
