import axios from "axios";
import Vue from "vue";

function getAuthHeaders() {
  const jwt = Vue.$cookies.get("token");
  if (jwt) {
    return {
      Authorization: `Bearer ${jwt}`,
    };
  }
}

function getClient() {
  return axios.create({
    baseURL: "http://fs-service.localhost/api/",
    headers: getAuthHeaders(),
    timeout: 3000,
  });
}
const api = {
  async createUser(email, username, password) {
    const params = { email, username, password };
    return getClient().post("users", params);
  },
  async getToken(email, password) {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);

    return getClient().post("auth/token", params);
  },
  async getCurrentUserInfo() {
    return getClient().get("users/my");
  },
  async getUserList(params) {
    return getClient().get("users/", { params });
  },
  async deleteUser(params) {
    return getClient().delete("users", { params });
  },
  async updateUser(user_id, role, storage_allowance, is_active) {
    const data = {
      user_id,
      role,
      storage_allowance,
      is_active,
    };
    return getClient().put("users", data);
  },
  async getFileInfo(params) {
    return getClient().get("files", { params });
  },
  async getFileList(params) {
    return getClient().get("files/list/", { params });
  },
  async searchFile(params) {
    return getClient().get("files/search/", { params });
  },
  async getFileCount(params) {
    return getClient().get("files/count", { params });
  },
  async getStorageUsed(params) {
    return getClient().get("files/usage", { params });
  },
  async deleteFile(file) {
    const params = {
      filename: file.filename,
    };
    return getClient().delete("files", { params });
  },
  async uploadFile(file, progressCallback) {
    const formData = new FormData();
    formData.append("file", file);
    return getClient().post("files/upload", formData, {
      onUploadProgress: progressCallback,
      timeout: 0
    });
  },
  async downloadFile(filename, progressCallback) {
    const params = { filename };
    return getClient().get("files/download", {
      onDownloadProgress: progressCallback,
      params,
      responseType: "blob",
    });
  },
};

export default api;
