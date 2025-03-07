import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const geist = Geist({
  subsets: ["latin"],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "Metro de Medellín - Rutas en tiempo real",
  description: "Sistema de rutas en tiempo real para el Metro de Medellín",
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="light" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
      </head>
      <body className={`${geist.className} min-h-screen bg-gradient-to-b from-blue-50 to-white`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
