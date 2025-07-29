
const whatsappUserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36';
const whatsappURL = "https://web.whatsapp.com"

function App(): React.JSX.Element {

  return (
    <div className="flex h-screen w-screen overflow-hidden">

      <main className="flex-1 relative">

        <webview
          src={whatsappURL}
          style={{
            display: "flex",
            width: '100%',
            height: '100%',
            border: 'none'
          }}
          partition={"persist:1"}
          useragent={whatsappUserAgent}
        />

      </main>
    </div>
  )
}

export default App
