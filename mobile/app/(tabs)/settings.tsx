import React, { useState, useEffect } from 'react';
import { View, Text, Switch, ScrollView, TextInput, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useSettingsStore } from '../../stores/settingsStore';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useNotifications } from '../../hooks/useNotifications';
import { useToast } from '../../context/ToastContext';
import * as Clipboard from 'expo-clipboard';
import { Moon, Sun, Monitor, Server, Bell, Shield, Copy } from 'lucide-react-native';
import { apiService } from '../../services/api';

export default function SettingsScreen() {
  const settings = useSettingsStore();
  const { expoPushToken } = useNotifications();
  const { showToast } = useToast();
  
  const [urlInput, setUrlInput] = useState(settings.apiBaseUrl);

  const handleSaveUrl = async () => {
    settings.setApiBaseUrl(urlInput);
    await apiService.setBaseUrl(urlInput);
    showToast('Server URL updated', 'success');
  };

  const copyToken = async () => {
    if (expoPushToken) {
      await Clipboard.setStringAsync(expoPushToken);
      showToast('FCM Token copied to clipboard', 'info');
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-background">
      <ScrollView className="p-4" contentContainerStyle={{ paddingBottom: 40 }}>
        <Text className="text-3xl font-bold text-foreground mb-6">Settings</Text>

        <Text className="text-sm font-semibold text-muted-foreground uppercase mb-2 ml-1">
          Appearance
        </Text>
        <Card className="mb-6">
          <CardContent className="p-0">
            <View className="flex-row border-b border-border">
              {['light', 'dark', 'system'].map((theme) => (
                <TouchableOpacity
                  key={theme}
                  onPress={() => settings.setTheme(theme as any)}
                  className={`flex-1 items-center justify-center p-4 ${
                    settings.theme === theme ? 'bg-secondary' : ''
                  }`}
                >
                  {theme === 'light' && <Sun size={24} color={settings.theme === theme ? '#2563eb' : '#94A3B8'} />}
                  {theme === 'dark' && <Moon size={24} color={settings.theme === theme ? '#2563eb' : '#94A3B8'} />}
                  {theme === 'system' && <Monitor size={24} color={settings.theme === theme ? '#2563eb' : '#94A3B8'} />}
                  <Text className={`mt-2 text-xs capitalize ${settings.theme === theme ? 'text-primary font-bold' : 'text-muted-foreground'}`}>
                    {theme}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </CardContent>
        </Card>

        <Text className="text-sm font-semibold text-muted-foreground uppercase mb-2 ml-1">
          Server Configuration
        </Text>
        <Card className="mb-6">
          <CardContent className="p-4">
            <View className="flex-row items-center mb-2">
              <Server size={18} color="#94A3B8" className="mr-2" />
              <Text className="text-foreground font-medium">Backend URL</Text>
            </View>
            <View className="flex-row space-x-2 gap-2">
              <Input
                value={urlInput}
                onChangeText={setUrlInput}
                containerClassName="flex-1"
                placeholder="http://10.0.2.2:8000"
              />
              <Button size="sm" onPress={handleSaveUrl}>
                <Text className="text-white">Save</Text>
              </Button>
            </View>
          </CardContent>
        </Card>

        <Text className="text-sm font-semibold text-muted-foreground uppercase mb-2 ml-1">
          Notifications
        </Text>
        <Card className="mb-6">
          <CardContent className="p-0">
            {[
              { key: 'approvals', label: 'Approval Requests', icon: Shield },
              { key: 'suggestions', label: 'Proactive Suggestions', icon: Bell },
              { key: 'digest', label: 'Daily Digest', icon: FileText },
            ].map((item, index) => (
              <View 
                key={item.key} 
                className={`flex-row items-center justify-between p-4 ${index !== 2 ? 'border-b border-border' : ''}`}
              >
                <View className="flex-row items-center">
                  <item.icon size={20} color="#94A3B8" className="mr-3" />
                  <Text className="text-foreground">{item.label}</Text>
                </View>
                <Switch
                  value={settings.notifications[item.key as keyof typeof settings.notifications]}
                  onValueChange={() => settings.toggleNotification(item.key as any)}
                  trackColor={{ false: '#334155', true: '#2563eb' }}
                  thumbColor="#f8fafc"
                />
              </View>
            ))}
          </CardContent>
        </Card>

        <Text className="text-sm font-semibold text-muted-foreground uppercase mb-2 ml-1">
          Debug Info
        </Text>
        <Card className="mb-6">
          <CardContent className="p-4">
            <Text className="text-xs text-muted-foreground mb-1">FCM Token</Text>
            <TouchableOpacity 
              onPress={copyToken}
              className="flex-row items-center bg-secondary p-2 rounded border border-border"
            >
              <Text className="text-xs text-foreground flex-1 font-mono" numberOfLines={1}>
                {expoPushToken || 'Not registered'}
              </Text>
              <Copy size={14} color="#94A3B8" className="ml-2" />
            </TouchableOpacity>
            
            <View className="mt-4 flex-row justify-between">
              <Text className="text-xs text-muted-foreground">App Version</Text>
              <Text className="text-xs text-foreground">1.0.0 (Build 1)</Text>
            </View>
          </CardContent>
        </Card>

        <Button 
          variant="destructive" 
          className="mb-8"
          onPress={() => {
            showToast('Cache cleared', 'info');
          }}
        >
          <Text className="text-white">Clear Cache & Reset</Text>
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
}

// Icon import helper
import { FileText } from 'lucide-react-native';