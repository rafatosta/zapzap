import {
    LuDownload as Download,
    LuExternalLink as ExternalLink
} from "react-icons/lu";
import LatestRelease from "../components/LatestRelease";
import { Badge, Button, Card } from "flowbite-react";

import { Container } from "../components/Container";

import { SiFlatpak } from "react-icons/si";
import { FaFedora } from "react-icons/fa6";
import { GrArchlinux } from "react-icons/gr";
import { PiPackage } from "react-icons/pi";

function DownloadSection() {

    const downloadOptions = [
        {
            icon: SiFlatpak,
            title: "Flatpak",
            description: "Instalação segura com sandboxing via Flathub. Compatível com uma ampla gama de distribuições Linux.",
            badge: "Recomendado",
            badgeVariant: "success" as const,
            url: "https://flathub.org/apps/com.rtosta.zapzap",
            features: ["Sandboxing", "Auto-updates", "Universal"]
        },
        {
            icon: PiPackage,
            title: "AppImage",
            description: "Baixe, torne executável e execute — nenhuma instalação necessária. Uma opção portátil e sem complicações.",
            badge: "Portátil",
            badgeVariant: "gray" as const,
            url: "https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-x86_64.AppImage",
            features: ["Sem instalação", "Portátil", "Universal"]
        },
        {
            icon: FaFedora,
            title: "Fedora",
            description: "Disponível via Copr. Instale e mantenha o ZapZap atualizado no Fedora usando DNF.",
            badge: "DNF",
            badgeVariant: "gray" as const,
            url: "https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/",
            features: ["DNF Package", "Auto-updates", "Nativo"]
        },
        {
            icon: GrArchlinux,
            title: "AUR",
            description: "Instale ZapZap em sistemas baseados no Arch via Arch User Repository (AUR). Pacote mantido pela comunidade.",
            badge: "Arch",
            badgeVariant: "failure" as const,
            url: "https://aur.archlinux.org/packages/zapzap",
            features: ["AUR Helper", "Community", "Rolling"]
        }
    ];

    return (
        <Container name="download">
            <div className="text-center max-w-3xl mx-auto">
                <h2 className="text-4xl md:text-5xl font-bold mb-6">
                    Escolha sua
                    <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent font-semibold"> distribuição</span>
                </h2>
                <p className="text-xl text-muted-foreground leading-relaxed">
                    ZapZap está disponível em múltiplos formatos para atender todas as distribuições Linux.
                </p>
            </div>

            {/* Version Info */}

            <LatestRelease />

            {/* Download Options */}
            <div className="grid md:grid-cols-2 gap-8 mt-6">
                {downloadOptions.map((option, index) => (
                    <Card
                        key={index}
                        className="hover:shadow-xl hover:-translate-y-2 group"
                    >
                        <div className="p-8">
                            <div className="flex items-start justify-between mb-4">
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                    <option.icon className="w-8 h-8 text-white" />
                                </div>
                                <Badge color={option.badgeVariant} className="ml-2">
                                    {option.badge}
                                </Badge>
                            </div>

                            <h3 className="text-2xl font-bold mb-3">{option.title}</h3>
                            <p className="text-muted-foreground mb-6 leading-relaxed">
                                {option.description}
                            </p>

                            <div className="flex flex-wrap gap-2 mb-6">
                                {option.features.map((feature, idx) => (
                                    <Badge
                                        color="indigo"
                                        key={idx}
                                        className="px-3 py-1"
                                    >
                                        {feature}
                                    </Badge>
                                ))}
                            </div>

                            <Button as={"a"} href={option.url}
                                className="w-full gap-2 hover:shadow-xl \
                                    bg-gradient-to-r from-primary-500 via-green-500 to-green-400
                                    "
                                size="lg"
                            >
                                <Download className="w-5 h-5" />
                                Baixar {option.title}
                                <ExternalLink className="w-4 h-4 ml-auto" />
                            </Button>
                        </div>
                    </Card>
                ))}
            </div>
        </Container>
    );
}

export default DownloadSection;