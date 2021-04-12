import api from "@/api";
import router from "@/router";

const state = {
  currentUser: {},
  usersInTable: [],
  usersCount: 0,
  sortOptions: {},
  itemsPerPage: 0,
  tableLoading: false,
  search: "",
  searchField: "Username",
  dialog: false,
  editingUser: {},
  newAllowance: 0,
  newRole: "",
  newStatus: false,
};

const getters = {
  canUpload: (state) => {
    if (state.currentUser.role === "ADMIN") {
      return true;
    } else if (state.currentUser.role === "UPLOADER") {
      return true;
    } else if (state.currentUser.role === "VIEWER") {
      return false;
    } else return false;
  },

  canDownload: (state) => {
    if (state.currentUser.role === "ADMIN") {
      return true;
    } else if (state.currentUser.role === "UPLOADER") {
      return true;
    } else if (state.currentUser.role === "VIEWER") {
      return false;
    } else return false;
  },

  canDelete: (state) => {
    if (state.currentUser.role === "ADMIN") {
      return true;
    } else if (state.currentUser.role === "UPLOADER") {
      return true;
    } else if (state.currentUser.role === "VIEWER") {
      return false;
    } else return false;
  },
};

const actions = {
  openUserEditDialog({ commit }, user) {
    commit("SET_USER_EDIT_DIALOG", true);
    commit("SET_EDITING_USER", user);
  },

  async fetchCurrentUser({ commit }) {
    try {
      const response = await api.getCurrentUserInfo();
      commit("SET_CURRENT_USER", response.data);
    } catch (err) {
      if (err.response.status === 401) {
        await router.push("/login");
      }
    }
  },

  // fetch a batch of sorted file lists from server for pagination.
  async fetchUserList({ commit, state }) {
    commit("SET_TABLE_LOADING", true);
    try {
      const userList = await api.getUserList(state.sortOptions);
      commit("SET_USERS_IN_TABLE", {
        users: userList.data.users,
        count: userList.data.count,
      });

      // get storage status from file service
      await Promise.all(
        state.usersInTable.map(async (user) => {
          const usage = await api.getStorageUsed({ user_id: user.user_id });
          user.storage_used = usage.data.storage_used;
        })
      );
    } catch (err) {
      if (err.response.status === 403) {
        await router.push("/login");
      }
      commit("SET_USER_ERROR", err.response.data.detail);
    } finally {
      commit("SET_TABLE_LOADING", false);
    }
  },

  async onEditUserSave({ commit, state }) {
    commit("SET_TABLE_LOADING", true);
    try {
      const response = await api.updateUser(
        state.editingUser.user_id,
        state.newRole,
        state.newAllowance,
        state.newStatus
      );
      commit("UPDATE_EDITED_USER", response.data);
      commit(
        "SET_NOTIF",
        { show: true, message: "User updated successfully" },
        { root: true }
      );
    } catch (err) {
      commit(
        "SET_ERROR",
        { show: true, message: err.response.data.detail },
        { root: true }
      );
    } finally {
      commit("SET_TABLE_LOADING", false);
      commit("SET_USER_EDIT_DIALOG", false);
    }
  },

  async deleteUser({ commit }, user) {
    commit("SET_TABLE_LOADING", true);
    try {
      const response = await api.deleteUser({ user_id: user.user_id });
      commit("DELETE_USER", response.data.user_id);
      commit(
        "SET_NOTIF",
        { show: true, message: "User deleted successfully" },
        { root: true }
      );
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
};

const mutations = {
  SET_CURRENT_USER: (state, user) => (state.currentUser = user),
  SET_USERS_IN_TABLE: (state, payload) => {
    state.usersInTable = payload.users;
    state.usersCount = payload.count;
  },
  SET_TABLE_LOADING: (state, loadingState) =>
    (state.tableLoading = loadingState),
  SET_USER_EDIT_DIALOG: (state, dialog) => (state.dialog = dialog),
  SET_EDITING_USER: (state, user) => {
    state.editingUser = user;
    state.newRole = user.role;
    state.newAllowance = user.storage_allowance;
    state.newStatus = user.is_active;
  },
  UPDATE_EDITED_USER: (state, payload) => {
    state.editingUser.role = payload.role;
    state.editingUser.storage_allowance = payload.storage_allowance;
    state.editingUser.is_active = payload.is_active;
  },
  DELETE_USER: (state, user_id) => {
    state.usersInTable.splice(
      state.usersInTable.findIndex((x) => x.user_id === user_id),
      1
    );
  },
  // transform vuetify data table options to parameter that the server will take
  SET_SORT_OPTIONS(state, options) {
    let { sortBy, sortDesc, page, itemsPerPage } = options;
    const transformedOptions = {};

    if (sortBy.length === 1) {
      transformedOptions.sort_by = sortBy[0];
      transformedOptions.desc = sortDesc[0];
    }

    transformedOptions[state.searchField.toLowerCase()] = state.search;

    const offset = (page - 1) * itemsPerPage;
    let limit = itemsPerPage;

    state.sortOptions = { ...transformedOptions, offset, limit };
  },

  SET_SEARCH(state, search) {
    state.search = search;
    state.sortOptions[state.searchField.toLowerCase()] = search;
  },

  SET_SEARCH_FIELD(state, searchField) {
    state.searchField = searchField;
  },

  SET_NEW_ROLE(state, role) {
    state.newRole = role;
  },

  SET_NEW_ALLOWANCE(state, allowance) {
    state.newAllowance = allowance;
  },

  SET_NEW_STATUS(state, status) {
    state.newStatus = status;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
