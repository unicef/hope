export const api = {
  baseURL: '/api/rest/',
  headers: {
    Accept: 'application/json',
  },
  cache: new Map(),

  buildParams(data: Record<string, any> = {}) {
    const params = new URLSearchParams();

    Object.entries(data).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach((v) => params.append(key, v.toString()));
      } else {
        params.append(key, value.toString());
      }
    });

    return params.toString();
  },

  async get(url: string, params: Record<string, any> = {}) {
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
