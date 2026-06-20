import useSWR from "swr";

const fetcher = (url: string) =>
  fetch(url).then((r) => {
    if (!r.ok) {
      throw new Error(`HTTP ${r.status}`);
    }

    return r.json();
  });

const formatNumber = (value: number) =>
  new Intl.NumberFormat("pt-BR").format(value);

export interface FlathubStats {
  totalDownloads: string;
  totalUpdates: string;
  totalInstalls: string;

  downloadsLast30Days: string;
  installsLast30Days: string;

  downloadsLast365Days: string;
  installsLast365Days: string;

  downloadsToday: string;
  installsToday: string;

  averageDownloadsPerDay: string;

  peakDownloads: string;
  peakDownloadsDate: string;

  chartData: {
    date: string;
    downloads: number;
    installs: number;
  }[];
}

export function useFlathubStats(
  appId = "com.rtosta.zapzap",
) {
  const { data, error, isLoading } = useSWR(
    `https://klausenbusk.github.io/flathub-stats/data/${appId}.json`,
    fetcher,
    {
      refreshInterval: 1000 * 60 * 60 * 12,
      revalidateOnFocus: false,
    },
  );

  const stats: FlathubStats | null = data
    ? (() => {
        const history = data.stats.map((day: any) => {
          let downloads = 0;
          let updates = 0;

          Object.values(day.arches).forEach(
            (arch: any) => {
              downloads += arch[0];
              updates += arch[1];
            },
          );

          return {
            date: day.date,
            downloads,
            updates,
            installs: downloads - updates,
          };
        });

        const totalDownloads = history.reduce(
          (sum: number, day: any) =>
            sum + day.downloads,
          0,
        );

        const totalUpdates = history.reduce(
          (sum: number, day: any) =>
            sum + day.updates,
          0,
        );

        const totalInstalls =
          totalDownloads - totalUpdates;

        const last30Days = history.slice(-30);
        const last365Days = history.slice(-365);

        const peakDay = history.reduce(
          (max: any, current: any) =>
            current.downloads > max.downloads
              ? current
              : max,
          history[0],
        );

        const today = history.at(-1);

        return {
          totalDownloads:
            formatNumber(totalDownloads),

          totalUpdates:
            formatNumber(totalUpdates),

          totalInstalls:
            formatNumber(totalInstalls),

          downloadsLast30Days: formatNumber(
            last30Days.reduce(
              (sum: number, day: any) =>
                sum + day.downloads,
              0,
            ),
          ),

          installsLast30Days: formatNumber(
            last30Days.reduce(
              (sum: number, day: any) =>
                sum + day.installs,
              0,
            ),
          ),

          downloadsLast365Days: formatNumber(
            last365Days.reduce(
              (sum: number, day: any) =>
                sum + day.downloads,
              0,
            ),
          ),

          installsLast365Days: formatNumber(
            last365Days.reduce(
              (sum: number, day: any) =>
                sum + day.installs,
              0,
            ),
          ),

          downloadsToday: formatNumber(
            today?.downloads ?? 0,
          ),

          installsToday: formatNumber(
            today?.installs ?? 0,
          ),

          averageDownloadsPerDay:
            formatNumber(
              Math.round(
                totalDownloads / history.length,
              ),
            ),

          peakDownloads: formatNumber(
            peakDay.downloads,
          ),

          peakDownloadsDate: peakDay.date,

          chartData: history,
        };
      })()
    : null;

  return {
    stats,
    loading: isLoading,
    error: error?.message ?? null,
  };
}