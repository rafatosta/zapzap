
import {
  Avatar,
  Dropdown,
  DropdownHeader,
  Navbar as NavbarFlowbit,
  NavbarBrand,
  NavbarCollapse,
  NavbarLink,
  NavbarToggle,
} from "flowbite-react";


import { DarkThemeToggle } from "flowbite-react";


import zapzapLogo from "/zapzap.svg";
import { useEffect } from "react";
import { scroller, Link } from 'react-scroll';

export function Navbar() {

  const navigationLinks = [
    { name: "Home", href: "home" },
    { name: "Features", href: "features" },
    { name: "Why ZapZap", href: "why" },
    { name: "Download", href: "download" },
    { name: "Donate", href: "donate" },
    { name: "About", href: "about" },
  ];

  useEffect(() => {
    if (window.location.hash == "#donate") {
      scroller.scrollTo('#donate', {
        duration: 500,
        smooth: true,
      })
    }
  }, [])


  return (
    <NavbarFlowbit fluid rounded className="fixed w-full z-50  text-gray-900 dark:text-gray-100">
      <NavbarBrand href="/">
        <img src={zapzapLogo} className="mr-3 h-6 sm:h-9" alt="ZapZap Logo" />
        <span className="self-center whitespace-nowrap text-xl font-semibold">ZapZap</span>
      </NavbarBrand>
      <div className="hidden lg:flex md:order-2 flex-row justify-center items-center gap-4">
        <DarkThemeToggle />

        <Dropdown
          arrowIcon={false}
          inline
          label={
            <Avatar alt="User settings" img="https://avatars.githubusercontent.com/u/18619894?v=4" rounded />
          }
        >
          <DropdownHeader>
            <span className="block text-sm">Rafael Tosta</span>
            <span className="block truncate text-sm font-medium">rafa.ecomp@gmail.com</span>
          </DropdownHeader>
        </Dropdown>
        <NavbarToggle />
      </div>
      <NavbarCollapse>
        {navigationLinks.map((link) => (
          <NavbarLink>
            <Link key={link.name}
              className="text-gray-700 dark:text-gray-100 cursor-pointer"
              to={link.href}
              activeClass="active"
              spy={true}
              hashSpy={true}
              smooth={true}
              duration={500}
              activeStyle={{
                color: '#20ba5b',
                fontWeight: 'bold'
              }}

            >
              {link.name}
            </Link>
          </NavbarLink>

        ))}
      </NavbarCollapse>
    </NavbarFlowbit>
  );
}