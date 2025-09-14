import { Button } from "flowbite-react";
import LatestRelease from "./LatestRelease";
import { LuStar as Star, LuUsers as Users, LuDownload as Download, LuGithub as Github } from "react-icons/lu";
import zapzapScreenshot from "/zapzap-screenshot.png";
import { Container } from "./Container";


function Hero() {
    return (
        <Container name="home">
            <LatestRelease />
            {/* Main Heading */}
            <h1 className="flex flex-col items-center justify-center gap-2 text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
                <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 \
                     bg-clip-text text-transparent text-shadow-[0_35px_35px_rgb(0_0_0_/_0.25)]">
                    ZapZap
                </span>

                <span className="text-center antialiased text-gray-700 dark:text-gray-300">
                    WhatsApp nativo para Linux
                </span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-center mb-8 max-w-3xl mx-auto text-gray-600 dark:text-gray-200">
                Uma experiência <span className="text-primary-500 font-semibold">nativa</span> do WhatsApp
                para Linux com suporte a múltiplas contas, notificações do sistema e muito mais.
            </p>

            {/* Stats */}
            <div className="flex justify-center items-center gap-8 mb-12">
                <div className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-500" />
                    <span className="font-medium">4.8/5</span>
                </div>
                <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-primary-500" />
                    <span className="font-medium">100k+ usuários</span>
                </div>
                <div className="flex items-center gap-2">
                    <Download className="w-5 h-5 text-blue-500" />
                    <span className="font-medium">Código aberto</span>
                </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
                <Button size="lg" className="px-8 py-4 text-lg font-medium gap-3 \
                    bg-gradient-to-r from-primary-500 via-green-500 to-green-400 shadow-lg shadow-primary-500/50">
                    <Download className="w-5 h-5" />
                    Download Grátis
                </Button>
                <Button color="alternative" size="lg" className="px-8 py-4 text-lg font-medium gap-3">
                    <Github className="w-5 h-5" />
                    Ver no GitHub
                </Button>
            </div>

            {/* Screenshot */}
            <div className="relative max-w-5xl mx-auto">
                <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-border/50">
                    <img
                        src={zapzapScreenshot}
                        alt="ZapZap Screenshot"
                        className="w-full h-auto"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-background/10 to-transparent pointer-events-none" />
                </div>
                {/* Decorative elements */}
                <div className="absolute -top-4 -left-4 w-72 h-72 bg-primary/10 rounded-full blur-3xl -z-10" />
                <div className="absolute -bottom-4 -right-4 w-72 h-72 bg-accent/10 rounded-full blur-3xl -z-10" />
            </div>
        </Container>
    );
}

export default Hero;