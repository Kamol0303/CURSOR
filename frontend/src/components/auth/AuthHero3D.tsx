"use client";

const CARD_SETS = [
  [
    "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=320&q=80",
    "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=320&q=80",
    "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=320&q=80",
  ],
  [
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=320&q=80",
    "https://images.unsplash.com/photo-1434030216561-bbafb2e79fd4?w=320&q=80",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=320&q=80",
  ],
  [
    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=320&q=80",
    "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=320&q=80",
    "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=320&q=80",
  ],
] as const;

export function AuthHero3D() {
  return (
    <div className="aeline-3d" aria-hidden>
      <div className="aeline-3d__wrap">
        {CARD_SETS.map((cards, groupIndex) => (
          <div key={groupIndex} className={`aeline-3d__group aeline-3d__group--${groupIndex + 1}`}>
            {cards.map((src, i) => (
              <div key={src} className={`aeline-3d__card aeline-3d__card--${i}`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} alt="" className="aeline-3d__img" loading="lazy" />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
