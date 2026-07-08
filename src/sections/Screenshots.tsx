const screenshots = [
    {
        title: "WhatsApp inbox",
        description: "Main ZapZap window with account switching, unread counters, conversation filters, and WhatsApp shortcuts.",
        image: "./screenshots/zapzap-main-chat.png",
        alt: "ZapZap showing the WhatsApp inbox with a left account sidebar and conversation list.",
    },
    {
        title: "Account settings",
        description: "Manage multiple WhatsApp Web sessions, notification overrides, icons, and User-Agent settings.",
        image: "./screenshots/zapzap-accounts.png",
        alt: "ZapZap settings screen open on the Accounts page.",
    },
    {
        title: "Appearance settings",
        description: "Customize interface chrome, theme, tray icon behavior, scale, and window decoration preferences.",
        image: "./screenshots/zapzap-appearance.png",
        alt: "ZapZap settings screen open on the Appearance page in the light theme.",
    },
    {
        title: "Dark theme",
        description: "Use the same settings interface with a native-feeling dark theme for low-light environments.",
        image: "./screenshots/zapzap-dark-theme.png",
        alt: "ZapZap settings screen open on the Appearance page in the dark theme.",
    },
    {
        title: "Notifications",
        description: "Control desktop notifications, privacy options, contact details, message previews, and ZapZap reminders.",
        image: "./screenshots/zapzap-notifications.png",
        alt: "ZapZap settings screen open on the Notifications page.",
    },
    {
        title: "Privacy and network",
        description: "Configure proxy options, per-account scope, host credentials, and WebRTC privacy protections.",
        image: "./screenshots/zapzap-privacy-network.png",
        alt: "ZapZap settings screen open on the Privacy and Network page.",
    },
    {
        title: "Performance experimental",
        description: "Tune cache, persistent cookies, GPU rendering, and advanced Chromium behavior when needed.",
        image: "./screenshots/zapzap-performance.png",
        alt: "ZapZap settings screen open on the Performance experimental page.",
    },
] as const;

function Screenshots() {
    return (
        <section id="screenshots" className="border-t border-hairline bg-background">
            <div className="mx-auto max-w-6xl px-6 py-24">
                <div className="mx-auto max-w-2xl text-center">
                    <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                        Screenshots
                    </p>

                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        See ZapZap in action.
                    </h2>

                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        A visual tour using real ZapZap screenshots, including the WhatsApp
                        inbox, multi-account settings, notifications, privacy, performance,
                        and light or dark appearance preferences.
                    </p>
                </div>

                <div className="mt-14 grid gap-6 md:grid-cols-2">
                    {screenshots.map((screenshot, index) => (
                        <article
                            key={screenshot.title}
                            className={`group overflow-hidden rounded-2xl border border-border bg-card ${
                                index === 0 ? "md:col-span-2" : ""
                            }`}
                        >
                            <a
                                href={screenshot.image}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block bg-gradient-to-br from-primary/15 via-secondary to-transparent p-3 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                                aria-label={`Open full-size screenshot: ${screenshot.title}`}
                            >
                                <img
                                    src={screenshot.image}
                                    alt={screenshot.alt}
                                    loading={index < 2 ? "eager" : "lazy"}
                                    className="aspect-[16/10] w-full rounded-xl border border-border bg-background object-cover object-left-top shadow-2xl shadow-black/10 transition duration-300 group-hover:scale-[1.01]"
                                />
                            </a>

                            <div className="border-t border-hairline p-5">
                                <h3 className="text-lg font-semibold tracking-tight">
                                    {screenshot.title}
                                </h3>

                                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                                    {screenshot.description}
                                </p>
                            </div>
                        </article>
                    ))}
                </div>
            </div>
        </section>
    );
}

export default Screenshots;
