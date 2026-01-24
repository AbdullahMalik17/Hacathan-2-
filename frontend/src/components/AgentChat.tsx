'use client';

import { useState } from 'react';
import { submitTask } from '@/app/actions';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function AgentChat() {
  const [input, setInput] = useState('');
  const [priority, setPriority] = useState('medium');
  const [sending, setSending] = useState(false);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setSending(true);
    
    const formData = new FormData();
    formData.set('title', 'Quick Command');
    formData.set('content', input);
    formData.set('priority', priority);
    
    await submitTask(formData);
    
    setInput('');
    setSending(false);
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-zinc-100">Command Input</h3>
        <Select value={priority} onValueChange={setPriority}>
          <SelectTrigger className="w-[120px] h-8 bg-zinc-800 border-zinc-700">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="low">Low Priority</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="high">High Priority</SelectItem>
            <SelectItem value="urgent">Urgent 🚨</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="relative">
        <Textarea 
          placeholder="Ask Abdullah Junior to do something..."
          className="bg-black/50 border-zinc-700 min-h-[100px] resize-none pr-4"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
        />
        <div className="absolute bottom-2 right-2">
          <span className="text-xs text-zinc-500">Press Enter to send</span>
        </div>
      </div>

      <div className="flex justify-end">
        <Button 
          onClick={handleSubmit} 
          disabled={sending}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {sending ? 'Sending...' : 'Transmit Order'}
        </Button>
      </div>
    </div>
  );
}
