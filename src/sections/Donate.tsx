function Donate() {


    const donations = [
        {
            title: "GitHub Sponsors",
            body: "Support ZapZap directly through GitHub and help fund long-term open-source development.",
            href: "https://github.com/sponsors/rafatosta",
        },
        {
            title: "Pix",
            body: "Fast and fee-free donations for supporters in Brazil.",
            href: "https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv",
        },

        {
            title: "PayPal",
            body: "A simple and secure way to support ZapZap from anywhere in the world.",
            href: "https://www.paypal.com/donate/?business=E7R4BVR45GRC2",
        },
        {
            title: "Wise",
            body: "International donations with low fees and real exchange rates.",
            href: "https://wise.com/pay/me/rafaelt2487",
        },
        {
            title: "Ko-fi",
            body: "Make a one-time or recurring contribution to keep the project active and improving.",
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
                        Donations
                    </p>

                    <h2 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
                        Help keep ZapZap alive.
                    </h2>

                    <p className="mt-4 text-[15px] leading-relaxed text-muted-foreground">
                        ZapZap is free and open source, maintained in my spare time.
                        If it makes your daily workflow better, consider supporting
                        its continued development.
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
                                    Donate →
                                </span>
                            </a>
                        </li>
                    ))}


                </ul>

                <p className="mt-10 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                    Every contribution helps cover infrastructure costs and gives more
                    time to develop new features, fix issues and keep ZapZap free.
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