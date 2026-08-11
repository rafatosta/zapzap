import useSWR from "swr";

type FlathubDay = {
  date: string;
  arches: Record<string, [downloads: number, updates: number]>;
};

type FlathubResponse = {
  stats: FlathubDay[];
};

type HistoryDay = {
  date: string;
  downloads: number;
  updates: number;
  installs: number;
};

const fetcher = (url: string): Promise<FlathubResponse> =>
  fetch(url).then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json() as Promise<FlathubResponse>;
  });

export interface FlathubStats {
  totalDownloads: number;
  totalUpdates: number;
  totalInstalls: number;
  downloadsLast30Days: number;
  installsLast30Days: number;
  downloadsLast365Days: number;
  installsLast365Days: number;
  downloadsToday: number;
  installsToday: number;
  averageDownloadsPerDay: number;
  peakDownloads: number;
  peakDownloadsDate: string;
  chartData: Array<Pick<HistoryDay, "date" | "downloads" | "installs">>;
}

const sumBy = (
  history: HistoryDay[],
  field: "downloads" | "updates" | "installs",
) => history.reduce((sum, day) => sum + day[field], 0);

export function useFlathubStats(appId = "com.rtosta.zapzap") {
  const { data, error, isLoading } = useSWR<FlathubResponse>(
    `https://klausenbusk.github.io/flathub-stats/data/${appId}.json`,
    fetcher,
    {
      refreshInterval: 1000 * 60 * 60 * 12,
      revalidateOnFocus: false,
    },
  );

  const stats: FlathubStats | null = data
    ? (() => {
        const history: HistoryDay[] = data.stats.map((day) => {
          let downloads = 0;
          let updates = 0;

          Object.values(day.arches).forEach((arch) => {
            downloads += arch[0];
            updates += arch[1];
          });

          return {
            date: day.date,
            downloads,
            updates,
            installs: downloads - updates,
          };
        });

        const totalDownloads = sumBy(history, "downloads");
        const totalUpdates = sumBy(history, "updates");
        const last30Days = history.slice(-30);
        const last365Days = history.slice(-365);
        const peakDay = history.reduce<HistoryDay | null>(
          (peak, current) =>
            !peak || current.downloads > peak.downloads ? current : peak,
          null,
        );
        const today = history.at(-1);

        return {
          totalDownloads,
          totalUpdates,
          totalInstalls: totalDownloads - totalUpdates,
          downloadsLast30Days: sumBy(last30Days, "downloads"),
          installsLast30Days: sumBy(last30Days, "installs"),
          downloadsLast365Days: sumBy(last365Days, "downloads"),
          installsLast365Days: sumBy(last365Days, "installs"),
          downloadsToday: today?.downloads ?? 0,
          installsToday: today?.installs ?? 0,
          averageDownloadsPerDay: history.length
            ? Math.round(totalDownloads / history.length)
            : 0,
          peakDownloads: peakDay?.downloads ?? 0,
          peakDownloadsDate: peakDay?.date ?? "",
          chartData: history.map(({ date, downloads, installs }) => ({
            date,
            downloads,
            installs,
          })),
        };
      })()
    : null;

  return {
    stats,
    loading: isLoading,
    error: error?.message ?? null,
  };
}
