import {
    Footer as FooterFlowbite,
    FooterBrand,
    FooterCopyright,
    FooterDivider,
    FooterIcon,
    FooterLink,
    FooterLinkGroup,
    FooterTitle,
    Button,
} from "flowbite-react";

import {
    LuExternalLink as ExternalLink,
    LuHeart as Heart
} from "react-icons/lu";

import zapzapLogo from "/zapzap.svg";
import { BsGithub, BsInstagram } from "react-icons/bs";
import { useTranslation } from "react-i18next";

export default function Footer() {
    const { t } = useTranslation();

    return (
        <FooterFlowbite container>
            <div className="w-full">
                <div className="grid w-full justify-between sm:flex sm:justify-between md:flex md:grid-cols-1">
                    <div>
                        <FooterBrand
                            href="https://rtosta.com/zapzap"
                            src={zapzapLogo}
                            alt={t("footer.brandAlt")}
                            name="ZapZap"
                        />
                        <div className="md:col-span-2 pt-4">
                            <p className="text-muted-foreground leading-relaxed mb-6 max-w-md">
                                {t("footer.description")}
                            </p>
                            <div className="flex space-x-3 pb-6 md:pb-0">
                                <Button
                                    as={"a"}
                                    target="_blank"
                                    href="https://github.com/rafatosta/zapzap"
                                    color="alternative"
                                    size="sm"
                                    className="gap-2"
                                >
                                    <BsGithub className="w-4 h-4" />
                                    GitHub
                                </Button>
                                <Button
                                    as={"a"}
                                    href="#donate"
                                    color="alternative"
                                    size="sm"
                                    className="gap-2"
                                >
                                    <Heart className="w-4 h-4 text-red-500" />
                                    {t("footer.support")}
                                </Button>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-8 sm:mt-4 sm:grid-cols-3 sm:gap-6">
                        <div>
                            <FooterTitle title={t("footer.product")} />
                            <FooterLinkGroup col>
                                <FooterLink href="#home">{t("footer.links.home")}</FooterLink>
                                <FooterLink href="#features">{t("footer.links.features")}</FooterLink>
                                <FooterLink href="#download">{t("footer.links.download")}</FooterLink>
                                <FooterLink href="#about">{t("footer.links.about")}</FooterLink>
                            </FooterLinkGroup>
                        </div>

                        <div>
                            <FooterTitle title={t("footer.community")} />
                            <FooterLinkGroup col>
                                <FooterLink target="_blank" href="https://github.com/rafatosta/zapzap/issues">
                                    <p className="flex items-center gap-1">
                                        {t("footer.links.issues")} <ExternalLink className="w-3 h-3" />
                                    </p>
                                </FooterLink>
                                <FooterLink target="_blank" href="https://github.com/rafatosta/zapzap/releases">
                                    <p className="flex items-center gap-1">
                                        {t("footer.links.releases")} <ExternalLink className="w-3 h-3" />
                                    </p>
                                </FooterLink>
                                <FooterLink target="_blank" href="https://github.com/rafatosta/zapzap?tab=readme-ov-file#">
                                    <p className="flex items-center gap-1">
                                        {t("footer.links.documentation")} <ExternalLink className="w-3 h-3" />
                                    </p>
                                </FooterLink>
                            </FooterLinkGroup>
                        </div>

                        <div>
                            <FooterTitle title={t("footer.legal")} />
                            <FooterLinkGroup col>
                                <FooterLink target="_blank" href="https://github.com/rafatosta/zapzap?tab=GPL-3.0-1-ov-file#">
                                    <p className="flex items-center gap-1">
                                        {t("footer.links.license")} <ExternalLink className="w-3 h-3" />
                                    </p>
                                </FooterLink>
                            </FooterLinkGroup>
                        </div>
                    </div>
                </div>

                <FooterDivider />

                <div className="w-full sm:flex sm:items-center sm:justify-between">
                    <FooterCopyright
                        href="#"
                        by={t("footer.copyright")}
                        year={2022}
                    />
                    <div className="mt-4 flex space-x-6 sm:mt-0 sm:justify-center">
                        <FooterIcon target="_blank" href="https://www.instagram.com/rafatosta_/" icon={BsInstagram} />
                        <FooterIcon target="_blank" href="https://github.com/rafatosta/" icon={BsGithub} />
                    </div>
                </div>
            </div>
        </FooterFlowbite>
    );
}