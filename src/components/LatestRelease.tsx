import { useEffect, useState } from "react";

export default function LatestRelease() {
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
        <div className="text-sm text-gray-600 dark:text-gray-200 mt-2">
            {error && <span>Error: {error}</span>}
            {version ? <span>Latest version: <strong>{version}</strong></span> : <span>Loading version...</span>}
        </div>
    );
}
