import { DarkThemeToggle } from "flowbite-react";

import patternLight from "/pattern-light.svg"
import patternDark from "/pattern-dark.svg"

import { FaLinux } from "react-icons/fa";
import { SiFlatpak } from "react-icons/si";
import { FaFedora } from "react-icons/fa6";
import { GrArchlinux } from "react-icons/gr";
import { PiPackage } from "react-icons/pi";
import { HiChevronRight } from "react-icons/hi2";

export default function App() {
  const CARDS = [
    {
      title: "Flatpak",
      description:
        "Install ZapZap securely with sandboxing via Flathub. Compatible with a wide range of Linux distributions.",
      url: "https://flathub.org/apps/com.rtosta.zapzap",
      icon: (
        <SiFlatpak className="w-9 h-9 text-gray-900 dark:text-gray-200" />
      ),
    },
    {
      title: "AppImage",
      description:
        "Download, make it executable, and run — no installation required. A portable and hassle-free option for any distro.",
      url: "https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-x86_64.AppImage",
      icon: (
        <PiPackage className="w-9 h-9 text-gray-900 dark:text-gray-200" />
      ),
    },
    {
      title: "Fedora",
      description:
        "Available via Copr. Easily install and keep ZapZap updated on Fedora using DNF.",
      url: "https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/",
      icon: (
        <FaFedora className="w-9 h-9 text-gray-900 dark:text-gray-200" />
      ),
    },
    {
      title: "AUR",
      description:
        "Install ZapZap on Arch-based systems via the Arch User Repository (AUR). This package is community-maintained.",
      url: "https://aur.archlinux.org/packages/zapzap",
      icon: (
        <GrArchlinux className="w-9 h-9 text-gray-900 dark:text-gray-200" />
      ),
    }
  ];


  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-4 py-24 dark:bg-gray-900">
      {/* Mudança de tema */}
      <div className="absolute inset-0 size-full">
        <div className="relative h-full w-full select-none">
          <img
            className="absolute right-0 min-w-dvh dark:hidden"
            alt="Pattern Light"
            src={patternLight}
          />
          <img
            className="absolute right-0 hidden min-w-dvh dark:block"
            alt="Pattern Dark"
            src={patternDark}
          />
        </div>
      </div>
      <div className="absolute top-4 right-4">
        <DarkThemeToggle />
      </div>
      {/* Conteúdo principal */}
      <div className="relative flex w-full max-w-5xl flex-col items-center justify-center gap-12">
        <div className="relative flex flex-col items-center gap-6">
          <h1 className="relative text-center text-6xl leading-[125%] font-bold text-gray-900 dark:text-gray-200">
            ZapZap
          </h1>
          <span className="inline-flex flex-wrap items-center justify-center gap-2.5 text-center">
            <span className="inline text-xl text-gray-600 dark:text-gray-400">
              A Linux WhatsApp web app with a native application experience.
            </span>
          </span>
        </div>

        {/* Mostra última versão disponível (Coletar do github) */}
        <div className='flex justify-center items-center gap-4 text-gray-600 dark:text-gray-400'>
          <span>{"Last releases"}</span>
          <div className="flex justify-center items-center gap-2">
            <FaLinux className="w-6 h-6" />
            <span>{"xxx..xxx...x"}</span>
          </div>

        </div>

        {/* Versões disponíveis */}
        <div className="relative flex w-full flex-col items-start gap-6 self-stretch">
          <div className="grid w-full grid-cols-1 gap-6 md:grid-cols-2">
            {CARDS.map((card) => (
              <a
                key={card.title}
                href={card.url}
                target="_blank"
                className="outline-primary-600 dark:outline-primary-500 group hover:border-primary-600 dark:hover:border-primary-500 cursor-pointer overflow-hidden rounded-xl border border-gray-200 bg-gray-50 outline-offset-2 focus:outline-2 dark:border-gray-700 dark:bg-gray-800"
              >
                <div className="flex items-center gap-6 p-4 jus h-full">
                  <div className="flex flex-1 items-center gap-4">
                    <div className="size-9">{card.icon}</div>

                    <div className="flex flex-1 flex-col items-start justify-center gap-1.5 border-l border-gray-200 pl-3.5 dark:border-gray-700">
                      <div className="w-full font-sans text-lg leading-4 font-semibold text-gray-900 dark:text-gray-200">
                        {card.title}
                      </div>

                      <div className="w-full font-sans text-sm leading-5 font-normal text-gray-500 dark:text-gray-400">
                        {card.description}
                      </div>
                    </div>
                  </div>

                  <HiChevronRight className="text-gray-500 dark:text-gray-400" />
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
