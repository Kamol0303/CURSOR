import createMiddleware from 'next-intl/middleware';
import { defaultLocale, locales } from './i18n/config';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'never',
  localeDetection: false,
});

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
