import Download from "./sections/Download";
import Hero from "./sections/Hero";
import Showcase from "./sections/Showcase";

function App() {

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      <Header />
      <main>
        <Hero />
        <Showcase />
        <Download />
        <Footer />
      </main>
    </div>
  )
}

/*************************************************************** */



const nav = [
  { label: "Features", href: "#features" },
  { label: "Download", href: "#download" },
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


function Footer() {
  return (
    <footer className="border-t border-hairline">
      <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 px-6 py-10 md:flex-row md:items-center">
        <div className="flex items-center gap-2 text-sm">
          <span className="inline-block h-2 w-2 rounded-full bg-primary" aria-hidden />
          <span className="font-semibold tracking-tight">ZapZap</span>
          <span className="text-muted-foreground">— built by Rafael Tosta.</span>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
          <a href="https://github.com/rafatosta/zapzap" className="hover:text-foreground">
            GitHub
          </a>
          <a href="https://github.com/sponsors/rafatosta" className="hover:text-foreground">
            Sponsor
          </a>
          <a href="https://flathub.org/apps/com.rtosta.zapzap" className="hover:text-foreground">
            Flathub
          </a>
        </div>
      </div>
    </footer>
  );
}


export default App
