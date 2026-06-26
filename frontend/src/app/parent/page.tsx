import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages } from "next-intl/server";
import { ParentLoginForm } from "@/components/ParentLoginForm";

export default async function ParentLoginPage() {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      <ParentLoginForm />
    </NextIntlClientProvider>
  );
}
