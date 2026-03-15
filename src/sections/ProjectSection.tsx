import { Badge, Card } from "flowbite-react";
import { useTranslation } from "react-i18next";
import { Container } from "../components/Container";
import {
  LuShieldCheck as ShieldCheck,
  LuGitBranch as GitBranch,
  LuUsers as Users,
  LuCalendarClock as CalendarClock,
  LuCircleHelp as CircleHelp,
} from "react-icons/lu";

export default function ProjectSection() {
  const { t } = useTranslation();

  const trustItems = t("projectSection.trust.items", {
    returnObjects: true,
  }) as Array<{ title: string; description: string }>;

  const roadmapItems = t("projectSection.roadmap.items", {
    returnObjects: true,
  }) as Array<{ title: string; description: string; status: string }>;

  const faqItems = t("projectSection.faq.items", {
    returnObjects: true,
  }) as Array<{ question: string; answer: string }>;

  const trustIcons = [Users, GitBranch, ShieldCheck];

  return (
    <Container name="project">
      <div className="mx-auto mb-8 max-w-3xl text-center">
        <h2 className="mb-5 text-4xl font-bold md:text-5xl">
          <span className="from-primary-400 via-primary-700 to-primary-900 bg-gradient-to-r bg-clip-text text-transparent">
            {t("projectSection.heading")}
          </span>
        </h2>
        <p className="text-muted-foreground text-lg md:text-xl">
          {t("projectSection.subtitle")}
        </p>
      </div>

      <div className="mb-12 grid gap-6 md:grid-cols-3">
        {trustItems.map((item, index) => {
          const Icon = trustIcons[index] ?? ShieldCheck;
          return (
            <Card
              key={index}
              className="border-primary-100 dark:border-primary-900"
            >
              <div className="p-5">
                <div className="bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300 mb-3 inline-flex rounded-xl p-3">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mb-2 text-xl font-semibold">{item.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {item.description}
                </p>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <Card>
          <div className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <CalendarClock className="text-primary-600 h-5 w-5" />
              <h3 className="text-2xl font-bold">
                {t("projectSection.roadmap.title")}
              </h3>
            </div>
            <div className="space-y-4">
              {roadmapItems.map((item, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 p-4 dark:border-gray-700"
                >
                  <div className="mb-2 flex items-start justify-between gap-2">
                    <p className="font-semibold">{item.title}</p>
                    <Badge color="indigo">{item.status}</Badge>
                  </div>
                  <p className="text-muted-foreground text-sm">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <CircleHelp className="text-primary-600 h-5 w-5" />
              <h3 className="text-2xl font-bold">
                {t("projectSection.faq.title")}
              </h3>
            </div>
            <div className="space-y-3">
              {faqItems.map((item, index) => (
                <details
                  key={index}
                  className="rounded-lg border border-gray-200 p-4 dark:border-gray-700"
                >
                  <summary className="cursor-pointer font-medium">
                    {item.question}
                  </summary>
                  <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                    {item.answer}
                  </p>
                </details>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </Container>
  );
}
