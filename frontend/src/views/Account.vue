<!--
Vue file for account page. It displays current user's info.
-->
<template>
  <v-container fill-height>
    <v-row align="center" justify="center">
      <v-col lg="4" md="6" sm="8">
        <v-card elevation="10" outlined>
          <v-card-title class="text-h3">
            <v-col>
              {{ currentUser.username }}
            </v-col>
          </v-card-title>
          <v-card-subtitle>
            <v-col>
              {{ currentUser.email }}
            </v-col>
            <v-col class="text-h5">
              {{ currentUser.role }}
            </v-col>
          </v-card-subtitle>
          <v-card-text class="text-right">
            <v-col>
              <span class="text-h5"
                >Plan: {{ currentUser.storage_allowance / 1000 / 1000 }}MB</span
              >
            </v-col>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapState } from "vuex";

export default {
  name: "Account",
  computed: {
    ...mapState({
      currentUser: (state) => state.users.currentUser,
    }),
  },

  methods: {
    ...mapActions(["fetchCurrentUser"]),
  },

  created() {
    this.fetchCurrentUser();
  },
};
</script>

<style scoped></style>
