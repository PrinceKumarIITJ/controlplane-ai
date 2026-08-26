import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ControlPlane.ai — Real-Time AI Assurance & Intervention Layer',
  description: 'Dynamically determines required level of assurance and intervenes before risky AI actions hit target systems.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
