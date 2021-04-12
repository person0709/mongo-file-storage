import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import store from "../store/index";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
    children: [
      {
        path: "/",
        name: "Files",
        component: () =>
          import(/* webpackChunkName: "register" */ "../views/Files.vue"),
      },
      {
        path: "/account",
        name: "Account",
        component: () =>
          import(/* webpackChunkName: "register" */ "../views/Account.vue"),
      },
      {
        path: "/admin",
        name: "Admin",
        component: () =>
          import(/* webpackChunkName: "register" */ "../views/Admin.vue"),
        async beforeEnter(to, from, next) {
          await store.dispatch("users/fetchCurrentUser");
          const currentUserRole = store.state.users.currentUser.role;
          if (currentUserRole !== "ADMIN") {
            alert("This page is only for admins");
            next(false);
          } else next();
        },
      },
    ],
  },
  {
    path: "/login",
    name: "Login",
    component: () =>
      import(/* webpackChunkName: "login" */ "../views/Login.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () =>
      import(/* webpackChunkName: "register" */ "../views/Register.vue"),
  },
];

const router = new VueRouter({
  mode: "history",
  routes,
});

export default router;
