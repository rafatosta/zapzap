import type { Screenshot } from "../components/ScreenshotCard";
import ScreenshotCard from "../components/ScreenshotCard";
import { useI18n } from "../i18n/useI18n";

function Screenshots() {
    const { t } = useI18n();
    const screenshots = [
        {
            title: t("screenshots.inbox.title"),
            description: t("screenshots.inbox.body"),
            image: "./screenshots/zapzap-main-chat.png",
            alt: t("screenshots.inbox.alt"),
        },
        {
            title: t("screenshots.accounts.title"),
            description: t("screenshots.accounts.body"),
            image: "./screenshots/zapzap-accounts.png",
            alt: t("screenshots.accounts.alt"),
        },
        {
            title: t("screenshots.appearance.title"),
            description: t("screenshots.appearance.body"),
            image: "./screenshots/zapzap-appearance.png",
            alt: t("screenshots.appearance.alt"),
        },
        {
            title: t("screenshots.dark.title"),
            description: t("screenshots.dark.body"),
            image: "./screenshots/zapzap-dark-theme.png",
            alt: t("screenshots.dark.alt"),
        },
        {
            title: t("screenshots.notifications.title"),
            description: t("screenshots.notifications.body"),
            image: "./screenshots/zapzap-notifications.png",
            alt: t("screenshots.notifications.alt"),
        },
        {
            title: t("screenshots.privacy.title"),
            description: t("screenshots.privacy.body"),
            image: "./screenshots/zapzap-privacy-network.png",
            alt: t("screenshots.privacy.alt"),
        },
        {
            title: t("screenshots.performance.title"),
            description: t("screenshots.performance.body"),
            image: "./screenshots/zapzap-performance.png",
            alt: t("screenshots.performance.alt"),
        },
    ] satisfies Screenshot[];
    const [featured, ...items] = screenshots;

    return (
        <section id="screenshots" className="border-t border-hairline bg-background">
            <div className="mx-auto max-w-6xl px-6 py-20">
                <div className="mx-auto max-w-2xl text-center">
                    <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                        {t("screenshots.eyebrow")}
                    </p>

                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        {t("screenshots.title")}
                    </h2>

                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        {t("screenshots.description")}
                    </p>
                </div>

                <div className="mt-12">
                    <ScreenshotCard screenshot={featured} featured />
                </div>

                <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {items.map((screenshot) => (
                        <ScreenshotCard
                            key={screenshot.title}
                            screenshot={screenshot}
                        />
                    ))}
                </div>
            </div>
        </section>
    );
}

export default Screenshots;
