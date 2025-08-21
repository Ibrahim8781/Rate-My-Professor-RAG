import Chatbot from './chatbot/page';

'use client'


export default function Home() {
  

  return (
    <div>
      
      
      
      <div className="bg-[#00695c] text-white min-h-screen">
      <Head>
        <title>AI Chatbot Landing Page</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Header/>
      <main>
        <Chatbot />
      </main>
      <Footer/>

      {/* <Head>
        <title>AI Chatbot Landing Page</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Header/>           
      <main>
        <Hero />
        <Features />
        <Pricing />
      </main>

      <Footer /> */}
    </div>
    </div>
    
  );
}

