"use client";

import { Card, CardBody, CardDescription, CardTitle, EmptyState } from "@/components/ui";

type Point = { label: string; value: number; is_forecast?: boolean };

export function TrendLineChart({
  title,
  subtitle,
  data,
  forecastLabel,
}: {
  title: string;
  subtitle: string;
  data: Point[];
  forecastLabel: string;
}) {
  if (data.length === 0) {
    return (
      <Card>
        <CardBody>
          <CardTitle>{title}</CardTitle>
          <EmptyState title="—" className="py-8" />
        </CardBody>
      </Card>
    );
  }

  const width = 640;
  const height = 220;
  const pad = { top: 16, right: 16, bottom: 36, left: 40 };
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;
  const max = Math.max(...data.map((d) => d.value), 1);
  const firstForecast = data.findIndex((d) => d.is_forecast);
  const actual = firstForecast === -1 ? data : data.slice(0, firstForecast);
  const forecast = firstForecast === -1 ? [] : data.slice(firstForecast - 1);

  const toX = (i: number) => pad.left + (i / Math.max(data.length - 1, 1)) * innerW;
  const toY = (v: number) => pad.top + innerH - (v / max) * innerH;

  const linePath = (points: Point[], startIndex: number) =>
    points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${toX(startIndex + i)} ${toY(p.value)}`)
      .join(" ");

  const actualPath = linePath(actual, 0);
  const forecastPath =
    forecast.length > 1 ? linePath(forecast, firstForecast === -1 ? 0 : firstForecast - 1) : "";

  return (
    <Card>
      <CardBody>
        <CardTitle>{title}</CardTitle>
        <CardDescription className="mb-4">{subtitle}</CardDescription>
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto" role="img">
          {[0, 0.25, 0.5, 0.75, 1].map((t) => {
            const y = pad.top + innerH * (1 - t);
            const val = Math.round(max * t);
            return (
              <g key={t}>
                <line x1={pad.left} y1={y} x2={width - pad.right} y2={y} className="stroke-border" />
                <text x={pad.left - 6} y={y + 4} textAnchor="end" className="fill-muted-foreground text-[10px]">
                  {val}
                </text>
              </g>
            );
          })}
          {actualPath && (
            <path d={actualPath} fill="none" stroke="currentColor" className="text-naqsh-primary" strokeWidth={2.5} strokeLinecap="round" />
          )}
          {forecastPath && (
            <path
              d={forecastPath}
              fill="none"
              stroke="currentColor"
              className="text-naqsh-primary"
              strokeWidth={2}
              strokeDasharray="6 4"
              opacity={0.75}
            />
          )}
          {data.map((p, i) => (
            <circle
              key={`${p.label}-${i}`}
              cx={toX(i)}
              cy={toY(p.value)}
              r={p.is_forecast ? 3 : 4}
              className={p.is_forecast ? "fill-card stroke-naqsh-primary" : "fill-naqsh-primary stroke-naqsh-primary"}
              strokeWidth={2}
            >
              <title>
                {p.label}: {p.value}
                {p.is_forecast ? ` (${forecastLabel})` : ""}
              </title>
            </circle>
          ))}
          {data.map((p, i) =>
            i % Math.ceil(data.length / 6) === 0 || i === data.length - 1 ? (
              <text
                key={`lbl-${p.label}`}
                x={toX(i)}
                y={height - 8}
                textAnchor="middle"
                className="fill-muted-foreground text-[9px]"
              >
                {p.label.slice(2)}
              </text>
            ) : null,
          )}
        </svg>
        {firstForecast !== -1 && (
          <p className="text-caption text-muted-foreground mt-2 flex items-center gap-2">
            <span className="inline-block w-8 border-t-2 border-dashed border-naqsh-primary" />
            {forecastLabel}
          </p>
        )}
      </CardBody>
    </Card>
  );
}
