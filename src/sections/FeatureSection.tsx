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
  LuDownload as Download,
  LuCheck as CheckCircle,
} from "react-icons/lu";
import { Container } from "../components/Container";
import { useTranslation, Trans } from "react-i18next";
import { IconType } from "react-icons";

type FeatureItem = {
  title: string;
  description: string;
};

function FeatureSection() {
  const { t } = useTranslation();

  const features = t("featureSection.features", {
    returnObjects: true,
  }) as FeatureItem[];

  const featureIcons: IconType[] = [
    Users,
    Bell,
    Share2,
    Palette,
    Shield,
    Monitor,
  ];

  const whyChoose = t("featureSection.whyChoose", {
    returnObjects: true,
  }) as FeatureItem[];
  const whyChooseIcons: IconType[] = [Zap, Smartphone, Download];

  const highlights = t("featureSection.highlights", {
    returnObjects: true,
  }) as string[];

  return (
    <Container name="features">
      <div className="mx-auto mb-16 max-w-3xl text-center">
        <p className="mb-6 text-4xl font-bold md:text-5xl">
          <Trans
            i18nKey="featureSection.heading"
            components={{
              1: (
                <span className="from-primary-400 via-primary-700 to-primary-900 bg-gradient-to-r via-80% bg-clip-text font-semibold text-transparent" />
              ),
            }}
          />
        </p>
        <p className="text-muted-foreground text-xl">
          {t("featureSection.subtitle")}
        </p>
      </div>

      <div className="mb-10 flex flex-wrap justify-center gap-3">
        {highlights.map((item, index) => (
          <span
            key={index}
            className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-sm dark:bg-gray-800"
          >
            <CheckCircle className="h-4 w-4 text-green-500" />
            {item}
          </span>
        ))}
      </div>

      <div className="mb-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {features.map((feature, index) => {
          const Icon = featureIcons[index] ?? Users;
          return (
            <Card
              key={index}
              className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="p-6 text-center">
                <div className="from-primary-500 to-primary-600 mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br">
                  <Icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="mb-3 text-xl font-semibold">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {whyChoose.map((item, index) => {
          const Icon = whyChooseIcons[index] ?? Zap;
          return (
            <div key={index} className="text-center lg:text-left">
              <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-blue-500 to-blue-600 lg:mx-0">
                <Icon className="h-10 w-10 text-white" />
              </div>
              <h3 className="mb-4 text-2xl font-bold">{item.title}</h3>
              <p className="text-muted-foreground">{item.description}</p>
            </div>
          );
        })}
      </div>
    </Container>
  );
}

export default FeatureSection;
