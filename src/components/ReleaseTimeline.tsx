// components/ReleaseTimeline.tsx
import {
  Timeline,
  TimelineBody,
  TimelineContent,
  TimelineItem,
  TimelinePoint,
  TimelineTime,
  TimelineTitle,
} from "flowbite-react";
import { useEffect, useState } from "react";

type Release = {
  id: number;
  name: string;
  tag_name: string;
  published_at: string;
  body: string;
};

export default function ReleaseTimeline() {
  const [releases, setReleases] = useState<Release[]>([]);

  useEffect(() => {
    const fetchReleases = async () => {
      try {
        const res = await fetch("https://api.github.com/repos/rafatosta/zapzap/releases");
        const data = await res.json();
        setReleases(data.slice(0, 3)); // <- pega somente as 3 primeiras
      } catch (err) {
        console.error("Erro ao buscar releases:", err);
      }
    };

    fetchReleases();
  }, []);

  return (
    <div className="w-full">
      <h2 className="text-2xl font-semibold mb-4 text-gray-700 dark:text-gray-100">
        Release Timeline
      </h2>
      <Timeline>
        {releases.map((release) => (
          <TimelineItem key={release.id}>
            <TimelinePoint />
            <TimelineContent>
              <TimelineTime>
                {new Date(release.published_at).toLocaleDateString("pt-BR")}
              </TimelineTime>
              <TimelineTitle>{release.name || release.tag_name}</TimelineTitle>
              <TimelineBody>
                <div className="whitespace-pre-line text-sm text-gray-600 dark:text-gray-300">
                  {release.body?.slice(0, 300) || "Sem descrição."}
                  {release.body?.length > 300 && "…"}
                </div>
              </TimelineBody>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </div>
  );
}
