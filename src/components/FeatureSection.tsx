import { Card } from "flowbite-react";
import {
    LuBell as Bell,
    LuUsers as Users,
    LuShare2 as Share2,
    LuPalette as Palette,
    LuShield as Shield,
    LuMonitor as Monitor,
    LuZap as Zap,
    LuSmartphone as Smartphone,
    LuDownload as Download
} from "react-icons/lu";
import { Container } from "./Container";

function FeatureSection() {
    const features = [
        {
            icon: Users,
            title: "Múltiplas Contas",
            description: "Gerencie várias contas do WhatsApp simultaneamente em uma única interface."
        },
        {
            icon: Bell,
            title: "Notificações Nativas",
            description: "Receba notificações do sistema integradas com o ambiente Linux."
        },
        {
            icon: Share2,
            title: "Compartilhamento de Mídia",
            description: "Arraste e solte arquivos diretamente para enviar fotos, vídeos e documentos."
        },
        {
            icon: Palette,
            title: "Temas Personalizados",
            description: "Adaptação automática aos temas claro e escuro do seu sistema."
        },
        {
            icon: Shield,
            title: "Privacidade Respeitada",
            description: "Sem coleta de dados. Sua privacidade é nossa prioridade."
        },
        {
            icon: Monitor,
            title: "Modo Background",
            description: "Continue recebendo mensagens mesmo com a janela minimizada."
        }
    ];

    return (
        <Container name="features">
            <div className="text-center max-w-3xl mx-auto mb-16">
                <p className="text-4xl md:text-5xl font-bold mb-6">
                    Recursos que fazem a <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent font-semibold">diferença</span>
                </p>
                <p className="text-xl text-muted-foreground">
                    ZapZap oferece uma experiência completa e nativa do WhatsApp,
                    projetada especificamente para usuários Linux.
                </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
                {features.map((feature, index) => (
                    <Card
                        key={index}
                        className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
                    >
                        <div className="p-6 text-center">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 mx-auto mb-4 flex items-center justify-center">
                                <feature.icon className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                            <p className="text-muted-foreground">{feature.description}</p>
                        </div>
                    </Card>
                ))}
            </div>

            {/* Why Choose Section */}
            <div className="grid lg:grid-cols-3 gap-8">
                <div className="text-center lg:text-left">
                    <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500 to-blue-600 mx-auto lg:mx-0 mb-6 flex items-center justify-center">
                        <Zap className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-4">Simples</h3>
                    <p className="text-muted-foreground">
                        Interface limpa e intuitiva. Sem complicações, apenas a experiência
                        do WhatsApp que você já conhece.
                    </p>
                </div>

                <div className="text-center lg:text-left">
                    <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-purple-500 to-purple-600 mx-auto lg:mx-0 mb-6 flex items-center justify-center">
                        <Smartphone className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-4">Nativo</h3>
                    <p className="text-muted-foreground">
                        Integração completa com o Linux. Atalhos do teclado, notificações
                        e comportamento nativo do sistema.
                    </p>
                </div>

                <div className="text-center lg:text-left">
                    <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-green-500 to-green-600 mx-auto lg:mx-0 mb-6 flex items-center justify-center">
                        <Download className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-4">Livre</h3>
                    <p className="text-muted-foreground">
                        Código aberto e gratuito. Sem limitações, sem custos ocultos.
                        Contribua e ajude a melhorar o projeto.
                    </p>
                </div>
            </div>
        </Container>
    );
}

export default FeatureSection;