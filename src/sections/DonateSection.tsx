import { FaPaypal, FaPix } from "react-icons/fa6";
import { SiKofi, SiGithubsponsors } from "react-icons/si";
import { Container } from "../components/Container";
import { Trans, useTranslation } from "react-i18next";
import { SiWise } from "react-icons/si";

import { DonateCard } from "../components/DonateCard";
import { PixModalContent } from "../components/PixModalContent";

import qrPix from "/qr-pix.png";

function DonationSection() {
  const { t } = useTranslation();

  const donationOptions = [
    {
      type: "link" as const,
      icon: SiWise,
      title: t("donationSection.options.wise.title"),
      description: t("donationSection.options.wise.description"),
      badge: t("donationSection.options.wise.badge"),
      badgeVariant: "success" as const,
      url: "https://wise.com/pay/me/rafaelt2487",
      features: t("donationSection.options.wise.features", {
        returnObjects: true,
      }) as string[],
      colors: {
        iconBg: "from-green-400 to-emerald-600",
        buttonBg: "from-green-400 via-emerald-500 to-teal-400",
      },
    },
    {
      type: "modal" as const,
      icon: FaPix,
      title: t("donationSection.options.pix.title"),
      description: t("donationSection.options.pix.description"),
      badge: t("donationSection.options.pix.badge"),
      badgeVariant: "success" as const,
      features: t("donationSection.options.pix.features", {
        returnObjects: true,
      }) as string[],
      colors: {
        iconBg: "from-green-500 to-green-600",
        buttonBg: "from-green-500 via-emerald-500 to-lime-400",
      },

      // 👇 dados específicos do modal
      qrCodeUrl: qrPix,
      pixOptions: [
        {
          label: "c86378c4-c34a-4951-bad0-42d5c1774f79",
          value: "c86378c4-c34a-4951-bad0-42d5c1774f79",
        },
      ],
    },
    {
      type: "link" as const,
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
      type: "link" as const,
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
      type: "link" as const,
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
          <DonateCard
            key={index}
            title={option.title}
            description={option.description}
            features={option.features}
            icon={option.icon}
            badge={option.badge}
            badgeColor={option.badgeVariant}
            buttonLabel={t("donationSection.button", {
              method: option.title,
            })}
            colors={option.colors}
            action={
              option.type === "modal"
                ? { type: "modal" }
                : { type: "link", url: option.url }
            }
            modalContent={
              option.type === "modal" ? (
                <PixModalContent
                  qrCodeUrl={option.qrCodeUrl}
                  pixOptions={option.pixOptions}
                />
              ) : undefined
            }
          />
        ))}
      </div>
    </Container>
  );
}

export default DonationSection;