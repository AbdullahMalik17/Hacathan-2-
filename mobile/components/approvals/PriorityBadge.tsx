import { Badge } from '../ui/Badge';

interface PriorityBadgeProps {
  priority: 'low' | 'medium' | 'high' | 'urgent';
  className?: string;
}

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  const variants = {
    low: 'secondary' as const,
    medium: 'warning' as const,
    high: 'destructive' as const,
    urgent: 'destructive' as const,
  };

  const labels = {
    low: 'Low Priority',
    medium: 'Medium Priority',
    high: 'High Priority',
    urgent: 'URGENT',
  };

  return (
    <Badge variant={variants[priority]} className={className}>
      {labels[priority]}
    </Badge>
  );
}
