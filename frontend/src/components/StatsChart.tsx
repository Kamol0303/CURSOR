"use client";

import { Card, CardBody, CardTitle } from "@/components/ui";

type Point = { label: string; value: number };

export function StatsChart({ title, data }: { title: string; data: Point[] }) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <Card hover className="h-full">
      <CardBody>
        <CardTitle className="text-naqsh-primary dark:text-naqsh-accent mb-4">{title}</CardTitle>
        <div className="flex items-end gap-1.5 h-28 sm:h-32">
          {data.map((point) => (
            <div key={point.label} className="flex-1 flex flex-col items-center gap-1.5 min-w-0">
              <div
                className="w-full bg-gradient-to-t from-naqsh-primary to-naqsh-accent/90 rounded-t-md transition-all duration-slow ease-out group-hover:opacity-90"
                style={{ height: `${(point.value / max) * 100}%`, minHeight: point.value > 0 ? 4 : 0 }}
                title={`${point.label}: ${point.value}`}
                role="img"
                aria-label={`${point.label}: ${point.value}`}
              />
              <span className="text-[9px] sm:text-caption text-muted-foreground truncate w-full text-center">
                {point.label}
              </span>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
