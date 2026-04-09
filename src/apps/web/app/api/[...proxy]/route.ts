import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

async function forward(request: NextRequest, method: string, path: string[]): Promise<NextResponse> {
	const url = new URL(`${API_URL}/api/${path.join("/")}${request.nextUrl.search}`);
	const body = ["GET", "HEAD"].includes(method) ? undefined : await request.text();
	const authHeader = request.headers.get("Authorization");
	const res = await fetch(url, {
		method,
		headers: {
			"Content-Type": request.headers.get("Content-Type") ?? "application/json",
			...(authHeader ? { Authorization: authHeader } : {}),
		},
		body,
		cache: "no-store",
	});

	const text = await res.text();
	return new NextResponse(text, {
		status: res.status,
		headers: {
			"Content-Type": res.headers.get("Content-Type") ?? "application/json",
			"Cache-Control": "no-store",
		},
	});
}

export async function GET(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
	const params = await context.params;
	return forward(request, "GET", params.proxy);
}

export async function POST(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
	const params = await context.params;
	return forward(request, "POST", params.proxy);
}

export async function PUT(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
	const params = await context.params;
	return forward(request, "PUT", params.proxy);
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
	const params = await context.params;
	return forward(request, "PATCH", params.proxy);
}

export async function DELETE(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
	const params = await context.params;
	return forward(request, "DELETE", params.proxy);
}
