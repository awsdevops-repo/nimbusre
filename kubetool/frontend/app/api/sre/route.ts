import { NextRequest, NextResponse } from 'next/server';

// API backend URL (configure via environment variables)
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, workflow_type = 'basic', max_tools = 5 } = body;

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Invalid query: query must be a non-empty string' },
        { status: 400 }
      );
    }

    // Call the Python backend API
    const response = await fetch(`${BACKEND_URL}/api/sre`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        workflow_type,
        max_tools,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Internal server error',
        status: 'error',
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // Health check endpoint
    const response = await fetch(`${BACKEND_URL}/health`);
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Health check failed:', error);
    return NextResponse.json(
      { status: 'unhealthy', error: 'Cannot connect to backend' },
      { status: 503 }
    );
  }
}
