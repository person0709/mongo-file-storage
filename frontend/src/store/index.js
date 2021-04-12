import Vue from "vue";
import Vuex from "vuex";
import files from "@/store/modules/files";
import users from "@/store/modules/users";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    notifSnackbar: false,
    notifMessage: "",
    errorSnackbar: false,
    errorMessage: "",
  },
  mutations: {
    SET_NOTIF(state, payload) {
      state.notifSnackbar = payload.show;
      state.notifMessage = payload.message;
    },

    SET_ERROR(state, payload) {
      state.errorSnackbar = payload.show;
      state.errorMessage = payload.message;
    },
  },
  modules: {
    files,
    users,
  },
});
