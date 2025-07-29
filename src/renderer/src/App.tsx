import { useState } from 'react'

const accounts = ['conta1']

const whatsappUserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36';


function App(): React.JSX.Element {
  const [selected, setSelected] = useState('conta1')

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <aside className="w-40 bg-gray-200 p-2">
        {accounts.map((acc) => (
          <button
            key={acc}
            onClick={() => setSelected(acc)}
            className={`block w-full mb-2 p-2 rounded ${selected === acc ? 'bg-blue-500 text-white' : 'bg-white'
              }`}
          >
            {acc}
          </button>
        ))}
      </aside>

      <main className="flex-1 relative">
        {accounts.map((acc) => (
          <webview
            key={acc}
            src="https://web.whatsapp.com"
            style={{
              display: selected === acc ? 'flex' : 'none',
              width: '100%',
              height: '100%',
              border: 'none'
            }}
            partition={`persist:${acc}`}
            useragent={whatsappUserAgent}
          />
        ))}
      </main>
    </div>
  )
}

export default App
