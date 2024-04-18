export const api = {
  baseURL: '/api/rest/',
  headers: {
    Accept: 'application/json',
  },
  cache: new Map(),

  async get(url: string, params: Record<string, any> = {}) {
    const query = new URLSearchParams(params).toString();

    const response = await fetch(`${this.baseURL}${url}?${query}`, {
      headers: this.headers,
    });

    if (response.status === 304) {
      const cached = this.cache.get(url);
      if (cached) {
        return cached.data;
      }
    }

    if (!response.ok) {
      throw new Error(`Error fetching data from ${url}`);
    }

    const etag = response.headers.get('ETag');
    const data = await response.json();

    if (etag) {
      this.cache.set(url, { etag, data });
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

    // Check if the response is empty
    const text = await response.text();
    if (!text) {
      // If the response is empty, return an object with a data property set to null
      return { data: null };
    }

    // If the response is not empty, parse it as JSON and return it
    return { data: JSON.parse(text) };
  },
};
