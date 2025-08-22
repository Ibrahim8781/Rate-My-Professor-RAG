'use client'

//import chatbot from '@/app/chatbot/page.js'
import Chatbot from "./chatbot/page";
import Head from "next/head";

export default function Home() {


  return (
    <div>
      <div className="bg-[#00695c] text-white min-h-screen">
        <Head>
          <title>AI Chatbot Landing Page</title> 
          <link rel="icon" href="/favicon.ico" />
        </Head>
        <main>
          <Chatbot />
        </main>
      </div>
    </div>

  );
}

