"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Button, Card, CardBody } from "@/components/ui";
import { getRoleFromToken, homePathForRole } from "@/lib/auth-cookie";

export default function ForbiddenPage() {
  const t = useTranslations("forbidden");
  const [home, setHome] = useState("/dashboard");

  useEffect(() => {
    const token = localStorage.getItem("tmb_access_token");
    if (token) {
      setHome(homePathForRole(getRoleFromToken(token)));
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <Card className="max-w-md w-full">
        <CardBody className="text-center py-10">
          <p className="text-5xl font-bold text-naqsh-primary">403</p>
          <h1 className="text-h3 text-foreground mt-4">{t("title")}</h1>
          <p className="text-small text-muted-foreground mt-2">{t("message")}</p>
          <Link href={home}>
            <Button className="mt-8">{t("goHome")}</Button>
          </Link>
        </CardBody>
      </Card>
    </div>
  );
}
