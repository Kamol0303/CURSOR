"use client";

type Point = { label: string; value: number };

export function StatsChart({ title, data }: { title: string; data: Point[] }) {
  const max = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="bg-white rounded-xl border p-5">
      <h3 className="font-semibold text-naqsh-primary mb-4">{title}</h3>
      <div className="flex items-end gap-2 h-32">
        {data.map((point) => (
          <div key={point.label} className="flex-1 flex flex-col items-center gap-1">
            <div
              className="w-full bg-naqsh-accent/80 rounded-t"
              style={{ height: `${(point.value / max) * 100}%`, minHeight: point.value > 0 ? 4 : 0 }}
              title={`${point.label}: ${point.value}`}
            />
            <span className="text-[10px] text-gray-500 truncate w-full text-center">{point.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
