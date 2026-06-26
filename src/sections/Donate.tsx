import * as Dialog from "@radix-ui/react-dialog";
import { useState } from "react";
import qrPix from "/qr-pix.png";

const PIX_KEY = "c86378c4-c34a-4951-bad0-42d5c1774f79";


function Donate() {

    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(PIX_KEY);

        setCopied(true);

        setTimeout(() => setCopied(false), 2000);
    };

    const donations = [
        {
            title: "GitHub Sponsors",
            body: "Support ZapZap directly through GitHub and help fund long-term open-source development.",
            href: "https://github.com/sponsors/rafatosta",
        },
        {
            title: "Ko-fi",
            body: "Make a one-time or recurring contribution to keep the project active and improving.",
            href: "https://ko-fi.com/rafaeltosta",
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

                    <li>
                        <Dialog.Root>
                            <Dialog.Trigger className={cardClass}>
                                <DonateCard
                                    index={4}
                                    title="Pix"
                                    body="Fast and fee-free donations for supporters in Brazil."
                                />
                                <span className="mt-4 inline-flex text-sm font-medium group-hover:text-foreground">
                                    Donate →
                                </span>
                            </Dialog.Trigger>

                            <Dialog.Portal>
                                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50" />

                                <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-2xl -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-xl border border-border bg-background shadow-lg">
                                    <div className="flex items-center justify-between border-b border-hairline px-6 py-5">
                                        <Dialog.Title className="text-xl font-semibold tracking-tight">
                                            Pix
                                        </Dialog.Title>

                                        <Dialog.Close className="text-2xl leading-none text-muted-foreground transition-colors hover:text-foreground">
                                            ×
                                        </Dialog.Close>
                                    </div>

                                    <div className="px-6 py-10 text-center">
                                        <Dialog.Description className="sr-only">
                                            Donate to ZapZap using Pix QR Code or Pix key.
                                        </Dialog.Description>

                                        <h3 className="text-2xl font-semibold tracking-tight">
                                            Use the Pix QR Code to donate
                                        </h3>

                                        <p className="mx-auto mt-4 max-w-xl text-[15px] leading-relaxed text-muted-foreground">
                                            Open your banking app, scan the QR Code or copy the Pix key below.
                                        </p>

                                        <div className="mx-auto mt-8 flex h-64 w-64 items-center justify-center rounded-2xl bg-subtle p-5">
                                            <img
                                                src={qrPix}
                                                alt="Pix QR Code"
                                                className="h-full w-full bg-white object-contain"
                                            />
                                        </div>

                                        <div className="mt-8 text-left">
                                            <label className="text-sm font-medium">
                                                Pix Key
                                            </label>

                                            <code className="mt-3 block overflow-hidden rounded-md border border-border bg-card px-3 py-3 font-mono text-sm text-muted-foreground">
                                                {PIX_KEY}
                                            </code>

                                            <button
                                                type="button"
                                                onClick={handleCopy}
                                                className="mt-4 w-full rounded-md border border-border px-4 py-3 text-sm font-medium transition-all"
                                            >
                                                <span
                                                    className={`transition-opacity ${copied ? "text-green-600" : ""
                                                        }`}
                                                >
                                                    {copied ? "✓ Pix Key Copied" : "Copy Pix Key"}
                                                </span>
                                            </button>
                                        </div>
                                    </div>
                                </Dialog.Content>
                            </Dialog.Portal>
                        </Dialog.Root>
                    </li>
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