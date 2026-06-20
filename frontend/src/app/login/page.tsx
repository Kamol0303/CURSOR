'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { GirihPattern, TamorLogo } from '@/components/ui/GirihPattern';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import { apiLogin, apiMfaVerify, apiOtpRequest, apiOtpVerify, setAccessToken } from '@/lib/api';

type LoginMode = 'password' | 'otp' | 'mfa';

export default function LoginPage() {
  const t = useTranslations('auth');
  const tc = useTranslations('common');
  const router = useRouter();

  const [mode, setMode] = useState<LoginMode>('password');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('+998');
  const [otpCode, setOtpCode] = useState('');
  const [mfaToken, setMfaToken] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await apiLogin(username, password);
      if (!res.success || !res.data) {
        const code = res.error?.code || 'INVALID_CREDENTIALS';
        setError(t(`errors.${code}` as 'errors.INVALID_CREDENTIALS'));
        return;
      }
      if (res.data.mfa_required && res.data.mfa_token) {
        setMfaToken(res.data.mfa_token);
        setMode('mfa');
        return;
      }
      if (res.data.access_token) {
        setAccessToken(res.data.access_token);
        router.push('/dashboard');
      }
    } catch {
      setError(tc('error'));
    } finally {
      setLoading(false);
    }
  };

  const handleMfaVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await apiMfaVerify(mfaToken, mfaCode);
      if (!res.success || !res.data?.access_token) {
        const code = res.error?.code || 'MFA_INVALID_CODE';
        setError(t(`errors.${code}` as 'errors.MFA_INVALID_CODE'));
        return;
      }
      setAccessToken(res.data.access_token);
      router.push('/dashboard');
    } catch {
      setError(tc('error'));
    } finally {
      setLoading(false);
    }
  };

  const handleOtpRequest = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiOtpRequest(phone);
      if (!res.success) {
        setError(t('errors.OTP_INVALID'));
      }
    } catch {
      setError(tc('error'));
    } finally {
      setLoading(false);
    }
  };

  const handleOtpVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await apiOtpVerify(phone, otpCode);
      if (!res.success || !res.data?.access_token) {
        const code = res.error?.code || 'OTP_INVALID';
        setError(t(`errors.${code}` as 'errors.OTP_INVALID'));
        return;
      }
      setAccessToken(res.data.access_token);
      router.push('/dashboard');
    } catch {
      setError(tc('error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center">
      <GirihPattern opacity={0.05} />

      <div className="absolute top-4 right-4 z-10">
        <LanguageSwitcher />
      </div>

      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="card p-8">
          <div className="mb-8 text-center">
            <TamorLogo size={48} />
            <p className="mt-2 text-sm text-[var(--muted-foreground)]">{tc('appSubtitle')}</p>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm border border-red-200 dark:border-red-800">
              {error}
            </div>
          )}

          {mode === 'password' && (
            <form onSubmit={handlePasswordLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">{t('username')}</label>
                <input
                  type="text"
                  className="input-field"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">{t('password')}</label>
                <input
                  type="password"
                  className="input-field"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? tc('loading') : t('loginButton')}
              </button>
              <button
                type="button"
                className="w-full text-sm text-[var(--primary)] hover:underline"
                onClick={() => setMode('otp')}
              >
                {t('otpLogin')}
              </button>
            </form>
          )}

          {mode === 'mfa' && (
            <form onSubmit={handleMfaVerify} className="space-y-4">
              <h2 className="text-lg font-semibold text-center">{t('mfaTitle')}</h2>
              <div>
                <label className="block text-sm font-medium mb-1">{t('mfaCode')}</label>
                <input
                  type="text"
                  className="input-field text-center text-2xl tracking-widest"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  maxLength={8}
                  required
                  autoComplete="one-time-code"
                />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? tc('loading') : t('mfaVerify')}
              </button>
            </form>
          )}

          {mode === 'otp' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">{t('phone')}</label>
                <input
                  type="tel"
                  className="input-field"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  pattern="^\+998\d{9}$"
                  required
                />
              </div>
              <button type="button" className="btn-primary w-full" onClick={handleOtpRequest} disabled={loading}>
                {t('otpRequest')}
              </button>
              <form onSubmit={handleOtpVerify} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">{t('otpCode')}</label>
                  <input
                    type="text"
                    className="input-field text-center text-2xl tracking-widest"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    maxLength={6}
                    required
                  />
                </div>
                <button type="submit" className="btn-primary w-full" disabled={loading}>
                  {loading ? tc('loading') : t('otpVerify')}
                </button>
              </form>
              <button
                type="button"
                className="w-full text-sm text-[var(--primary)] hover:underline"
                onClick={() => setMode('password')}
              >
                {t('login')}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
