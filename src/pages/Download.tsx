import { Element } from 'react-scroll';

import { SiFlatpak } from "react-icons/si";
import { FaFedora } from "react-icons/fa6";
import { GrArchlinux } from "react-icons/gr";
import { PiPackage } from "react-icons/pi";
import { HiChevronRight } from "react-icons/hi2";

import LatestRelease from "../components/LatestRelease";
import ReleaseTimeline from "../components/ReleaseTimeline";
import { PageContainer } from '../components/PageContainer';

function Download() {
    const CARDS = [
        {
            title: "Flatpak",
            description:
                "Install ZapZap securely with sandboxing via Flathub. Compatible with a wide range of Linux distributions.",
            url: "https://flathub.org/apps/com.rtosta.zapzap",
            icon: <SiFlatpak className="w-9 h-9 text-gray-900 dark:text-gray-200" />,
        },
        {
            title: "AppImage",
            description:
                "Download, make it executable, and run — no installation required. A portable and hassle-free option for any distro.",
            url: "https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-x86_64.AppImage",
            icon: <PiPackage className="w-9 h-9 text-gray-900 dark:text-gray-200" />,
        },
        {
            title: "Fedora",
            description:
                "Available via Copr. Easily install and keep ZapZap updated on Fedora using DNF.",
            url: "https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/",
            icon: <FaFedora className="w-9 h-9 text-gray-900 dark:text-gray-200" />,
        },
        {
            title: "AUR",
            description:
                "Install ZapZap on Arch-based systems via the Arch User Repository (AUR). This package is community-maintained.",
            url: "https://aur.archlinux.org/packages/zapzap",
            icon: <GrArchlinux className="w-9 h-9 text-gray-900 dark:text-gray-200" />,
        },
    ];

    return (
        <Element name="download">
            <PageContainer>

                {/* Título principal */}
                <header className="text-center space-y-4">
                    <h1 className="text-5xl md:text-6xl font-bold text-shadow-lg">
                        Downloads
                    </h1>

                    {/* Última versão */}
                    <section className="w-full">
                        <LatestRelease />
                    </section>
                </header>

                <div className='flex flex-col lg:flex-row justify-between items-start w-full gap-6'>
                    {/* Opções de download */}
                    <section className="w-full">
                        <h2 className="text-2xl font-semibold mb-4 text-gray-700 dark:text-gray-100">
                            Available Packages
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
                            {CARDS.map((card) => (
                                <a
                                    key={card.title}
                                    href={card.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="group rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 hover:border-primary-600 dark:hover:border-primary-500 transition-colors"
                                >
                                    <div className="flex items-center gap-6 p-4">
                                        <div className="flex-shrink-0">{card.icon}</div>
                                        <div className="flex flex-col gap-1 border-l border-gray-200 pl-4 dark:border-gray-700">
                                            <h3 className="text-lg font-semibold">{card.title}</h3>

                                        </div>
                                        <HiChevronRight className="ml-auto text-gray-400 group-hover:text-primary-600 transition" />
                                    </div>
                                </a>
                            ))}
                        </div>
                    </section>
                    {/* Linha do tempo de releases */}
                    <section className="w-full">
                        <ReleaseTimeline />
                    </section>


                </div>
            </PageContainer>
        </Element>
    );
}

export default Download;
