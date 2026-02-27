import { supabase } from './supabase';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function getAuthHeaders() {
    const { data: { session } } = await supabase.auth.getSession();
    const token = session?.access_token;
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
}

export class ApiError extends Error {
    status: number;
    constructor(status: number, message: string) {
        super(message);
        this.status = status;
        this.name = 'ApiError';
    }
}

export const api = {
    async get(endpoint: string) {
        const headers = await getAuthHeaders();
        const response = await fetch(`${BASE_URL}${endpoint}`, { headers });
        if (!response.ok) {
            const text = await response.text();
            throw new ApiError(response.status, text);
        }
        return response.json();
    },

    async post(endpoint: string, body: any) {
        const headers = await getAuthHeaders();
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            const text = await response.text();
            throw new ApiError(response.status, text);
        }
        return response.json();
    },

    async put(endpoint: string, body: any) {
        const headers = await getAuthHeaders();
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'PUT',
            headers,
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            const text = await response.text();
            throw new ApiError(response.status, text);
        }
        return response.json();
    },

    async postFormData(endpoint: string, formData: FormData) {
        const headers = await getAuthHeaders();
        // Remove Content-Type so browser sets it with boundary
        const { 'Content-Type': _, ...authHeaders } = headers as any;
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: authHeaders,
            body: formData,
        });
        if (!response.ok) {
            const text = await response.text();
            throw new ApiError(response.status, text);
        }
        return response.json();
    },
};
