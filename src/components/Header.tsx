import { Menu, X } from "lucide-react";
import * as Dialog from "@radix-ui/react-dialog";

import icon from '/icon.svg'

const nav = [
  { label: "Features", href: "#features" },
  { label: "Download", href: "#download" },
  { label: "Donate", href: "#donate" },
  { label: "GitHub", href: "https://github.com/rafatosta/zapzap" },
];

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-hairline bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <a
          href="#"
          className="flex items-center gap-2 text-[15px] font-semibold tracking-tight"
        >
          <img
            src={icon}
            alt="ZapZap desktop client running on Linux"
            loading="lazy"
            className="w-8 hover:opacity-90"
          />
          ZapZap
        </a>

        <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
          {nav.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="transition-colors hover:text-foreground"
              target={item.href.startsWith("http") ? "_blank" : undefined}
              rel={item.href.startsWith("http") ? "noreferrer" : undefined}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:block">
          <a
            href="#download"
            className="rounded-md border border-border bg-foreground px-3.5 py-1.5 text-xs font-medium text-background transition-opacity hover:opacity-90"
          >
            Download
          </a>
        </div>

        <Dialog.Root>
          <Dialog.Trigger asChild>
            <button
              type="button"
              className="inline-flex size-9 items-center justify-center rounded-md border border-border text-foreground transition-colors hover:bg-muted md:hidden"
              aria-label="Open menu"
            >
              <Menu className="size-4" />
            </button>
          </Dialog.Trigger>

          <Dialog.Portal>
            <Dialog.Overlay className="fixed inset-0 z-50 bg-background/70 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />

            <Dialog.Content className="fixed right-0 top-0 z-50 h-dvh w-72 border-l border-border bg-background p-6 shadow-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right">
              <div className="flex items-center justify-between">
                <Dialog.Title asChild>
                  <a
                    href="#"
                    className="flex items-center gap-2 text-[15px] font-semibold tracking-tight"
                  >
                    <img
                      src={icon}
                      alt="ZapZap"
                      loading="lazy"
                      className="w-8"
                    />
                    ZapZap
                  </a>
                </Dialog.Title>

                <Dialog.Close asChild>
                  <button
                    type="button"
                    className="inline-flex size-9 items-center justify-center rounded-md border border-border text-foreground transition-colors hover:bg-muted"
                    aria-label="Close menu"
                  >
                    <X className="size-4" />
                  </button>
                </Dialog.Close>
              </div>

              <nav className="mt-8 flex flex-col gap-1">
                {nav.map((item) => (
                  <Dialog.Close key={item.label} asChild>
                    <a
                      href={item.href}
                      className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                      target={item.href.startsWith("http") ? "_blank" : undefined}
                      rel={item.href.startsWith("http") ? "noreferrer" : undefined}
                    >
                      {item.label}
                    </a>
                  </Dialog.Close>
                ))}
              </nav>

              <Dialog.Close asChild>
                <a
                  href="#download"
                  className="mt-6 block rounded-md border border-border bg-foreground px-3.5 py-2 text-center text-sm font-medium text-background transition-opacity hover:opacity-90"
                >
                  Download
                </a>
              </Dialog.Close>
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>
      </div>
    </header>
  );
}