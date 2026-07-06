import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const internalApi =
  process.env.INTERNAL_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    // Fallback: proxy /api/* to backend when NEXT_PUBLIC_API_URL is not set (same-origin mode)
    return [
      {
        source: "/api/:path*",
        destination: `${internalApi}/api/:path*`,
      },
    ];
  },
};

export default withNextIntl(nextConfig);
