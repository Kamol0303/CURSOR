import {getRequestConfig} from 'next-intl/server';

import {getMessages} from '@/lib/messages';

import {routing} from './routing';

export default getRequestConfig(async ({requestLocale}) => {
  const locale = (await requestLocale) ?? routing.defaultLocale;
  const resolvedLocale = routing.locales.includes(locale as 'uz' | 'ru' | 'en')
    ? (locale as 'uz' | 'ru' | 'en')
    : routing.defaultLocale;

  return {
    locale: resolvedLocale,
    messages: getMessages(resolvedLocale)
  };
});
