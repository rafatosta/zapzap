import {
    LuCircleCheckBig as CheckCircle,
    LuPackage as Package,
    LuArchive as Archive,
    LuLaptop as Laptop,
    LuDownload as Download,
    LuExternalLink as ExternalLink
} from "react-icons/lu";
import LatestRelease from "./LatestRelease";
import { Badge, Button, Card } from "flowbite-react";

function DownloadSection() {

    const downloadOptions = [
        {
            icon: Package,
            title: "Flatpak",
            description: "Instalação segura com sandboxing via Flathub. Compatível com uma ampla gama de distribuições Linux.",
            badge: "Recomendado",
            badgeVariant: "default" as const,
            url: "#",
            features: ["Sandboxing", "Auto-updates", "Universal"]
        },
        {
            icon: Archive,
            title: "AppImage",
            description: "Baixe, torne executável e execute — nenhuma instalação necessária. Uma opção portátil e sem complicações.",
            badge: "Portátil",
            badgeVariant: "secondary" as const,
            url: "#",
            features: ["Sem instalação", "Portátil", "Universal"]
        },
        {
            icon: Laptop,
            title: "Fedora",
            description: "Disponível via Copr. Instale e mantenha o ZapZap atualizado no Fedora usando DNF.",
            badge: "DNF",
            badgeVariant: "outline" as const,
            url: "#",
            features: ["DNF Package", "Auto-updates", "Nativo"]
        },
        {
            icon: Package,
            title: "AUR",
            description: "Instale ZapZap em sistemas baseados no Arch via Arch User Repository (AUR). Pacote mantido pela comunidade.",
            badge: "Arch",
            badgeVariant: "outline" as const,
            url: "#",
            features: ["AUR Helper", "Community", "Rolling"]
        }
    ];

    return (
        <section id="download" className="py-20">
            <div className="mx-auto px-4 py-20 flex flex-col items-center justify-center gap-6" >
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <h2 className="text-4xl md:text-5xl font-bold mb-6">
                        Escolha sua
                        <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent font-semibold"> distribuição</span>
                    </h2>
                    <p className="text-xl text-muted-foreground leading-relaxed">
                        ZapZap está disponível em múltiplos formatos para atender todas as distribuições Linux.
                    </p>
                </div>

                {/* Version Info */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 glassmorphism px-6 py-3 rounded-full">
                        <CheckCircle className="w-5 h-5 text-primary-700" />
                        <span className="font-medium">Versão atual: 6.2.1</span>
                    </div>
                    <LatestRelease />
                </div>

                {/* Download Options */}
                <div className="grid md:grid-cols-2 gap-8 mb-16">
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
                                    <Badge  color={option.badge === "Recomendado" ? "success" : "default"} className="ml-2">
                                        {option.badge}
                                    </Badge>
                                </div>

                                <h3 className="text-2xl font-bold mb-3">{option.title}</h3>
                                <p className="text-muted-foreground mb-6 leading-relaxed">
                                    {option.description}
                                </p>

                                <div className="flex flex-wrap gap-2 mb-6">
                                    {option.features.map((feature, idx) => (
                                        <span
                                            key={idx}
                                            className="px-3 py-1 text-sm bg-accent text-accent-foreground rounded-full"
                                        >
                                            {feature}
                                        </span>
                                    ))}
                                </div>

                                <Button
                                    className="w-full gap-2 group-hover:shadow-lg \
                                    bg-gradient-to-r from-primary-500 via-green-500 to-green-400"
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


                {/* System Requirements REVISAR */}
                <div className="max-w-2xl mx-auto">
                    <Card className="">
                        <div className="p-8 text-center">
                            <h3 className="text-2xl font-bold mb-4">Requisitos do Sistema</h3>
                            <div className="grid md:grid-cols-2 gap-6 text-left">
                                <div>
                                    <h4 className="font-semibold mb-2 text-primary-500">Mínimo</h4>
                                    <ul className="text-muted-foreground space-y-1">
                                        <li>• Linux (kernel 3.10+)</li>
                                        <li>• 1 GB RAM</li>
                                        <li>• 200 MB espaço</li>
                                        <li>• Conexão com internet</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="font-semibold mb-2 text-primary-500">Recomendado</h4>
                                    <ul className="text-muted-foreground space-y-1">
                                        <li>• Ubuntu 20.04+ / similar</li>
                                        <li>• 2 GB RAM</li>
                                        <li>• 500 MB espaço</li>
                                        <li>• Ambiente desktop moderno</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </Card>
                </div>

            </div>
        </section>
    );
}

export default DownloadSection;