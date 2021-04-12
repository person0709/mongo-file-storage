<template>
  <v-container fluid fill-height>
    <v-row align="center" justify="center">
      <v-col xs="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar dark color="primary">
            <v-toolbar-title>Sign up</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <v-form @keyup.enter="submit" v-model="valid">
              <v-text-field
                @keyup.enter="submit"
                v-model="email"
                prepend-icon="mdi-email"
                name="email"
                label="Email"
                type="text"
                :rules="emailRules"
                required
              ></v-text-field>
              <v-text-field
                @keyup.enter="submit"
                v-model="username"
                prepend-icon="mdi-account"
                name="username"
                label="Username"
                type="text"
                :rules="usernameRules"
                required
              ></v-text-field>
              <v-text-field
                @keyup.enter="submit"
                v-model="password"
                prepend-icon="mdi-lock"
                name="password"
                label="Password"
                id="password"
                type="password"
                :rules="passwordRules"
                required
              ></v-text-field>
            </v-form>
            <div v-if="isRegisterError">
              <v-alert
                :value="isRegisterError"
                transition="fade-transition"
                type="error"
              >
                {{ errorMessage }}
              </v-alert>
            </div>
          </v-card-text>
          <v-col
            ><router-link to="/login"
              >Already have an account?</router-link
            ></v-col
          >
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click.prevent="submit" :disabled="!valid">Register</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import api from "@/api";
import router from "@/router";

export default {
  name: "Register",

  data: () => ({
    email: "",
    username: "",
    password: "",
    isRegisterError: false,
    errorMessage: "",
    emailRules: [
      (v) => !!v || "Email is required",
      (v) => /.+@.+/.test(v) || "Email must be valid",
    ],
    usernameRules: [
      (v) => !!v || "Username is required",
      (v) => v.length < 20 || "Username must be less than 20 characters",
    ],
    passwordRules: [
      (v) => !!v || "Password is required",
      (v) => v.length >= 8 || "Password must be longer than 8 characters",
    ],
    valid: false,
  }),

  methods: {
    async submit() {
      try {
        await api.createUser(this.email, this.username, this.password);
        this.isRegisterError = false;
        await router.push("/login");
      } catch (err) {
        this.isRegisterError = true;
        this.errorMessage = err.response.data.detail;
      }
    },
  },
};
</script>

<style scoped></style>
