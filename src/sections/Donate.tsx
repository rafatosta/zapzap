import { useI18n } from "../i18n/useI18n";

function Donate() {
    const { t } = useI18n();

    const donations = [
        {
            title: "GitHub Sponsors",
            body: t("donate.github"),
            href: "https://github.com/sponsors/rafatosta",
        },
        {
            title: "Pix",
            body: t("donate.pix"),
            href: "https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv",
        },

        {
            title: "PayPal",
            body: t("donate.paypal"),
            href: "https://www.paypal.com/donate/?business=E7R4BVR45GRC2",
        },
        {
            title: "Wise",
            body: t("donate.wise"),
            href: "https://wise.com/pay/me/rafaelt2487",
        },
        {
            title: "Ko-fi",
            body: t("donate.kofi"),
            href: "https://ko-fi.com/rafaeltosta",
        },
    ];

    const cardClass =
        "group block h-full rounded-xl border border-transparent bg-subtle p-5 text-left transition-all duration-200 hover:-translate-y-1 hover:border-border hover:bg-card hover:shadow-sm";

    return (
        <section id="donate" className="border-t border-hairline bg-subtle">
            <div className="mx-auto max-w-6xl px-6 py-24">
                <div className="max-w-2xl">
                    <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                        {t("donate.eyebrow")}
                    </p>

                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        {t("donate.title")}
                    </h2>

                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        {t("donate.description")}
                    </p>
                </div>

                <ul className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    {donations.map((item, index) => (
                        <li key={item.title}>
                            <a
                                href={item.href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={cardClass}
                            >
                                <DonateCard index={index} title={item.title} body={item.body} />
                                <span className="mt-4 inline-flex text-sm font-medium group-hover:text-foreground">
                                    {t("donate.action")} →
                                </span>
                            </a>
                        </li>
                    ))}


                </ul>

                <p className="mt-10 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                    {t("donate.footer")}
                </p>
            </div>
        </section>
    );
}

function DonateCard({
    index,
    title,
    body,
}: {
    index: number;
    title: string;
    body: string;
}) {
    return (
        <div className="border-t border-hairline pt-5">
            <div className="flex items-center gap-3">
                <span className="font-mono text-[11px] tabular-nums text-muted-foreground transition-colors group-hover:text-foreground">
                    {String(index + 1).padStart(2, "0")}
                </span>

                <h3 className="text-[15px] font-semibold tracking-tight">
                    {title}
                </h3>
            </div>

            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {body}
            </p>
        </div>
    );
}

export default Donate;
