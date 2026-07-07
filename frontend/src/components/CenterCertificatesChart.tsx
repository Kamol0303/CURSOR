"use client";

import { Card, CardBody, CardDescription, CardTitle, EmptyState } from "@/components/ui";

type BarItem = { center_id: string; center_name: string; certificate_count: number };

export function CenterCertificatesChart({
  title,
  subtitle,
  data,
  viewAllHref,
  viewAllLabel,
}: {
  title: string;
  subtitle: string;
  data: BarItem[];
  viewAllHref?: string;
  viewAllLabel?: string;
}) {
  const top = data.slice(0, 10);
  const max = Math.max(...top.map((d) => d.certificate_count), 1);

  return (
    <Card>
      <CardBody>
        <CardTitle>{title}</CardTitle>
        <CardDescription className="mb-6">{subtitle}</CardDescription>
        {top.length === 0 ? (
          <EmptyState title="—" className="py-8" />
        ) : (
          <div className="space-y-3">
            {top.map((item) => (
              <div key={item.center_id} className="group">
                <div className="flex justify-between text-small mb-1 gap-2">
                  <span className="font-medium text-foreground truncate" title={item.center_name}>
                    {item.center_name}
                  </span>
                  <span className="text-naqsh-primary font-semibold shrink-0">
                    {item.certificate_count}
                  </span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-naqsh-accent rounded-full transition-all group-hover:bg-naqsh-primary"
                    style={{ width: `${(item.certificate_count / max) * 100}%` }}
                    title={`${item.center_name}: ${item.certificate_count}`}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
        {data.length > 10 && viewAllHref && viewAllLabel && (
          <a
            href={viewAllHref}
            className="inline-block mt-4 text-small font-medium text-naqsh-accent hover:text-naqsh-primary transition-colors"
          >
            {viewAllLabel}
          </a>
        )}
      </CardBody>
    </Card>
  );
}
