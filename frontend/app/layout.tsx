import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Possibilista Prototype",
  description: "Deterministic guidance prototype for secondary-track exploration.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
