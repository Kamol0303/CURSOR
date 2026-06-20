'use client';

import {FormEvent, useMemo, useState} from 'react';
import {useTranslations} from 'next-intl';

import {useRouter} from '@/i18n/navigation';

type LoginFormProps = {
  locale: string;
};

type LoginSuccessPayload = {
  mfa_required?: boolean;
  challenge_token?: string | null;
  user?: {
    username?: string | null;
  } | null;
};

function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';
}

function parseErrorCode(payload: unknown): string {
  if (
    payload &&
    typeof payload === 'object' &&
    'detail' in payload &&
    payload.detail &&
    typeof payload.detail === 'object' &&
    'code' in payload.detail &&
    typeof payload.detail.code === 'string'
  ) {
    return payload.detail.code;
  }

  if (
    payload &&
    typeof payload === 'object' &&
    'error' in payload &&
    payload.error &&
    typeof payload.error === 'object' &&
    'code' in payload.error &&
    typeof payload.error.code === 'string'
  ) {
    return payload.error.code;
  }

  return 'UNKNOWN_ERROR';
}

export function LoginForm({locale}: LoginFormProps) {
  const t = useTranslations('auth');
  const router = useRouter();

  const [username, setUsername] = useState('hokimyat');
  const [password, setPassword] = useState('admin2026');
  const [code, setCode] = useState('');
  const [challengeToken, setChallengeToken] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isMfaStep = useMemo(() => Boolean(challengeToken), [challengeToken]);

  async function submitPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({username, password, locale})
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(parseErrorCode(payload));
      }

      const data = payload.data as LoginSuccessPayload;
      if (data.mfa_required && data.challenge_token) {
        setChallengeToken(data.challenge_token);
        setMessage(t('mfaPrompt'));
        return;
      }

      setMessage(t('loginSuccess'));
      router.push('/dashboard', {locale});
    } catch (submitError) {
      const codeValue = submitError instanceof Error ? submitError.message : 'UNKNOWN_ERROR';
      setError(t(`errors.${codeValue}` as never));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function submitMfa(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!challengeToken) {
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setMessage(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/mfa/verify`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({challenge_token: challengeToken, code})
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(parseErrorCode(payload));
      }

      setChallengeToken(null);
      setCode('');
      setMessage(t('loginSuccess'));
      router.push('/dashboard', {locale});
    } catch (submitError) {
      const codeValue = submitError instanceof Error ? submitError.message : 'UNKNOWN_ERROR';
      setError(t(`errors.${codeValue}` as never));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-[rgba(27,77,62,0.12)] bg-[rgba(27,77,62,0.04)] px-4 py-3 text-sm text-slate-700">
        <p className="font-semibold text-[var(--color-naqsh-primary)]">{t('demoCredentialsTitle')}</p>
        <p className="mt-1">
          <span className="font-medium">{t('username')}:</span> hokimyat
        </p>
        <p>
          <span className="font-medium">{t('password')}:</span> admin2026
        </p>
      </div>

      {!isMfaStep ? (
        <form className="space-y-5" onSubmit={submitPassword}>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t('username')}</label>
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-[var(--color-naqsh-primary)]"
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t('password')}</label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-[var(--color-naqsh-primary)]"
            />
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-2xl bg-[var(--color-naqsh-primary)] px-4 py-3 font-semibold text-white transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? t('loading') : t('submit')}
          </button>
        </form>
      ) : (
        <form className="space-y-5" onSubmit={submitMfa}>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">{t('mfa')}</label>
            <input
              value={code}
              onChange={(event) => setCode(event.target.value)}
              placeholder="123456"
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-[var(--color-naqsh-primary)]"
            />
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-2xl bg-[var(--color-naqsh-primary)] px-4 py-3 font-semibold text-white transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? t('loading') : t('mfaSubmit')}
          </button>
        </form>
      )}

      {message ? (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {message}
        </div>
      ) : null}

      {error ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}
    </div>
  );
}
