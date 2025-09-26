import Footer from "./components/Footer";
import Header from "./components/Header";
import Hero from "./components/Hero";
import AboutSection from "./sections/AboutSection";
import DonateSection from "./sections/DonateSection";
import DownloadSection from "./sections/DownloadSection";
import FeatureSection from "./sections/FeatureSection";

export default function App() {

  return (
    <div className="min-h-screen \
      bg-white dark:bg-gray-900 \
      text-gray-900 dark:text-gray-100 \
      ">
      <Header />
      <Hero />
      <FeatureSection/>
      <DownloadSection />
      <DonateSection />
      <AboutSection />
      <Footer />
    </div>
  );
}