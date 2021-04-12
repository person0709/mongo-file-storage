<template>
  <v-app>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import router from "@/router";

export default {
  name: "App",
  components: {},
  beforeCreate() {
    const token = this.$cookies.get("token");
    if (token) {
      this.$store.dispatch("users/fetchCurrentUser");
    } else {
      router.push("/login");
    }
  },
};
</script>
