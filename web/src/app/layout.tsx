import "@/app/globals.css";
import { Playfair_Display, Manrope } from "next/font/google";
import type { Metadata } from "next";

const display = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["600", "700"]
});

const body = Manrope({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600", "700"]
});

export const metadata: Metadata = {
  title: "FormulateFit AI Studio",
  description: "Turn messy fitness intent into structured, editable training blueprints"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${display.variable} ${body.variable} bg-background text-foreground`}>{children}</body>
    </html>
  );
}
