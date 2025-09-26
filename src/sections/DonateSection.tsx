import {
    LuHeartHandshake as Heart,
    LuExternalLink as ExternalLink
} from "react-icons/lu";
import { FaPaypal, FaPix } from "react-icons/fa6";
import { SiKofi, SiGithubsponsors } from "react-icons/si";
import { Badge, Button, Card } from "flowbite-react";
import { Container } from "../components/Container";

function DonationSection() {

    const donationOptions = [
        {
            icon: FaPix,
            title: "Pix",
            description: "Contribua diretamente via chave Pix. Rápido, prático e sem taxas adicionais.",
            badge: "Direto",
            badgeVariant: "success" as const,
            url: "https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv",
            features: ["Instantâneo", "Sem taxas", "Seguro"],
            colors: {
                iconBg: "from-green-500 to-green-600",
                buttonBg: "from-green-500 via-emerald-500 to-lime-400"
            }
        },
        {
            icon: FaPaypal,
            title: "PayPal",
            description: "Faça sua doação internacionalmente de forma simples e segura com PayPal.",
            badge: "Global",
            badgeVariant: "gray" as const,
            url: "https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux&currency_code=USD",
            features: ["Cartão", "Internacional", "Seguro"],
            colors: {
                iconBg: "from-blue-500 to-blue-600",
                buttonBg: "from-blue-500 via-sky-500 to-cyan-400"
            }
        },
        {
            icon: SiKofi,
            title: "Ko-fi",
            description: "Buy me a coffee and help keep me coding!",
            badge: "Recorrente",
            badgeVariant: "indigo" as const,
            url: "https://ko-fi.com/rafaeltosta",
            features: ["Mensal", "Recorrente", "Comunidade"],
            colors: {
                iconBg: "from-sky-400 to-sky-600",
                buttonBg: "from-sky-400 via-cyan-500 to-blue-400"
            }
        },
        {
            icon: SiGithubsponsors,
            title: "GitHub Sponsors",
            description: "Contribua diretamente através do GitHub Sponsors e fortaleça o desenvolvimento open-source.",
            badge: "OSS",
            badgeVariant: "failure" as const,
            url: "https://github.com/sponsors/rafatosta",
            features: ["Dev", "Open Source", "Internacional"],
            colors: {
                iconBg: "from-pink-500 to-rose-600",
                buttonBg: "from-pink-500 via-rose-500 to-red-400"
            }
        }
    ];

    return (
        <Container name="donate">
            <div className="text-center max-w-3xl mx-auto">
                <h2 className="text-4xl md:text-5xl font-bold mb-6">
                    Apoie o
                    <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent font-semibold"> ZapZap</span>
                </h2>
                <p className="text-xl text-muted-foreground leading-relaxed">
                    Sua contribuição ajuda a manter o projeto ativo, gratuito e em constante evolução.
                </p>
            </div>

            {/* Donation Options */}
            <div className="grid md:grid-cols-2 gap-8 mt-6">
                {donationOptions.map((option, index) => (
                    <Card
                        key={index}
                        className="hover:shadow-xl hover:-translate-y-2 group"
                    >
                        <div className="p-8">
                            <div className="flex items-start justify-between mb-4">
                                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${option.colors.iconBg} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
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
                                target="_blank"
                                rel="noopener noreferrer"
                                className={`w-full gap-2 hover:shadow-xl bg-gradient-to-r ${option.colors.buttonBg}`}
                                size="lg"
                            >
                                <Heart className="w-5 h-5" />
                                Apoiar via {option.title}
                                <ExternalLink className="w-4 h-4 ml-auto" />
                            </Button>
                        </div>
                    </Card>
                ))}
            </div>
        </Container>
    );
}

export default DonationSection;
