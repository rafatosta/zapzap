import useSWR from "swr";

type GitHubRelease = {
  tag_name: string;
};

const fetcher = (url: string): Promise<GitHubRelease> =>
  fetch(url).then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json() as Promise<GitHubRelease>;
  });

export function useLatestRelease() {
  const { data, error, isLoading } = useSWR<GitHubRelease>(
    "https://api.github.com/repos/rafatosta/zapzap/releases/latest",
    fetcher,
  );

  return {
    version: data?.tag_name ?? null,
    loading: isLoading,
    error: error?.message ?? null,
  };
}
