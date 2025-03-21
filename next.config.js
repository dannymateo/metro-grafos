/** @type {import('next').NextConfig} */
const nextConfig = {
    basePath: '/client-metro',
    trailingSlash: true,

    webpack: (config) => {
        config.resolve.fallback = {
            ...config.resolve.fallback,
            fs: false,
        };
        return config;
    },
};

module.exports = nextConfig;
