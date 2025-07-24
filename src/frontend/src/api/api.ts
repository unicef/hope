export const api = {
  baseURL: '/api/rest/',
  headers: {
    Accept: 'application/json',
  },
  cache: new Map(),

  buildParams(data: Record<string, any> = {}) {
    const params = new URLSearchParams();

    Object.entries(data).forEach(([key, value]) => {
      if (typeof key !== 'string' || !/^[a-zA-Z0-9_-]+$/.test(key)) {
        throw new Error('Invalid parameter key');
      }

      if (Array.isArray(value)) {
        value.forEach((v) => {
          if (typeof v !== 'string' && typeof v !== 'number') {
            throw new Error('Invalid parameter value');
          }
          params.append(key, encodeURIComponent(v.toString()));
        });
      } else {
        if (typeof value !== 'string' && typeof value !== 'number') {
          throw new Error('Invalid parameter value');
        }
        params.append(key, encodeURIComponent(value.toString()));
      }
    });

    return params.toString();
  },

  async get(url: string, params: Record<string, any> = {}, filename?: string) {
    const query = this.buildParams(params);
    const cacheKey = url + (query ? `?${query}` : '');

    const cached = this.cache.get(cacheKey);
    const headers = { ...this.headers };

    if (cached && cached.etag) {
      headers['If-None-Match'] = cached.etag;
    }

    const response = await fetch(`${this.baseURL}${cacheKey}`, {
      headers,
    });

    if (response.status === 304) {
      return cached.data;
    }

    if (!response.ok) {
      throw new Error(`Error fetching data from ${url}`);
    }

    // Handle download if URL includes "download"
    if (url.includes('download')) {
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename || url.split('/').pop() || 'download';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
      return;
    }

    const etag = response.headers.get('ETag');
    const data = await response.json();

    if (etag && data !== undefined && data !== null) {
      this.cache.set(cacheKey, { etag, data });
    }
    return data;
  },

  async post(url: string, data: Record<string, any> | FormData) {
    const isFormData = data instanceof FormData;
    const fetchOptions: RequestInit = {
      method: 'POST',
      headers: {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      },
      body: isFormData ? data : JSON.stringify(data),
    };

    const response = await fetch(`${this.baseURL}${url}`, fetchOptions);

    if (!response.ok) {
      const error = Error(`Error posting data to ${url}`);
      try {
        // @ts-ignore
        error.data = await response.json();
      } catch (e) {
        // @ts-ignore
        error.data = null;
      }
      throw error;
    }

    const text = await response.text();
    if (!text) {
      return { data: null };
    }

    return { data: JSON.parse(text) };
  },

  async put(url: string, data: Record<string, any> = {}) {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'PUT',
      headers: {
        ...this.headers,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = Error(`Error puting data to ${url}`);
      try {
        // @ts-ignore
        error.data = await response.json();
      } catch (e) {
        // @ts-ignore
        error.data = null;
      }
      throw error;
    }

    const text = await response.text();
    if (!text) {
      return { data: null };
    }
    return { data: JSON.parse(text) };
  },

  async delete(url: string) {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'DELETE',
      headers: {
        ...this.headers,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error deleting data from ${url}`);
    }
    return;
  },
};

export type Params = Record<string, any>;

export const handleApiResponse = async (apiCall) => {
  try {
    const response = await apiCall;
    return response;
  } catch (error: any) {
    console.error('API call failed:', error.message || error);
    throw new Error(`API call failed: ${error.message || 'Unknown error'}`);
  }
};

export const handleMutationError = (error: any, action: string): never => {
  const errorMessage = error?.message || 'An unknown error occurred';
  throw new Error(`Failed to ${action}: ${errorMessage}`);
};

export const postRequest = async (
  url: string,
  body: any,
  errorMessage: string,
) => {
  try {
    const response = await api.post(url, body);
    return response.data;
  } catch (error) {
    handleMutationError(error, errorMessage);
    throw error;
  }
};
