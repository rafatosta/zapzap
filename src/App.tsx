import { DarkThemeToggle } from "flowbite-react";

import patternLight from "/pattern-light.svg"
import patternDark from "/pattern-dark.svg"
import Home from "./pages/Home";



export default function App() {
  
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-4 py-24 dark:bg-gray-900">
      {/* Mudança de tema */}
      <div className="absolute inset-0 size-full">
        <div className="relative h-full w-full select-none">
          <img
            className="absolute right-0 min-w-dvh dark:hidden"
            alt="Pattern Light"
            src={patternLight}
          />
          <img
            className="absolute right-0 hidden min-w-dvh dark:block"
            alt="Pattern Dark"
            src={patternDark}
          />
        </div>
      </div>
      <div className="absolute top-4 right-4">
        <DarkThemeToggle />
      </div>
      {/* Home */}

      <Home />
      
    </main>
  );
}
