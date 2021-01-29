import axios from 'axios';

class ApiClient {
  constructor({ apiUrl, headers = {} }) {
    this.headers = headers;
    this.settings = {
      baseURL: apiUrl,
    };
  }

  setHeaders = (headers) => {
    this.headers = headers;
  };

  async get(endpoint, params = {}, opts = {}) {
    return await this.send({
      method: 'get',
      endpoint: endpoint,
      params: params,
      ...opts,
    });
  }

  async post(endpoint, payload = {}, opts = {}) {
    return await this.send({
      method: 'post',
      endpoint: endpoint,
      payload: payload,
      ...opts,
    });
  }

  async put(endpoint, payload = {}, opts = {}) {
    return await this.send({
      method: 'put',
      endpoint: endpoint,
      payload: payload,
      ...opts,
    });
  }

  async patch(endpoint, payload = {}, opts = {}) {
    return await this.send({
      method: 'patch',
      endpoint: endpoint,
      payload: payload,
      ...opts,
    });
  }
  async delete(endpoint, payload = {}, opts = {}) {
    return await this.send({
      method: 'delete',
      endpoint: endpoint,
      payload: payload,
      ...opts,
    });
  }

  async send(request) {
    const {
      method = 'get',
      endpoint,
      payload = {},
      headers = {},
      params,
    } = request;

    try {
      const response = await axios({
        method,
        headers: { ...this.headers, ...headers },
        params,
        url: endpoint,
        data: payload,
        ...this.settings,
      });
      return response.data;
    } catch (error) {
      // TODO: We should throw the error directly from here.
      // throw new error();
      // However, by doing this may change the behavior of the error handling of APIs using this ApiClient.
      return { error };
    }
  }
}

export default ApiClient;
