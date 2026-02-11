import { useTranslation, Trans } from "react-i18next";
import { Button, Badge, Card } from "flowbite-react";
import LatestRelease from "../components/LatestRelease";
import { Container } from "../components/Container";

import {
    LuDownload as Download,
    LuExternalLink as ExternalLink
} from "react-icons/lu";
import { SiFlatpak } from "react-icons/si";
import { FaFedora } from "react-icons/fa6";
import { GrArchlinux } from "react-icons/gr";
import { PiPackage } from "react-icons/pi";

export default function DownloadSection() {
    const { t } = useTranslation();

    // Pegando somente textos da locale
    const downloadOptions = t("downloadSection.options", { returnObjects: true }) as Array<{
        title: string;
        description: string;
        badge: string;
        features?: string[]; // Pode não ser array se a tradução estiver errada
    }>;

    // Ícones fixos fora da tradução
    const icons = [SiFlatpak, PiPackage, FaFedora, GrArchlinux];

    // URLs fixas fora da tradução
    const urls: string[] = [
        "https://flathub.org/apps/com.rtosta.zapzap",
        "https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-x86_64.AppImage",
    ];

    return (
        <Container name="download">
            <div className="text-center max-w-3xl mx-auto">
                <h2 className="text-4xl md:text-5xl font-bold mb-6">
                    <Trans
                        i18nKey="downloadSection.heading"
                        components={{ 1: <span className="bg-gradient-to-r from-primary-400 via-primary-700 to-primary-900 bg-clip-text text-transparent font-semibold" /> }}
                    />
                </h2>
                <p className="text-xl text-muted-foreground leading-relaxed">
                    {t("downloadSection.subtitle")}
                </p>
            </div>

            {/* Version Info */}
            <LatestRelease />

            {/* Download Options */}
            <div className="grid md:grid-cols-2 gap-8 mt-6">
                {downloadOptions.map((option, index) => {
                    const Icon = icons[index] || SiFlatpak;
                    const url = urls[index] || "#";
                    const safeFeatures = Array.isArray(option.features) ? option.features : [];

                    return (
                        <Card key={index} className="hover:shadow-xl hover:-translate-y-2 group">
                            <div className="p-8">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                        <Icon className="w-8 h-8 text-white" />
                                    </div>
                                    <Badge color={index === 0 ? "success" : index === 3 ? "failure" : "gray"} className="ml-2">
                                        {option.badge}
                                    </Badge>
                                </div>

                                <h3 className="text-2xl font-bold mb-3">{option.title}</h3>
                                <p className="text-muted-foreground mb-6 leading-relaxed">{option.description}</p>

                                <div className="flex flex-wrap gap-2 mb-6">
                                    {safeFeatures.map((feature, idx) => (
                                        <Badge color="indigo" key={idx} className="px-3 py-1">{feature}</Badge>
                                    ))}
                                </div>

                                <Button as="a" href={url} target="_blank" rel="noopener noreferrer" className="w-full gap-2 hover:shadow-xl bg-gradient-to-r from-primary-500 via-green-500 to-green-400" size="lg">
                                    <Download className="w-5 h-5" />
                                    {t("downloadSection.download")} {option.title}
                                    <ExternalLink className="w-4 h-4 ml-auto" />
                                </Button>
                            </div>
                        </Card>
                    );
                })}
            </div>
        </Container>
    );
}
