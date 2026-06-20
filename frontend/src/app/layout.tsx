import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TaMoR — Education Monitoring & Rating Platform',
  description: 'Toyloq District Education Monitoring and Rating Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return children;
}
