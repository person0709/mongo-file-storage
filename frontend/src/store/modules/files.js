import api from "@/api";
import router from "@/router";

const state = {
  fileMetas: [],
  tableLoading: false,
  totalFileCount: 0,
  uploadProgress: 0,
  downloadProgress: 0,
  storageUsed: 0,
  sortOptions: {},
  itemsPerPage: 0,
};

const getters = {
  isUploadDone: (state) => {
    return state.uploadProgress > 0;
  },

  isDownloadDone: (state) => {
    return state.downloadProgress > 0;
  },

  storagePercentage: (state, getters, rootState) => {
    return (
      (state.storageUsed / rootState.users.currentUser.storage_allowance) * 100
    );
  },

  storageColor: (state, getters) => {
    if (getters.storagePercentage < 50) {
      return "green";
    } else if (
      50 <= getters.storagePercentage &&
      getters.storagePercentage <= 80
    ) {
      return "orange";
    } else {
      return "red";
    }
  },
};

const actions = {
  // fetch a batch of sorted file lists from server for pagination.
  async fetchFileMetas({ commit, state }) {
    commit("SET_TABLE_LOADING", true);
    try {
      const fileMetasRes = await api.getFileList(state.sortOptions);
      const countRes = await api.getFileCount({});
      commit("SET_FILE_METAS", {
        fileMetas: fileMetasRes.data.files,
        totalFileCount: countRes.data.count,
      });
    } catch (err) {
      if (err.response.status === 403) {
        await router.push("/login");
      }
      commit(
        "SET_ERROR",
        { show: true, message: err.response.data.detail },
        { root: true }
      );
    } finally {
      commit("SET_TABLE_LOADING", false);
    }
  },

  async uploadFile({ commit, state, rootState }, uploadingFile) {
    // check file storage limit before uploading
    if (
      state.storageUsed + uploadingFile.size >
      rootState.users.currentUser.storage_allowance
    ) {
      commit(
        "SET_ERROR",
        { show: true, message: "Storage limit exceeded" },
        { root: true }
      );
      return;
    }
    // check for duplicate filename
    try {
      const fileCheck = await api.getFileInfo({
        filename: uploadingFile.name,
      });
      if (fileCheck.status === 200) {
        commit(
          "SET_ERROR",
          { show: true, message: "File with the same name exists" },
          { root: true }
        );
        return;
      }
    } catch (err) {
      // the server returns 404 when the file is not found
      if (err.response.status !== 404) {
        commit(
          "SET_ERROR",
          { show: true, message: err.response.data.detail },
          { root: true }
        );
      }
    }
    // start uploading
    try {
      const uploadedFileMeta = await api.uploadFile(uploadingFile, (e) =>
        commit("UPDATE_UPLOAD_PROGRESS", Math.round((e.loaded * 100) / e.total))
      );
      commit(
        "SET_NOTIF",
        { show: true, message: "File uploaded successfully" },
        { root: true }
      );
      commit("ADD_FILE_META_TO_TABLE", uploadedFileMeta.data);
    } catch (err) {
      if (err.response.status === 403) {
        await router.push("/login");
      } else {
        commit(
          "SET_ERROR",
          { show: true, message: err.response.data.detail },
          { root: true }
        );
      }
    } finally {
      commit("UPDATE_UPLOAD_PROGRESS", 0);
    }
  },

  async fetchStorageUsed({ commit }) {
    const response = await api.getStorageUsed();
    commit("SET_STORAGE_USED", response.data.storage_used);
  },

  // fetch file list
  async fetchFileSearch({ commit, dispatch }, search) {
    if (search === "") {
      await dispatch("fetchFileMetas");
      return;
    }
    commit("SET_TABLE_LOADING", true);
    try {
      const response = await api.searchFile({
        pattern: search,
        limit: 10,
      });
      commit("SET_FILE_METAS", {
        fileMetas: response.data.files,
        totalFileCount: response.data.files.length,
      });
    } catch (err) {
      commit(
        "SET_ERROR",
        { show: true, message: err.response.data.detail },
        { root: true }
      );
    } finally {
      commit("SET_TABLE_LOADING", false);
    }
  },

  // delete a file and remove from the current file list
  async deleteFile({ commit, state, dispatch }, file) {
    commit("SET_TABLE_LOADING", true);
    try {
      const response = await api.deleteFile(file);
      if (response.status === 200) {
        commit(
          "SET_NOTIF",
          { show: true, message: "File deleted successfully" },
          { root: true }
        );
        // refetch the list if there are more items in the table than the current items per page
        // setting so that the table gets re-filled
        if (state.totalFileCount > state.itemsPerPage) {
          await dispatch("fetchFileMetas");
        } else {
          commit("DELETE_FILE_META_FROM_TABLE", file);
        }
      }
    } catch (err) {
      if (err.response.status === 403) {
        await router.push("/login");
      }
    } finally {
      commit("SET_TABLE_LOADING", false);
    }
  },

  // download a file as a blob and trigger save window
  async downloadFile({ commit }, file) {
    commit("SET_TABLE_LOADING", true);
    try {
      const response = await api.downloadFile(file.filename, (e) =>
        commit(
          "UPDATE_DOWNLOAD_PROGRESS",
          Math.round((e.loaded * 100) / e.total)
        )
      );
      const blob = new Blob([response.data], { type: response.data.type });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = file.filename;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (err) {
      commit(
        "SET_ERROR",
        { show: true, message: err.response.data.detail },
        { root: true }
      );
    } finally {
      commit("SET_TABLE_LOADING", false);
      commit("UPDATE_DOWNLOAD_PROGRESS", 0);
    }
  },
};

const mutations = {
  SET_FILE_METAS(state, payload) {
    state.fileMetas = payload.fileMetas;
    state.totalFileCount = payload.totalFileCount;
  },

  SET_TABLE_LOADING(state, loadingState) {
    state.tableLoading = loadingState;
  },

  SET_STORAGE_USED(state, storage) {
    state.storageUsed = storage;
  },

  UPDATE_UPLOAD_PROGRESS(state, progress) {
    state.uploadProgress = progress;
  },

  UPDATE_DOWNLOAD_PROGRESS(state, progress) {
    state.downloadProgress = progress;
  },

  // if a file is uploaded, add the uploaded file info to the table
  ADD_FILE_META_TO_TABLE(state, fileMeta) {
    state.fileMetas.unshift(fileMeta);
    state.totalFileCount++;
    if (state.totalFileCount > state.itemsPerPage) state.fileMetas.pop();
  },

  // if a file is deleted, remove the file from the table
  DELETE_FILE_META_FROM_TABLE(state, fileMeta) {
    state.fileMetas.splice(state.fileMetas.indexOf(fileMeta), 1);
    state.totalFileCount--;
  },

  SET_SORT_OPTIONS(state, options) {
    // transform vuetify data table options to parameter that the server will take
    let { sortBy, sortDesc, page, itemsPerPage } = options;
    const transformedOptions = {};

    if (sortBy.length === 1) {
      transformedOptions.sort_by = sortBy[0];
      transformedOptions.desc = sortDesc[0];
    }

    const offset = (page - 1) * itemsPerPage;
    let limit = itemsPerPage;
    if (itemsPerPage === -1) limit = 100;
    state.itemsPerPage = itemsPerPage;
    state.sortOptions = { ...transformedOptions, offset, limit };
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
