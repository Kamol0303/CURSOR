type MetricCardProps = {
  label: string;
  value: string;
  delta: string;
};

export function MetricCard({label, value, delta}: MetricCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_18px_48px_rgba(15,30,24,0.12)] dark:border-slate-800 dark:bg-slate-950">
      <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <div className="mt-3 flex items-end justify-between">
        <h3 className="text-3xl font-semibold text-[var(--foreground)] dark:text-white">{value}</h3>
        <span className="rounded-full bg-[rgba(27,77,62,0.1)] px-3 py-1 text-xs font-semibold text-[var(--color-naqsh-primary)]">{delta}</span>
      </div>
    </div>
  );
}
