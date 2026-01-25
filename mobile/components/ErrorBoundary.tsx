import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <View className="flex-1 bg-background p-6 justify-center">
          <Text className="text-2xl font-bold text-foreground mb-4">
            Something went wrong
          </Text>
          <ScrollView className="flex-1 bg-muted p-4 rounded-lg mb-4">
            <Text className="text-sm font-mono text-foreground">
              {this.state.error?.message}
            </Text>
            <Text className="text-xs font-mono text-muted-foreground mt-2">
              {this.state.error?.stack}
            </Text>
          </ScrollView>
          <TouchableOpacity
            className="bg-primary p-4 rounded-lg"
            onPress={() => this.setState({ hasError: false, error: null })}
          >
            <Text className="text-primary-foreground text-center font-semibold">
              Try Again
            </Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}
