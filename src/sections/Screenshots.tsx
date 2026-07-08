import type { Screenshot } from "../components/ScreenshotCard";
import ScreenshotCard from "../components/ScreenshotCard";

const screenshots = [
    {
        title: "WhatsApp inbox",
        description:
            "Main ZapZap window with account switching, unread counters, conversation filters, and WhatsApp shortcuts.",
        image: "./screenshots/zapzap-main-chat.png",
        alt: "ZapZap showing the WhatsApp inbox with a left account sidebar and conversation list.",
    },
    {
        title: "Account settings",
        description:
            "Manage multiple WhatsApp Web sessions, notification overrides, icons, and User-Agent settings.",
        image: "./screenshots/zapzap-accounts.png",
        alt: "ZapZap settings screen open on the Accounts page.",
    },
    {
        title: "Appearance settings",
        description:
            "Customize interface chrome, theme, tray icon behavior, scale, and window decoration preferences.",
        image: "./screenshots/zapzap-appearance.png",
        alt: "ZapZap settings screen open on the Appearance page in the light theme.",
    },
    {
        title: "Dark theme",
        description:
            "Use the same settings interface with a native-feeling dark theme for low-light environments.",
        image: "./screenshots/zapzap-dark-theme.png",
        alt: "ZapZap settings screen open on the Appearance page in the dark theme.",
    },
    {
        title: "Notifications",
        description:
            "Control desktop notifications, privacy options, contact details, message previews, and ZapZap reminders.",
        image: "./screenshots/zapzap-notifications.png",
        alt: "ZapZap settings screen open on the Notifications page.",
    },
    {
        title: "Privacy and network",
        description:
            "Configure proxy options, per-account scope, host credentials, and WebRTC privacy protections.",
        image: "./screenshots/zapzap-privacy-network.png",
        alt: "ZapZap settings screen open on the Privacy and Network page.",
    },
    {
        title: "Performance experimental",
        description:
            "Tune cache, persistent cookies, GPU rendering, and advanced Chromium behavior when needed.",
        image: "./screenshots/zapzap-performance.png",
        alt: "ZapZap settings screen open on the Performance experimental page.",
    },
] satisfies Screenshot[];

function Screenshots() {
    const [featured, ...items] = screenshots;

    return (
        <section id="screenshots" className="border-t border-hairline bg-background">
            <div className="mx-auto max-w-6xl px-6 py-20">
                <div className="mx-auto max-w-2xl text-center">
                    <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                        Screenshots
                    </p>

                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        See ZapZap in action.
                    </h2>

                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        A quick visual tour of ZapZap, including WhatsApp, accounts,
                        appearance, notifications, privacy, and performance settings.
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