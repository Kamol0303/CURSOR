'use client';

import { GirihPattern } from '@/components/ui/GirihPattern';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import { TamorLogo } from '@/components/ui/GirihPattern';

export default function VerifyPage() {
  return (
    <div className="relative min-h-screen flex items-center justify-center">
      <GirihPattern opacity={0.05} />
      <div className="absolute top-4 right-4 z-10">
        <LanguageSwitcher />
      </div>
      <div className="relative z-10 card p-8 max-w-md w-full mx-4 text-center">
        <TamorLogo size={48} />
        <h1 className="mt-4 text-xl font-bold">Certificate Verification</h1>
        <p className="mt-2 text-sm text-[var(--muted-foreground)]">
          Public certificate verification — Phase 2 implementation
        </p>
      </div>
    </div>
  );
}
