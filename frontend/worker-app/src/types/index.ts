// Type definitions

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface Order {
  id: string;
  pickup: string;
  dropoff: string;
  eta: number;
  g_mean?: number;
  g_var?: number;
  status: 'pending' | 'in-progress' | 'completed';
  createdAt: string;
}

export interface CompletedJob {
  id: string;
  pickup: string;
  dropoff: string;
  earnings: number;
  completedAt: string;
  g_mean?: number;
}

export interface Earnings {
  totalEarnings: number;
  completedJobs: CompletedJob[];
  period?: string;
}
