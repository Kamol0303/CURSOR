import { redirect } from '@/i18n/routing';

export default async function LocaleHomePage({
  params,
}: {
  params: Promise<{ locale: 'uz' | 'ru' | 'en' }>;
}) {
  const { locale } = await params;
  redirect({ href: '/login', locale });
}
