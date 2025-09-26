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
import { Container } from "../components/Container";
import { useTranslation, Trans } from "react-i18next";

function FeatureSection() {
  const { t } = useTranslation();

  const features = t("featureSection.features", { returnObjects: true }) as {
    title: string;
    description: string;
    icon: any;
  }[];

  // Reatribuir os ícones correspondentes
  const featureIcons = [Users, Bell, Share2, Palette, Shield, Monitor];
  features.forEach((f, i) => f.icon = featureIcons[i]);

  const whyChoose = t("featureSection.whyChoose", { returnObjects: true }) as { title: string; description: string }[];
  const whyChooseIcons = [Zap, Smartphone, Download];

  return (
    <Container name="features">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <p className="text-4xl md:text-5xl font-bold mb-6">
          <Trans i18nKey="featureSection.heading" components={{ 1: <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent font-semibold" /> }} />
        </p>
        <p className="text-xl text-muted-foreground">{t("featureSection.subtitle")}</p>
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

      <div className="grid lg:grid-cols-3 gap-8">
        {whyChoose.map((item, index) => {
          const Icon = whyChooseIcons[index];
          return (
            <div key={index} className="text-center lg:text-left">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500 to-blue-600 mx-auto lg:mx-0 mb-6 flex items-center justify-center">
                <Icon className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4">{item.title}</h3>
              <p className="text-muted-foreground">{item.description}</p>
            </div>
          );
        })}
      </div>
    </Container>
  );
}

export default FeatureSection;
