import authEn from '@/messages/en/auth.json';
import commonEn from '@/messages/en/common.json';
import dashboardEn from '@/messages/en/dashboard.json';
import authRu from '@/messages/ru/auth.json';
import commonRu from '@/messages/ru/common.json';
import dashboardRu from '@/messages/ru/dashboard.json';
import authUz from '@/messages/uz/auth.json';
import commonUz from '@/messages/uz/common.json';
import dashboardUz from '@/messages/uz/dashboard.json';

const catalog = {
  uz: {
    auth: authUz,
    common: commonUz,
    dashboard: dashboardUz
  },
  ru: {
    auth: authRu,
    common: commonRu,
    dashboard: dashboardRu
  },
  en: {
    auth: authEn,
    common: commonEn,
    dashboard: dashboardEn
  }
} as const;

export function getMessages(locale: 'uz' | 'ru' | 'en') {
  return catalog[locale];
}
