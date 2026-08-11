import { useI18n } from "../i18n/useI18n";

function Footer() {
    const { t } = useI18n();

    return (
        <footer className="border-t border-hairline">
            <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 px-6 py-10 md:flex-row md:items-center">
                <div className="flex items-center gap-2 text-sm">
                    <span className="inline-block h-2 w-2 rounded-full bg-primary" aria-hidden />
                    <span className="font-semibold tracking-tight">ZapZap</span>
                    <span className="text-muted-foreground">{t("footer.builtBy")}</span>
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
                    <a href="https://github.com/rafatosta/zapzap" target="_blank" rel="noopener noreferrer" className="rounded-sm hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                        GitHub
                    </a>
                    <a href="https://github.com/sponsors/rafatosta" target="_blank" rel="noopener noreferrer" className="rounded-sm hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                        {t("footer.sponsor")}
                    </a>
                    <a href="https://flathub.org/apps/com.rtosta.zapzap" target="_blank" rel="noopener noreferrer" className="rounded-sm hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                        Flathub
                    </a>
                </div>
            </div>
        </footer>
    );
}
export default Footer;
