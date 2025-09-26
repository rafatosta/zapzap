import AboutSection from "./components/AboutSection";
import DonateSection from "./components/DonateSections";
import DownloadSection from "./components/DownloadSection";
import FeatureSection from "./components/FeatureSection";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Hero from "./components/Hero";

export default function App() {

  return (
    <div className="min-h-screen \
      bg-white dark:bg-gray-900 \
      text-gray-900 dark:text-gray-100 \
      ">
      <Header />
      <Hero />
      <FeatureSection />
      <DownloadSection />
      <DonateSection />
      <AboutSection />
      <Footer />
    </div>
  );
}