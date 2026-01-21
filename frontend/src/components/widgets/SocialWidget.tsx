'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Facebook, Twitter, Instagram, Linkedin, ArrowUpRight } from 'lucide-react';

const socialStats = [
  { platform: 'LinkedIn', followers: 1240, engagement: '+5.2%', icon: Linkedin, color: 'text-blue-500' },
  { platform: 'Twitter', followers: 850, engagement: '+2.1%', icon: Twitter, color: 'text-sky-400' },
  { platform: 'Instagram', followers: 3200, engagement: '+12%', icon: Instagram, color: 'text-pink-500' },
  { platform: 'Facebook', followers: 1500, engagement: '-0.5%', icon: Facebook, color: 'text-blue-600' },
];

export default function SocialWidget() {
  return (
    <Card className="bg-zinc-900/50 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400">Social Pulse</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {socialStats.map((stat) => (
            <div key={stat.platform} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
                <span className="text-sm text-zinc-300">{stat.platform}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold text-white">{stat.followers}</span>
                <span className={`text-xs ${stat.engagement.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                  {stat.engagement}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
