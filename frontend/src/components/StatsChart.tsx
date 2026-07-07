"use client";

type Point = { label: string; value: number };

export function StatsChart({ title, data }: { title: string; data: Point[] }) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200/80 dark:border-gray-800 shadow-sm p-4 sm:p-5 hover:shadow-md transition-shadow duration-200">
      <h3 className="text-sm font-semibold text-naqsh-primary dark:text-naqsh-accent mb-4">{title}</h3>
      <div className="flex items-end gap-1.5 h-28 sm:h-32">
        {data.map((point) => (
          <div key={point.label} className="flex-1 flex flex-col items-center gap-1 min-w-0">
            <div
              className="w-full bg-gradient-to-t from-naqsh-primary to-naqsh-accent/90 dark:from-naqsh-primary dark:to-naqsh-accent rounded-t-sm transition-all duration-200"
              style={{ height: `${(point.value / max) * 100}%`, minHeight: point.value > 0 ? 4 : 0 }}
              title={`${point.label}: ${point.value}`}
            />
            <span className="text-[9px] sm:text-[10px] text-gray-500 dark:text-gray-400 truncate w-full text-center">
              {point.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
