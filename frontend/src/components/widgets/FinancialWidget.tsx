'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign } from 'lucide-react';

interface FinancialData {
  revenue: number;
  expenses: number;
  profit: number;
  margin: number;
}

export default function FinancialWidget({ data }: { data: FinancialData | null }) {
  // Use data or fallback to zero/placeholder
  const financials = data || {
    revenue: 0,
    expenses: 0,
    profit: 0,
    margin: 0
  };

  return (
    <Card className="bg-zinc-900/50 border-zinc-800">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400">
          Financial Health (Odoo)
        </CardTitle>
        <DollarSign className="h-4 w-4 text-green-500" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white mb-4">
          ${financials.revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          <span className="text-xs font-normal text-zinc-500 ml-2">Revenue MTD</span>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-zinc-500">Expenses</p>
            <p className="text-sm font-semibold text-red-400">
              -${financials.expenses.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-zinc-500">Net Profit</p>
            <p className="text-sm font-semibold text-green-400">
              +${financials.profit.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-zinc-800 flex justify-between items-center text-xs">
          <Badge variant="outline" className="text-blue-400 border-blue-400/20 bg-blue-400/10">
            {data ? "Live Data" : "No Data"}
          </Badge>
          <span className="text-zinc-500">{financials.margin}% Margin</span>
        </div>
      </CardContent>
    </Card>
  );
}
