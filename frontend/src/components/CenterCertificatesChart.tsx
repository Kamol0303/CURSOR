"use client";

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
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-naqsh-primary">{title}</h3>
        <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
      </div>
      {top.length === 0 ? (
        <p className="text-gray-400 text-sm py-8 text-center">—</p>
      ) : (
        <div className="space-y-3">
          {top.map((item) => (
            <div key={item.center_id} className="group">
              <div className="flex justify-between text-sm mb-1 gap-2">
                <span className="font-medium text-gray-700 truncate" title={item.center_name}>
                  {item.center_name}
                </span>
                <span className="text-naqsh-primary font-semibold shrink-0">
                  {item.certificate_count}
                </span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
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
          className="inline-block mt-4 text-sm font-medium text-naqsh-accent hover:text-naqsh-primary"
        >
          {viewAllLabel}
        </a>
      )}
    </div>
  );
}
