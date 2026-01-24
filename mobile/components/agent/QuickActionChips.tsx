import React from 'react';
import { ScrollView, TouchableOpacity, Text } from 'react-native';

interface QuickActionChipsProps {
  onSelect: (action: string) => void;
  disabled?: boolean;
  suggestions?: string[];
}

const DEFAULT_ACTIONS = [
  'Check status',
  'Pending approvals',
  'What\'s urgent?',
  'Help',
];

export function QuickActionChips({ onSelect, disabled, suggestions }: QuickActionChipsProps) {
  const actions = suggestions && suggestions.length > 0 ? suggestions : DEFAULT_ACTIONS;

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      className="py-2 flex-grow-0"
      contentContainerStyle={{ paddingHorizontal: 16 }}
    >
      {actions.map((action, index) => (
        <TouchableOpacity
          key={`${action}-${index}`}
          onPress={() => onSelect(action)}
          disabled={disabled}
          className={`px-4 py-2 rounded-full mr-2 border ${
            disabled
              ? 'bg-muted border-border opacity-50'
              : 'bg-primary/10 border-primary/30 active:bg-primary/20'
          }`}
          activeOpacity={0.7}
        >
          <Text className={`text-sm ${disabled ? 'text-muted-foreground' : 'text-primary'}`}>
            {action}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}
