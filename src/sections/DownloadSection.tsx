import { useTranslation, Trans } from "react-i18next";
import { Button, Badge, Card } from "flowbite-react";
import LatestRelease from "../components/LatestRelease";
import { Container } from "../components/Container";

import {
  LuDownload as Download,
  LuExternalLink as ExternalLink,
  LuShieldCheck as ShieldCheck,
  LuCheckCheck as CheckCheck,
} from "react-icons/lu";
import { SiFlatpak } from "react-icons/si";
import { FaFedora } from "react-icons/fa6";
import { GrArchlinux } from "react-icons/gr";
import { PiPackage } from "react-icons/pi";
import { IconType } from "react-icons";

type DownloadOption = {
  title: string;
  description: string;
  badge: string;
  features?: string[];
};

export default function DownloadSection() {
  const { t } = useTranslation();

  const downloadOptions = t("downloadSection.options", {
    returnObjects: true,
  }) as DownloadOption[];

  const quickSteps = t("downloadSection.quickSteps", {
    returnObjects: true,
  }) as string[];

  const icons: IconType[] = [SiFlatpak, PiPackage, FaFedora, GrArchlinux];

  const urls: string[] = [
    "https://flathub.org/apps/com.rtosta.zapzap",
    "https://github.com/rafatosta/zapzap/releases/latest/download/ZapZap-x86_64.AppImage",
    "https://copr.fedorainfracloud.org/coprs/rafatosta/zapzap/",
    "https://aur.archlinux.org/packages/zapzap",
  ];

  return (
    <Container name="download">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="mb-6 text-4xl font-bold md:text-5xl">
          <Trans
            i18nKey="downloadSection.heading"
            components={{
              1: (
                <span className="from-primary-400 via-primary-700 to-primary-900 bg-gradient-to-r bg-clip-text font-semibold text-transparent" />
              ),
            }}
          />
        </h2>
        <p className="text-muted-foreground text-xl leading-relaxed">
          {t("downloadSection.subtitle")}
        </p>
      </div>

      <LatestRelease />

      <Card className="from-primary-50 to-primary-100/50 dark:from-primary-950/30 dark:to-primary-900/10 mt-6 w-full bg-gradient-to-r">
        <div className="p-6">
          <p className="mb-4 text-lg font-semibold">
            {t("downloadSection.quickStartTitle")}
          </p>
          <div className="grid gap-3 md:grid-cols-3">
            {quickSteps.map((step, index) => (
              <div
                key={index}
                className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white/80 p-4 dark:border-gray-700 dark:bg-gray-900/40"
              >
                <span className="bg-primary-600 inline-flex h-6 w-6 items-center justify-center rounded-full text-sm font-semibold text-white">
                  {index + 1}
                </span>
                <p className="text-sm leading-relaxed">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <div className="mt-6 grid gap-8 md:grid-cols-2">
        {downloadOptions.map((option, index) => {
          const Icon = icons[index] ?? SiFlatpak;
          const url = urls[index] ?? "#";
          const safeFeatures = Array.isArray(option.features)
            ? option.features
            : [];

          return (
            <Card
              key={index}
              className="group hover:-translate-y-2 hover:shadow-xl"
            >
              <div className="p-8">
                <div className="mb-4 flex items-start justify-between">
                  <div className="from-primary-500 to-primary-600 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br transition-transform duration-300 group-hover:scale-110">
                    <Icon className="h-8 w-8 text-white" />
                  </div>
                  <Badge
                    color={
                      index === 0 ? "success" : index === 3 ? "failure" : "gray"
                    }
                    className="ml-2"
                  >
                    {option.badge}
                  </Badge>
                </div>

                <h3 className="mb-3 text-2xl font-bold">{option.title}</h3>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  {option.description}
                </p>

                <div className="mb-6 flex flex-wrap gap-2">
                  {safeFeatures.map((feature, idx) => (
                    <Badge color="indigo" key={idx} className="px-3 py-1">
                      {feature}
                    </Badge>
                  ))}
                </div>

                <Button
                  as="a"
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="from-primary-500 w-full gap-2 bg-gradient-to-r via-green-500 to-green-400 hover:shadow-xl"
                  size="lg"
                >
                  <Download className="h-5 w-5" />
                  {t("downloadSection.download")} {option.title}
                  <ExternalLink className="ml-auto h-4 w-4" />
                </Button>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="mt-8 flex flex-wrap items-center justify-center gap-4 text-sm">
        <span className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-4 py-2 dark:bg-gray-800">
          <ShieldCheck className="h-4 w-4 text-green-600" />
          {t("downloadSection.security.checksum")}
        </span>
        <span className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-4 py-2 dark:bg-gray-800">
          <CheckCheck className="h-4 w-4 text-blue-600" />
          {t("downloadSection.security.opensource")}
        </span>
      </div>
    </Container>
  );
}
