"use client";

import Link from "next/link";

function SplitCurve() {
  return (
    <svg
      className="aeline-split-login__curve"
      width="67"
      height="578"
      viewBox="0 0 67 578"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        d="M11.3847656,-5.68434189e-14 C-7.44726562,36.7213542 5.14322917,126.757812 49.15625,270.109375 C70.9827986,341.199016 54.8877465,443.829224 0.87109375,578 L67,578 L67,-5.68434189e-14 L11.3847656,-5.68434189e-14 Z"
        fill="#F9BC35"
      />
    </svg>
  );
}

export function AuthSplitLoginCard({
  children,
  welcomeTitle,
  welcomeSubtitle,
  sideHref,
  sideLabel,
}: {
  children: React.ReactNode;
  welcomeTitle: string;
  welcomeSubtitle: string;
  sideHref?: string;
  sideLabel?: string;
}) {
  return (
    <div id="login" className="aeline-split-login">
      <div className="aeline-split-login__body">
        <div className="aeline-split-login__main">{children}</div>
        <SplitCurve />
        <aside className="aeline-split-login__side">
          <div className="aeline-split-login__side-content">
            <h2>{welcomeTitle}</h2>
            <p>{welcomeSubtitle}</p>
            {sideHref && sideLabel && (
              <Link href={sideHref} className="aeline-split-login__side-btn">
                {sideLabel}
              </Link>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
