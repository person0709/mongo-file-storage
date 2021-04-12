<template>
  <v-container fluid>
    <v-app-bar app color="primary">
      <v-app-bar-nav-icon @click.stop="sidebar = !sidebar"></v-app-bar-nav-icon>
      <v-spacer></v-spacer>
      <v-btn small @click="logout">
        <v-icon left> mdi-logout </v-icon>
        Logout
      </v-btn>
    </v-app-bar>
    <v-navigation-drawer
      app
      v-model="sidebar"
      floating
      :mini-variant.sync="mini"
      color="light-blue lighten-5"
    >
      <v-list-item class="pa-1 pl-2">
        <v-list-item-avatar>
          <v-icon large>mdi-database</v-icon>
        </v-list-item-avatar>
        <v-list-item-title class="title" v-show="!mini">
          File Storage
        </v-list-item-title>
        <v-btn icon @click.stop="mini = !mini">
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
      </v-list-item>
      <v-divider></v-divider>
      <v-list dense>
        <v-list-item
          v-for="item in items"
          :key="item.title"
          link
          :to="item.href"
          @click.stop="mini = true"
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-snackbar v-model="notifSnackbar" color="green">
      {{ notifMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="notifSnackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar dark v-model="errorSnackbar" color="red">
      <strong>Error!</strong> {{ errorMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="errorSnackbar = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <router-view></router-view>
  </v-container>
</template>

<script>
import Vue from "vue";
import router from "@/router";
import { mapState } from "vuex";

export default {
  name: "Home",
  data: () => ({
    sidebar: false,
    mini: true,
    items: [
      { title: "Home", href: "/", icon: "mdi-home" },
      { title: "Account", href: "/account", icon: "mdi-account" },
      { title: "Admin", href: "/admin", icon: "mdi-account-tie" },
    ],
  }),
  computed: {
    ...mapState(["notifMessage", "errorMessage"]),

    notifSnackbar: {
      get() {
        return this.$store.state.notifSnackbar;
      },
      set(value) {
        this.$store.commit("SET_NOTIF", { show: value, message: "" });
      },
    },

    errorSnackbar: {
      get() {
        return this.$store.state.errorSnackbar;
      },
      set(value) {
        this.$store.commit("SET_ERROR", { show: value, message: "" });
      },
    },
  },
  methods: {
    logout() {
      Vue.$cookies.remove("token");
      router.push("/login");
    },
  },

  beforeCreate() {
    this.$store.dispatch("users/fetchCurrentUser");
  },
};
</script>
