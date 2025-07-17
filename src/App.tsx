import { DarkThemeToggle } from "flowbite-react";

import patternLight from "/pattern-light.svg"
import patternDark from "/pattern-dark.svg"
import flowbiteReact from  "/flowbite-react.svg"
import flowbite from "/flowbite.svg"
import figama from "/figma.svg"

export default function App() {
  const CARDS = [
    {
      title: "Flowbite React Docs",
      description:
        "Learn more on how to get started and use the Flowbite React components",
      url: "https://flowbite-react.com/",
      icon: (
        <svg
          className="h-9 w-9 text-gray-500"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            d="M12 6.03v13m0-13c-2.819-.831-4.715-1.076-8.029-1.023A.99.99 0 0 0 3 6v11c0 .563.466 1.014 1.03 1.007 3.122-.043 5.018.212 7.97 1.023m0-13c2.819-.831 4.715-1.076 8.029-1.023A.99.99 0 0 1 21 6v11c0 .563-.466 1.014-1.03 1.007-3.122-.043-5.018.212-7.97 1.023"
          />
        </svg>
      ),
    },
    {
      title: "Flowbite Blocks",
      description:
        "Get started with over 450 blocks to build websites even faster",
      url: "https://flowbite.com/blocks/",
      icon: (
        <svg
          className="h-9 w-9 text-gray-500"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            d="M9.143 4H4.857A.857.857 0 0 0 4 4.857v4.286c0 .473.384.857.857.857h4.286A.857.857 0 0 0 10 9.143V4.857A.857.857 0 0 0 9.143 4Zm10 0h-4.286a.857.857 0 0 0-.857.857v4.286c0 .473.384.857.857.857h4.286A.857.857 0 0 0 20 9.143V4.857A.857.857 0 0 0 19.143 4Zm-10 10H4.857a.857.857 0 0 0-.857.857v4.286c0 .473.384.857.857.857h4.286a.857.857 0 0 0 .857-.857v-4.286A.857.857 0 0 0 9.143 14Zm10 0h-4.286a.857.857 0 0 0-.857.857v4.286c0 .473.384.857.857.857h4.286a.857.857 0 0 0 .857-.857v-4.286a.857.857 0 0 0-.857-.857Z"
          />
        </svg>
      ),
    },
    {
      title: "Flowbite Icons",
      description:
        "Get started with over 650+ SVG free and open-source icons for your apps",
      url: "https://flowbite.com/icons/",
      icon: (
        <svg
          className="h-9 w-9 text-gray-500"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            d="M11 6.5h2M11 18h2m-7-5v-2m12 2v-2M5 8h2a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1Zm0 12h2a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1Zm12 0h2a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1h-2a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1Zm0-12h2a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1h-2a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1Z"
          />
        </svg>
      ),
    },
    {
      title: "Flowbite Illustrations",
      description:
        "Start using over 50+ SVG illustrations in 3D style to add character to your apps",
      url: "https://flowbite.com/illustrations/",
      icon: (
        <svg
          className="h-9 w-9 text-gray-500"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            d="m3 16 5-7 6 6.5m6.5 2.5L16 13l-4.286 6M14 10h.01M4 19h16a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1Z"
          />
        </svg>
      ),
    },
    {
      title: "Flowbite Pro",
      description:
        "Upgrade your development stack with more components and templates from Flowbite",
      url: "https://flowbite.com/pro/",
      icon: <img alt="Flowbite Pro logo" src={flowbite} />,
    },
    {
      title: "Flowbite Figma",
      description:
        "Use our Figma Design System to design and collaborate better within your team",
      url: "https://flowbite.com/figma/",
      icon: <img alt="Figma logo" src={figama} />,
    },
  ];

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-4 py-24 dark:bg-gray-900">
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

      <div className="relative flex w-full max-w-5xl flex-col items-center justify-center gap-12">
        <div className="relative flex flex-col items-center gap-6">
          <h1 className="relative text-center text-4xl leading-[125%] font-bold text-gray-900 dark:text-gray-200">
            Build fast with us
          </h1>
          <span className="inline-flex flex-wrap items-center justify-center gap-2.5 text-center">
            <span className="inline text-xl text-gray-600 dark:text-gray-400">
              Your app is ready, start building with
            </span>
            <span className="relative inline-flex items-center gap-2">
              <img
                className="size-6"
                alt="Flowbite React logo"
                src={flowbiteReact}
              />
              <span className="relative w-fit text-xl font-semibold whitespace-nowrap text-[#111928] dark:text-white">
                Flowbite React
              </span>
            </span>
            <h2 className="inline text-xl text-gray-600 dark:text-gray-400">
              now.
            </h2>
          </span>
        </div>

        <div className="relative flex w-full flex-col items-start gap-6 self-stretch">
          <div className="grid w-full grid-cols-1 gap-6 md:grid-cols-2">
            {CARDS.map((card) => (
              <a
                key={card.title}
                href={card.url}
                target="_blank"
                className="outline-primary-600 dark:outline-primary-500 group hover:border-primary-600 dark:hover:border-primary-500 cursor-pointer overflow-hidden rounded-xl border border-gray-200 bg-gray-50 outline-offset-2 focus:outline-2 dark:border-gray-700 dark:bg-gray-800"
              >
                <div className="flex items-center gap-6 p-4">
                  <div className="flex flex-1 items-center gap-2">
                    <div className="size-9">{card.icon}</div>

                    <div className="flex flex-1 flex-col items-start justify-center gap-1.5 border-l border-gray-200 pl-3.5 dark:border-gray-700">
                      <div className="w-full font-sans text-lg leading-4 font-semibold text-gray-900 dark:text-gray-200">
                        {card.title}
                      </div>

                      <div className="w-full font-sans text-sm leading-5 font-normal text-gray-500 dark:text-gray-400">
                        {card.description}
                      </div>
                    </div>
                  </div>

                  <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    className="group-hover:text-primary-600 dark:group-hover:text-primary-500 h-6 w-6 text-gray-500 transition-transform group-hover:translate-x-1"
                  >
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M14.2929 7.29289C14.6834 6.90237 15.3166 6.90237 15.7071 7.29289L19.7071 11.2929C19.8946 11.4804 20 11.7348 20 12C20 12.2652 19.8946 12.5196 19.7071 12.7071L15.7071 16.7071C15.3166 17.0976 14.6834 17.0976 14.2929 16.7071C13.9024 16.3166 13.9024 15.6834 14.2929 15.2929L16.5858 13H5C4.44772 13 4 12.5523 4 12C4 11.4477 4.44772 11 5 11H16.5858L14.2929 8.70711C13.9024 8.31658 13.9024 7.68342 14.2929 7.29289Z"
                      fill="currentColor"
                    />
                  </svg>
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
