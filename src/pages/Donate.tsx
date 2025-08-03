import {
    FaPix,
    FaGithub,
    FaPaypal,
} from "react-icons/fa6";

import { SiKofi } from "react-icons/si";

import { Element } from 'react-scroll';

export default function Donate() {
    return (
        <Element name="donate">
            <div className="relative flex w-full max-w-5xl h-screen flex-col items-center justify-center gap-12 pt-12 lg:pt-0">
                <h1 className="relative text-center text-3xl leading-[125%] text-shadow-lg font-bold">
                    Support the Project
                </h1>

                <p className="mb-8 text-lg text-gray-600 dark:text-gray-200">
                    If you like this project and want to support its development, consider
                    making a donation. Any amount helps to keep the project active, free,
                    and constantly improving.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {/* Pix */}
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-md">
                        <div className="flex items-center gap-3 mb-4">
                            <FaPix className="text-green-500 text-xl" />
                            <h2 className="text-xl font-semibold text-gray-100">Pix (Brazil)</h2>
                        </div>
                        <p className="text-sm text-gray-300 mb-2">Make a Pix</p>
                        <a
                            href="https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block bg-primary-500 hover:bg-primary-600 text-white font-semibold px-4 py-2 rounded-md transition"
                        >
                            Donate with Pix
                        </a>
                    </div>

                    {/* GitHub Sponsors */}
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-md">
                        <div className="flex items-center gap-3 mb-4">
                            <FaGithub className="text-gray-100 text-xl" />
                            <h2 className="text-xl font-semibold text-gray-100">GitHub Sponsors</h2>
                        </div>
                        <p className="text-sm text-gray-300 mb-3">
                            Support via GitHub and get exclusive updates.
                        </p>
                        <a
                            href="https://github.com/sponsors/rafatosta"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block bg-primary-500 hover:bg-primary-600 text-white font-semibold px-4 py-2 rounded-md transition"
                        >
                            Sponsor on GitHub
                        </a>
                    </div>

                    {/* Ko-fi */}
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-md">
                        <div className="flex items-center gap-3 mb-4">
                            <SiKofi className="text-[#FFDD00] text-xl" />
                            <h2 className="text-xl font-semibold text-gray-100">Ko-fi</h2>
                        </div>
                        <p className="text-sm text-gray-300 mb-3">
                            Buy me a coffee and help keep me coding!
                        </p>
                        <a
                            href="https://ko-fi.com/rafaeltosta"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block bg-primary-500 hover:bg-primary-600 text-white font-semibold px-4 py-2 rounded-md transition"
                        >
                            Donate on Ko-fi
                        </a>
                    </div>

                    {/* PayPal */}
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-md">
                        <div className="flex items-center gap-3 mb-4">
                            <FaPaypal className="text-[#00457C] text-xl" />
                            <h2 className="text-xl font-semibold text-gray-100">PayPal</h2>
                        </div>
                        <p className="text-sm text-gray-300 mb-3">
                            Make a secure donation using your PayPal account.
                        </p>
                        <a
                            href="https://www.paypal.com/donate/?business=E7R4BVR45GRC2&no_recurring=0&item_name=ZapZap+-+Whatsapp+Desktop+for+linux&currency_code=USD"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block bg-primary-500 hover:bg-primary-600 text-white font-semibold px-4 py-2 rounded-md transition"
                        >
                            Donate with PayPal
                        </a>
                    </div>
                </div>

                <p className="mt-12 text-sm text-gray-500 text-center">
                    Thank you for supporting this project 💚
                </p>
            </div>
        </Element>
    );
}
