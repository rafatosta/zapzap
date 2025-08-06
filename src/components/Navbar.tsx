import {
  Avatar,
  Dropdown,
  DropdownHeader,
  Navbar as NavbarFlowbit,
  NavbarBrand,
  NavbarCollapse,
  NavbarToggle,
} from "flowbite-react";
import { DarkThemeToggle } from "flowbite-react";

import zapzapLogo from "/zapzap.svg";
import { useEffect, useState } from "react";
import { scroller, Link } from 'react-scroll';

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false); // 👈 Estado do toggle

  const navigationLinks = [
    { name: "Home", href: "home" },
    { name: "Features", href: "features" },
    { name: "Why ZapZap", href: "why" },
    { name: "Download", href: "download" },
    { name: "Donate", href: "donate" },
    { name: "About", href: "about" },
  ];

  useEffect(() => {
    if (window.location.hash === "#donate") {
      scroller.scrollTo("donate", {
        duration: 500,
        smooth: true,
      });
    }
  }, []);

  return (
    <NavbarFlowbit fluid rounded className="fixed w-full z-50 text-gray-900 dark:text-gray-100">
      <NavbarBrand href="/">
        <img src={zapzapLogo} className="mr-3 h-6 sm:h-9" alt="ZapZap Logo" />
        <span className="self-center whitespace-nowrap text-xl font-semibold">ZapZap</span>
      </NavbarBrand>

      <div className="flex md:order-2 flex-row justify-center items-center gap-4">
        <DarkThemeToggle />
        <Dropdown
          arrowIcon={false}
          inline
          label={
            <Avatar className="hidden lg:flex" alt="User settings" img="https://avatars.githubusercontent.com/u/18619894?v=4" rounded />
          }
        >
          <DropdownHeader>
            <span className="block text-sm">Rafael Tosta</span>
            <span className="block truncate text-sm font-medium">rafa.ecomp@gmail.com</span>
          </DropdownHeader>
        </Dropdown>

        {/* 👇 Alterna o estado do menu */}
        <NavbarToggle onClick={() => setIsOpen(!isOpen)} />
      </div>

      {/* 👇 Aplica o estado controlado manualmente */}
      <NavbarCollapse className={isOpen ? "block" : "hidden"}>
        {navigationLinks.map((link) => (
          <Link
            key={link.name}
            className="text-gray-700 dark:text-gray-100 cursor-pointer p-2"
            to={link.href}
            activeClass="active"
            spy={true}
            hashSpy={true}
            smooth={true}
            duration={500}
            activeStyle={{
              color: '#20ba5b',
              fontWeight: 'bold',
            }}
            onClick={() => setIsOpen(false)} // 👈 Fecha o menu ao clicar
          >
            {link.name}
          </Link>
        ))}
      </NavbarCollapse>
    </NavbarFlowbit>
  );
}
