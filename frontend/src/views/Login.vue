<template>
  <v-container fluid fill-height>
    <v-row align="center" justify="center">
      <v-col xs="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar dark color="primary">
            <v-toolbar-title>File Store</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-form @keyup.enter="submit">
              <v-text-field
                @keyup.enter="submit"
                v-model="email"
                prepend-icon="mdi-email"
                name="login"
                label="Email"
                type="text"
              ></v-text-field>
              <v-text-field
                @keyup.enter="submit"
                v-model="password"
                prepend-icon="mdi-lock"
                name="password"
                label="Password"
                id="password"
                type="password"
              ></v-text-field>
            </v-form>
            <v-col>
              <router-link to="/register">Need an account?</router-link>
            </v-col>
            <div v-if="isLoginError">
              <v-alert
                :value="isLoginError"
                transition="fade-transition"
                type="error"
              >
                Incorrect email or password
              </v-alert>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click.prevent="submit">Login</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import api from "@/api";
import router from "@/router";
import Vue from "vue";

export default {
  name: "Login",
  beforeRouteEnter(to, from, next) {
    // remove existing token whenever user enters login page
    Vue.$cookies.remove("token");
    next();
  },
  data: () => ({
    email: "",
    password: "",
    isLoginError: false,
  }),
  methods: {
    async submit() {
      try {
        // save JWT in cookie
        const response = await api.getToken(this.email, this.password);
        Vue.$cookies.set("token", response.data.access_token);
        this.isLoginError = false;
        await router.push("/");
      } catch (err) {
        console.log(err)
        this.isLoginError = true;
      }
    },
  },
};
</script>

<style scoped></style>
