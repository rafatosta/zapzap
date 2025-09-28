import { useEffect, useState } from "react";
import { useTranslation, Trans } from "react-i18next";

export default function LatestRelease(){
  const { t } = useTranslation();
  const [version, setVersion] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("https://api.github.com/repos/rafatosta/zapzap/releases/latest")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch release");
        return res.json();
      })
      .then((data) => setVersion(data.tag_name))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="text-sm text-gray-600 dark:text-gray-200 px-4 py-2">
      {error && <span>{t("latestRelease.error", { error })}</span>}
      {version ? (
        <Trans
          i18nKey="latestRelease.available"
          values={{ version }}
          components={{ 1: <strong /> }}
        />
      ) : (
        <span>{t("latestRelease.loading")}</span>
      )}
    </div>
  );
}
