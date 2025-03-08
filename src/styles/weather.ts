export const weatherStyles = {
    container: {
        base: `
            relative
            flex items-center justify-center
            bg-white/90 rounded-full
            shadow-lg backdrop-blur-sm
            transition-all duration-300
            hover:transform hover:scale-110
        `,
        sizes: {
            sm: 'w-6 h-6',
            md: 'w-8 h-8',
            lg: 'w-10 h-10'
        }
    },
    icon: {
        base: `
            text-center leading-none
            transition-all duration-300
        `,
        sizes: {
            sm: 'text-xs',
            md: 'text-sm',
            lg: 'text-base'
        }
    },
    popup: {
        container: `
            p-3 rounded-lg
            bg-white/95 backdrop-blur-md
            shadow-xl
            min-w-[200px]
        `,
        header: `
            flex items-center gap-2
            border-b border-gray-200
            pb-2 mb-2
        `,
        readings: `
            grid grid-cols-2 gap-2
            text-sm text-gray-600
        `,
        footer: `
            text-xs text-gray-400
            mt-2 pt-2
            border-t border-gray-200
        `
    }
}; 