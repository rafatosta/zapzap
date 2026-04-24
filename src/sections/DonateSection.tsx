import {
  LuHeartHandshake as Heart,
  LuExternalLink as ExternalLink,
} from "react-icons/lu";
import { FaPaypal, FaPix } from "react-icons/fa6";
import { SiKofi, SiGithubsponsors } from "react-icons/si";
import { Badge, Button, Card } from "flowbite-react";
import { Container } from "../components/Container";
import { Trans, useTranslation } from "react-i18next";

function DonationSection() {
  const { t } = useTranslation();

  const donationOptions = [
    {
      icon: FaPix,
      title: t("donationSection.options.pix.title"),
      description: t("donationSection.options.pix.description"),
      badge: t("donationSection.options.pix.badge"),
      badgeVariant: "success" as const,
      url: "https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv",
      features: t("donationSection.options.pix.features", {
        returnObjects: true,
      }) as string[],
      colors: {
        iconBg: "from-green-500 to-green-600",
        buttonBg: "from-green-500 via-emerald-500 to-lime-400",
      },
    },
    {
      icon: FaPaypal,
      title: t("donationSection.options.paypal.title"),
      description: t("donationSection.options.paypal.description"),
      badge: t("donationSection.options.paypal.badge"),
      badgeVariant: "gray" as const,
      url: "https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux&currency_code=USD",
      features: t("donationSection.options.paypal.features", {
        returnObjects: true,
      }) as string[],
      colors: {
        iconBg: "from-blue-500 to-blue-600",
        buttonBg: "from-blue-500 via-sky-500 to-cyan-400",
      },
    },
    {
      icon: SiKofi,
      title: t("donationSection.options.kofi.title"),
      description: t("donationSection.options.kofi.description"),
      badge: t("donationSection.options.kofi.badge"),
      badgeVariant: "indigo" as const,
      url: "https://ko-fi.com/rafaeltosta",
      features: t("donationSection.options.kofi.features", {
        returnObjects: true,
      }) as string[],
      colors: {
        iconBg: "from-sky-400 to-sky-600",
        buttonBg: "from-sky-400 via-cyan-500 to-blue-400",
      },
    },
    {
      icon: SiGithubsponsors,
      title: t("donationSection.options.githubSponsors.title"),
      description: t("donationSection.options.githubSponsors.description"),
      badge: t("donationSection.options.githubSponsors.badge"),
      badgeVariant: "failure" as const,
      url: "https://github.com/sponsors/rafatosta",
      features: t("donationSection.options.githubSponsors.features", {
        returnObjects: true,
      }) as string[],
      colors: {
        iconBg: "from-pink-500 to-rose-600",
        buttonBg: "from-pink-500 via-rose-500 to-red-400",
      },
    },
  ];

  return (
    <Container name="donate">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="mb-6 text-4xl font-bold md:text-5xl">
          <Trans
            i18nKey="donationSection.heading"
            components={{
              1: (
                <span className="from-primary-400 via-primary-700 to-primary-900 bg-gradient-to-r via-80% bg-clip-text font-semibold text-transparent" />
              ),
            }}
          />
        </h2>
        <p className="text-muted-foreground text-xl leading-relaxed">
          {t("donationSection.subtitle")}
        </p>
      </div>

      <div className="mt-6 grid gap-8 md:grid-cols-2">
        {donationOptions.map((option, index) => (
          <Card
            key={index}
            className="group hover:-translate-y-2 hover:shadow-xl"
          >
            <div className="p-8">
              <div className="mb-4 flex items-start justify-between">
                <div
                  className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${option.colors.iconBg} flex items-center justify-center transition-transform duration-300 group-hover:scale-110`}
                >
                  <option.icon className="h-8 w-8 text-white" />
                </div>
                <Badge color={option.badgeVariant} className="ml-2">
                  {option.badge}
                </Badge>
              </div>

              <h3 className="mb-3 text-2xl font-bold">{option.title}</h3>
              <p className="text-muted-foreground mb-6 leading-relaxed">
                {option.description}
              </p>

              <div className="mb-6 flex flex-wrap gap-2">
                {option.features.map((feature, idx) => (
                  <Badge color="indigo" key={idx} className="px-3 py-1">
                    {feature}
                  </Badge>
                ))}
              </div>

              <Button
                as="a"
                href={option.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`w-full gap-2 bg-gradient-to-r hover:shadow-xl ${option.colors.buttonBg}`}
                size="lg"
              >
                <Heart className="h-5 w-5" />
                {t("donationSection.button", { method: option.title })}
                <ExternalLink className="ml-auto h-4 w-4" />
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </Container>
  );
}

export default DonationSection;
