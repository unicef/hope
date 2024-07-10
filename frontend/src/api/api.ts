export const api = {
  baseURL: '/api/rest/',
  headers: {
    Accept: 'application/json',
  },
  cache: new Map(),

  async get(url: string, params: Record<string, any> = {}) {
    const query = new URLSearchParams(params).toString();
    const cacheKey = `${url}?${query}`;

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

  async post(url: string, data: Record<string, any> = {}) {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'POST',
      headers: {
        ...this.headers,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Error posting data to ${url}`);
    }

    const text = await response.text();
    if (!text) {
      return { data: null };
    }

    return { data: JSON.parse(text) };
  },
};
