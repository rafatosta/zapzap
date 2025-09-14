import { useEffect, useState } from "react";
import { Container } from "./Container";
import { Card } from "flowbite-react";

type Contributor = {
  login: string;
  avatar_url: string;
  html_url: string;
};

export default function AboutSection() {
  const [contributors, setContributors] = useState<Contributor[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("https://api.github.com/repos/rafatosta/zapzap/contributors")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch contributors");
        return res.json();
      })
      .then(setContributors)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <Container name="about">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <p className="text-4xl md:text-5xl font-bold mb-6">
          Sobre o <span className="bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent font-semibold">desenvolvimento</span>
        </p>
        <p className="text-xl text-muted-foreground">
          Saiba mais sobre o desenvolvedor e colaboração da comunidade Linux para o desenvolvimento do ZapZap.
        </p>
      </div>

      <div className="mb-6 space-y-4 text-justify">
        <p>
          <strong>ZapZap</strong> is a native-like WhatsApp web wrapper for Linux, offering enhanced features like multi-account support, system tray notifications, drag-and-drop media, spell checking, and dynamic theming.
        </p>
        <p>
          Built with ❤️ by <a href="https://github.com/rafatosta" className="text-blue-600 underline">Rafael Tosta</a>, a developer focused on creating accessible and efficient desktop applications using modern web and desktop technologies.
        </p>
        <p>
          The project is open-source and community-driven. You can find it on{" "}
          <a href="https://github.com/rafatosta/zapzap" className="text-blue-600 underline">GitHub</a> and contribute to its development or improvements.
        </p>
      </div>

      <h2 className="text-2xl font-semibold">Contributors</h2>
      {error && <p className="text-red-500">{error}</p>}
      {!contributors.length && !error && <p>Loading contributors...</p>}

      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-7 gap-2">
        {contributors.map((contributor, index) => (
          <Card
            href={contributor.html_url}
            key={index}
            className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1 \
            dark:border-gray-700 dark:bg-gray-800 border-gray-200 bg-gray-50 \
            ">
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
