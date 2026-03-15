import { Button, Badge } from "flowbite-react";
import LatestRelease from "./LatestRelease";
import {
  LuStar as Star,
  LuUsers as Users,
  LuDownload as Download,
  LuGithub as Github,
  LuShieldCheck as ShieldCheck,
  LuBadgeCheck as BadgeCheck,
} from "react-icons/lu";
import zapzapScreenshot from "/zapzap-screenshot.png";
import { Container } from "./Container";
import { useTranslation } from "react-i18next";

function Hero() {
  const { t } = useTranslation();

  const trustBadges = t("hero.trustBadges", {
    returnObjects: true,
  }) as string[];

  return (
    <Container name="home">
      <LatestRelease />

      <h1 className="animate-slide-up mb-6 flex flex-col items-center justify-center gap-2 text-5xl font-bold md:text-7xl">
        <span className="from-primary-400 via-primary-700 to-primary-900 bg-gradient-to-r bg-clip-text text-transparent text-shadow-[0_35px_35px_rgb(0_0_0_/_0.25)]">
          ZapZap
        </span>
        <span className="text-center text-gray-700 antialiased dark:text-gray-300">
          {t("hero.heading")}
        </span>
      </h1>

      <p className="mx-auto mb-6 max-w-3xl text-center text-xl text-gray-600 md:text-2xl dark:text-gray-200">
        {t("hero.subtitle", { native: t("hero.native") })}
      </p>

      <div className="mb-8 flex flex-wrap items-center justify-center gap-3">
        {trustBadges.map((badge, index) => (
          <Badge key={index} color="indigo" className="px-3 py-1 text-sm">
            {badge}
          </Badge>
        ))}
      </div>

      <div className="mb-12 flex flex-wrap justify-center gap-8">
        <div className="flex items-center gap-2">
          <Star className="h-5 w-5 text-yellow-500" />
          <span className="font-medium">{t("hero.stats.rating")}</span>
        </div>
        <div className="flex items-center gap-2">
          <Users className="text-primary-500 h-5 w-5" />
          <span className="font-medium">{t("hero.stats.users")}</span>
        </div>
        <div className="flex items-center gap-2">
          <Download className="h-5 w-5 text-blue-500" />
          <span className="font-medium">{t("hero.stats.opensource")}</span>
        </div>
      </div>

      <div className="mb-16 flex flex-col items-center justify-center gap-4 sm:flex-row">
        <Button
          href="#download"
          size="lg"
          className="from-primary-500 shadow-primary-500/50 gap-3 bg-gradient-to-r via-green-500 to-green-400 px-8 py-4 text-lg font-medium shadow-lg"
        >
          <Download className="h-5 w-5" />
          {t("hero.buttons.download")}
        </Button>
        <Button
          href="https://github.com/rafatosta/zapzap"
          color="alternative"
          size="lg"
          className="gap-3 px-8 py-4 text-lg font-medium"
        >
          <Github className="h-5 w-5" />
          {t("hero.buttons.github")}
        </Button>
      </div>

      <div className="relative mx-auto max-w-5xl">
        <div className="absolute top-4 left-4 z-10 hidden rounded-full bg-white/90 px-4 py-1 text-sm font-medium shadow md:block dark:bg-gray-900/90">
          <span className="inline-flex items-center gap-1">
            <BadgeCheck className="h-4 w-4 text-green-500" />
            {t("hero.proof.opensource")}
          </span>
        </div>
        <div className="absolute top-4 right-4 z-10 hidden rounded-full bg-white/90 px-4 py-1 text-sm font-medium shadow md:block dark:bg-gray-900/90">
          <span className="inline-flex items-center gap-1">
            <ShieldCheck className="h-4 w-4 text-blue-500" />
            {t("hero.proof.privacy")}
          </span>
        </div>

        <div className="border-border/50 relative overflow-hidden rounded-2xl border shadow-2xl">
          <img
            src={zapzapScreenshot}
            alt={t("hero.screenshotAlt")}
            className="h-auto w-full"
          />
          <div className="from-background/10 pointer-events-none absolute inset-0 bg-gradient-to-t to-transparent" />
        </div>
        <div className="bg-primary/10 absolute -top-4 -left-4 -z-10 h-72 w-72 rounded-full blur-3xl" />
        <div className="bg-accent/10 absolute -right-4 -bottom-4 -z-10 h-72 w-72 rounded-full blur-3xl" />
      </div>
    </Container>
  );
}

export default Hero;
