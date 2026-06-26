<<<<<<< HEAD
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
=======
import { getRequestConfig } from "next-intl/server";
import { cookies } from "next/headers";

export const locales = ["uz", "ru", "en"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "uz";

export default getRequestConfig(async () => {
  const cookieStore = cookies();
  const locale = (cookieStore.get("NEXT_LOCALE")?.value as Locale) || defaultLocale;
  const resolved = locales.includes(locale) ? locale : defaultLocale;

  return {
    locale: resolved,
    messages: (await import(`../messages/${resolved}.json`)).default,
>>>>>>> main
  };
});
