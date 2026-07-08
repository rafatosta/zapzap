import * as Dialog from "@radix-ui/react-dialog";

export type Screenshot = {
    title: string;
    description: string;
    image: string;
    alt: string;
};

type ScreenshotCardProps = {
    screenshot: Screenshot;
    featured?: boolean;
};

function ScreenshotCard({
    screenshot,
    featured = false,
}: ScreenshotCardProps) {
    return (
        <Dialog.Root>
            <figure className="group overflow-hidden rounded-2xl border border-border bg-card">
                <Dialog.Trigger asChild>
                    <button
                        type="button"
                        className="block w-full cursor-zoom-in bg-gradient-to-br from-primary/10 via-secondary to-transparent p-2 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                        aria-label={`Open screenshot: ${screenshot.title}`}
                    >
                        <img
                            src={screenshot.image}
                            alt={screenshot.alt}
                            loading={featured ? "eager" : "lazy"}
                            className={`w-full rounded-xl border border-border bg-background object-cover object-left-top shadow-xl shadow-black/10 transition duration-300 group-hover:scale-[1.01] ${featured ? "aspect-[16/9]" : "aspect-[16/10]"
                                }`}
                        />
                    </button>
                </Dialog.Trigger>

                <figcaption className="border-t border-hairline p-4">
                    <h3
                        className={
                            featured
                                ? "text-lg font-semibold tracking-tight"
                                : "text-sm font-semibold tracking-tight"
                        }
                    >
                        {screenshot.title}
                    </h3>

                    <p
                        className={`mt-1 leading-relaxed text-muted-foreground ${featured ? "text-sm" : "line-clamp-2 text-xs"
                            }`}
                    >
                        {screenshot.description}
                    </p>
                </figcaption>
            </figure>

            <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />

                <Dialog.Content className="fixed left-1/2 top-1/2 z-50 grid max-h-[90vh] w-[calc(100vw-2rem)] max-w-6xl -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-2xl border border-border bg-card shadow-2xl focus:outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
                    <div className="flex items-start justify-between gap-4 border-b border-hairline px-5 py-4">
                        <div>
                            <Dialog.Title className="text-base font-semibold tracking-tight">
                                {screenshot.title}
                            </Dialog.Title>

                            <Dialog.Description className="mt-1 max-w-3xl text-sm leading-relaxed text-muted-foreground">
                                {screenshot.description}
                            </Dialog.Description>
                        </div>

                        <Dialog.Close asChild>
                            <button
                                type="button"
                                className="inline-flex size-9 shrink-0 items-center justify-center rounded-full border border-border bg-background text-lg leading-none text-muted-foreground transition hover:bg-secondary hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                                aria-label="Close screenshot dialog"
                            >
                                ×
                            </button>
                        </Dialog.Close>
                    </div>

                    <div className="max-h-[calc(90vh-88px)] overflow-auto bg-background p-3">
                        <img
                            src={screenshot.image}
                            alt={screenshot.alt}
                            className="mx-auto h-auto w-full rounded-xl border border-border bg-background object-contain"
                        />
                    </div>
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    );
}

export default ScreenshotCard;