import './globals.css'

export const metadata = {
  title: 'ProfFinder',
  description: 'A website to ask about professor',
   icons: {
    icon: "/ProfFinder.png",
  }
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

