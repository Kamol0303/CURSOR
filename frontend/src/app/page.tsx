import { redirect } from '@/i18n/routing';

export default function RootPage() {
  redirect({ href: '/login', locale: 'uz' });
}
