import {
    Navbar,
    NavbarBrand,
    NavbarCollapse,
    NavbarToggle,
    Button,
} from "flowbite-react";
import { useState } from "react";
import { Link } from "react-scroll";
import zapzapLogo from "/zapzap.svg";
import { LuHeart } from "react-icons/lu";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "./LanguageSwitcher";

interface NavLink {
    name: string;
    href: string;
}

function Header() {
    const { t } = useTranslation();

    const navigationLinks: NavLink[] = [
        { name: t("nav.home"), href: "home" },
        { name: t("nav.features"), href: "features" },
        { name: t("nav.download"), href: "download" },
        { name: t("nav.donate"), href: "donate" },
        { name: t("nav.about"), href: "about" },
    ];

    const [isOpen, setIsOpen] = useState(false);

    return (
        <header className="fixed top-0 w-full z-50 ">
            <Navbar fluid rounded className="bg-white/30 backdrop-blur-md">
                <NavbarBrand href="/">
                    <img
                        src={zapzapLogo}
                        className="mr-3 h-6 sm:h-9"
                        alt="ZapZap Logo"
                    />
                    <span className="self-center whitespace-nowrap text-2xl font-bold bg-gradient-to-r from-primary-400 via-primary-700 via-80% to-primary-900 bg-clip-text text-transparent text-shadow-md">
                        ZapZap
                    </span>
                </NavbarBrand>
                <div className="flex md:order-2 gap-2">
                    <LanguageSwitcher />
                    <Button
                        as="a"
                        href="#donate"
                        color="alternative"
                        size="sm"
                        className="gap-2"
                    >
                        <LuHeart className="w-4 h-4 text-red-500" />
                        {t("button.support")}
                    </Button>
                    <NavbarToggle onClick={() => setIsOpen(!isOpen)} />
                </div>
                <NavbarCollapse className={isOpen ? "block" : "hidden"}>
                    {navigationLinks.map((link) => (
                        <Link
                            key={link.href}
                            className="text-gray-700 dark:text-gray-100 cursor-pointer p-2"
                            to={link.href}
                            activeClass="active"
                            spy={true}
                            hashSpy={true}
                            smooth={true}
                            duration={500}
                            activeStyle={{
                                color: "#20ba5b",
                                fontWeight: "bold",
                                textShadow:
                                    "0px 1px 0px var(--tw-text-shadow-color, rgb(0 0 0 / 0.075)), 0px 1px 1px var(--tw-text-shadow-color, rgb(0 0 0 / 0.075)), 0px 2px 2px var(--tw-text-shadow-color, rgb(0 0 0 / 0.075))",
                            }}
                            onClick={() => setIsOpen(false)}
                        >
                            {link.name}
                        </Link>
                    ))}
                </NavbarCollapse>
            </Navbar>
        </header>
    );
}

export default Header;
