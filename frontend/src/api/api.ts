export const api = {
  baseURL: '/api/rest/',
  headers: {
    Accept: 'application/json',
  },
  cache: new Map(),

  async get(url: string, params: Record<string, any> = {}) {
    const query = new URLSearchParams(params).toString();
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

    const etag = response.headers.get('ETag');
    const data = await response.json();

    if (etag) {
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
};
