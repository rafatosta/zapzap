import useSWR from "swr";

const fetcher = (url: string) =>
  fetch(url).then((res) => res.json());

export function useLatestRelease() {
  const { data } = useSWR(
    "https://api.github.com/repos/rafatosta/zapzap/releases/latest",
    fetcher,
  );

  return data?.tag_name ?? null;
}