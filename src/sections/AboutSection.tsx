import { useEffect, useState } from "react";
import { Card } from "flowbite-react";
import { Container } from "../components/Container";
import { useTranslation } from "react-i18next";

type Contributor = {
  login: string;
  avatar_url: string;
  html_url: string;
};

export default function AboutSection() {
  const { t } = useTranslation();
  const [contributors, setContributors] = useState<Contributor[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("https://api.github.com/repos/rafatosta/zapzap/contributors")
      .then((res) => {
        if (!res.ok) throw new Error(t("aboutSection.errorFetch"));
        return res.json();
      })
      .then(setContributors)
      .catch((err) => setError(err.message));
  }, [t]);

  const paragraphs = t("aboutSection.paragraphs", { returnObjects: true }) as string[];

  return (
    <Container name="about">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <p className="text-4xl md:text-5xl font-bold mb-6">
          {t("aboutSection.heading.prefix")}{" "}
          <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent font-semibold">
            {t("aboutSection.heading.highlight")}
          </span>
        </p>
        <p className="text-xl text-muted-foreground">{t("aboutSection.subtitle")}</p>
      </div>

      <div className="mb-6 space-y-4 text-justify">
        {paragraphs.map((p, idx) => (
          <p
            key={idx}
            dangerouslySetInnerHTML={{ __html: p }}
            className="text-muted-foreground"
          />
        ))}
      </div>

      <h2 className="text-2xl font-semibold">{t("aboutSection.contributors")}</h2>
      {error && <p className="text-red-500">{error}</p>}
      {!contributors.length && !error && <p>{t("aboutSection.loading")}</p>}

      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-7 gap-2">
        {contributors.map((contributor, index) => (
          <Card
            href={contributor.html_url}
            key={index}
            className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1 dark:border-gray-700 dark:bg-gray-800 border-gray-200 bg-gray-50"
          >
            <div className="flex flex-col items-center text-center gap-2 justify-center">
              <img
                src={contributor.avatar_url}
                alt={contributor.login}
                className="w-16 h-16 rounded-full"
              />
              <span className="text-sm font-medium">{contributor.login}</span>
            </div>
          </Card>
        ))}
      </div>
    </Container>
  );
}