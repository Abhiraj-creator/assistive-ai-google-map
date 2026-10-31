import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const adkRequest = {
      appName: body.appName,
      userId: body.userId,
      sessionId: body.sessionId,
      newMessage: body.newMessage,
    };

    // First, ensure session exists
    try {
      await fetch(`http://localhost:8000/apps/${body.appName}/users/${body.userId}/sessions/${body.sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: {} }),
      });
    } catch (sessionError) {
      // Session might already exist, continue
      console.log('Session creation note:', sessionError);
    }

    // Forward the request to the ADK server with correct format
    const response = await fetch('http://localhost:8000/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(adkRequest),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`ADK Server responded with status: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `ADK server is unavailable: ${errorMessage}` },
      { 
        // This is an upstream-service failure, not an error in the user's query.
        status: 503,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
