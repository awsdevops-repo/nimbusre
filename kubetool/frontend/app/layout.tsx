import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "NimbusRE Agent - Kubernetes Management",
  description: "AI-powered SRE tool for Kubernetes cluster management and troubleshooting",
  icons: {
    icon: "/favicon.ico",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="bg-sre-dark text-white font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
