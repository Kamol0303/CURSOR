"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Button, Card, CardBody } from "@/components/ui";

export default function NotFoundPage() {
  const t = useTranslations("notFoundPage");

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <Card className="max-w-lg w-full">
        <CardBody className="text-center py-10 px-6">
          <p className="text-5xl font-bold text-naqsh-primary">404</p>
          <h1 className="text-h3 text-foreground mt-4">{t("title")}</h1>
          <p className="text-small text-muted-foreground mt-2">{t("message")}</p>
          <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/">
              <Button>{t("staffLogin")}</Button>
            </Link>
            <Link href="/parent/login">
              <Button variant="secondary">{t("parentLogin")}</Button>
            </Link>
            <Link href="/verify">
              <Button variant="secondary">{t("verify")}</Button>
            </Link>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
