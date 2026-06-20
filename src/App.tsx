import Hero from "./sections/Hero";

function App() {

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      <Header />
      <main>
        <Hero />
      </main>
    </div>
  )
}

/*************************************************************** */



const nav = [
  { label: "Features", href: "#features" },
  { label: "Download", href: "#download" },
  { label: "FAQ", href: "#faq" },
  { label: "GitHub", href: "https://github.com/rafatosta/zapzap" },
];

function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-hairline bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <a href="#" className="flex items-center gap-2 text-[15px] font-semibold tracking-tight">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-primary" aria-hidden />
          ZapZap
        </a>
        <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
          {nav.map((n) => (
            <a key={n.label} href={n.href} className="transition-colors hover:text-foreground">
              {n.label}
            </a>
          ))}
        </nav>
        <a
          href="#download"
          className="rounded-md border border-border bg-foreground px-3.5 py-1.5 text-xs font-medium text-background transition-opacity hover:opacity-90"
        >
          Download
        </a>
      </div>
    </header>
  );
}


export default App
