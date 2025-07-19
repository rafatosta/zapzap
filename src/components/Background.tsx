import { DarkThemeToggle } from "flowbite-react";

/* import patternLight from "/pattern-light.svg";
import patternDark from "/pattern-dark.svg"; */
import zapzapLogo from "/zapzap.svg";

function Background() {
  return (
    <>
      <div className="fixed inset-0 size-full">
        <div className="relative h-full w-full select-none">
          {/* Background */}
          {/* <img
            className="absolute right-0 min-w-dvh dark:hidden"
            alt="Pattern Light"
            src={patternLight}
          />
          <img
            className="absolute right-0 hidden min-w-dvh dark:block"
            alt="Pattern Dark"
            src={patternDark}
          /> */}

          {/* Central */}
          <div
            className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none"
            aria-hidden="true"
          >
            <img
              src={zapzapLogo}
              alt="Zapzap Watermark"
              className="w-3/4 max-w-md"
            />
          </div>
        </div>
      </div>

      {/* Theme Toggle */}
      <div className="fixed top-4 right-4 z-50">
        <DarkThemeToggle />
      </div>
    </>
  );
}

export default Background;
