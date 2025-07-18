import { useEffect, useState } from "react";

type Contributor = {
  login: string;
  avatar_url: string;
  html_url: string;
};

export default function About() {
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
    <div className="relative flex w-full max-w-5xl flex-col items-center justify-center gap-12">
      <div className="relative flex flex-col items-center gap-6">
        <h1 className="relative text-center text-3xl leading-[125%] font-bold text-shadow-lg">
          About ZapZap
        </h1>
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
        {contributors.map((contributor) => (
          <a
            key={contributor.login}
            href={contributor.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex flex-col items-center text-center p-3 rounded-lg hover:shadow-md 
            border dark:border-gray-700 dark:bg-gray-800 border-gray-200 bg-gray-50"
          >
            <img
              src={contributor.avatar_url}
              alt={contributor.login}
              className="w-16 h-16 rounded-full mb-2"
            />
            <span className="text-sm font-medium">{contributor.login}</span>
          </a>
        ))}
      </div>
    </div>
  );
}
