  import { NextResponse } from 'next/server';

  export async function POST(request) {
    const { text } = await request.json();
    
      const response = await fetch('http://127.0.0.1:5000/api/process', {
      //const response = await fetch('/api/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  }
