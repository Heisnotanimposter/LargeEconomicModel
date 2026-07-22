import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "LEM | Large Economic Model",
  description: "The Command Center — Professional economic data dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="lem-dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-lem-obsidian text-lem-white tracking-tight`}
      >
        {children}
      </body>
    </html>
  );
}
