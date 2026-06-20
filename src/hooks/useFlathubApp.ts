import useSWR from "swr";

const fetcher = async (url: string) => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
};

function formatTimestamp(timestamp?: string) {
  if (!timestamp) {
    return "—";
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "long",
  }).format(new Date(Number(timestamp) * 1000));
}

export interface FlathubApp {
  id: string;
  name: string;
  summary: string;
  developer: string;

  version: string;
  releaseDate: string;

  verified: boolean;
  verifiedLabel: string;

  homepage: string | null;
  donation: string | null;
  bugtracker: string | null;

  icon: string | null;
  screenshot: string | null;

  categories: string[];
  keywords: string[];

  license: string;
  runtime: string;

  mobileFriendly: boolean;
  eol: boolean;
}

export function useFlathubApp(appId: string) {
  const { data, error, isLoading } = useSWR(
    `https://flathub.org/api/v2/appstream/${appId}`,
    fetcher,
    {
      refreshInterval: 1000 * 60 * 60,
      revalidateOnFocus: false,
    }
  );

  const app: FlathubApp | null = data
    ? {
        id: data.id,

        name: data.name ?? "—",
        summary: data.summary ?? "—",

        developer: data.developer_name ?? "—",

        version: data.releases?.[0]?.version ?? "—",

        releaseDate: formatTimestamp(
          data.releases?.[0]?.timestamp
        ),

        verified:
          data.metadata?.[
            "flathub::verification::verified"
          ] === true,

        verifiedLabel:
          data.metadata?.[
            "flathub::verification::verified"
          ]
            ? "Verified"
            : "Not verified",

        homepage: data.urls?.homepage ?? null,

        donation: data.urls?.donation ?? null,

        bugtracker: data.urls?.bugtracker ?? null,

        icon: data.icon ?? null,

        screenshot:
          data.screenshots?.[0]?.sizes?.[0]?.src ?? null,

        categories: data.categories ?? [],

        keywords: data.keywords ?? [],

        license: data.project_license ?? "—",

        runtime: data.bundle?.runtime ?? "—",

        mobileFriendly:
          data.isMobileFriendly ?? false,

        eol: data.is_eol ?? false,
      }
    : null;

  return {
    app,
    loading: isLoading,
    error: error?.message ?? null,
  };
}