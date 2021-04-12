<template>
  <v-dialog v-model="dialog" persistent max-width="600px">
    <v-card class="pb-0">
      <v-card-title>
        <v-col><span class="text-h5">Edit User</span></v-col>
        <v-col>{{ this.editingUser.username }}</v-col>
      </v-card-title>
      <v-card-text>
        <v-list subheader>
          <v-subheader>Storage Allowance</v-subheader>
          <v-divider></v-divider>
          <v-list-item>
            <v-container>
              <v-row>
                <v-col cols="5">
                  <span
                    class="display-1"
                    v-text="
                      this.editingUser.storage_allowance / 1000 / 1000 + 'MB'
                    "
                  ></span>
                </v-col>
                <v-col cols="2">
                  <v-icon x-large>mdi-arrow-right-bold</v-icon>
                </v-col>
                <v-col cols="5">
                  <span
                    class="display-1"
                    v-text="newAllowance / 1000 / 1000 + 'MB'"
                  ></span>
                </v-col>
                <v-slider
                  v-model="newAllowance"
                  min="0"
                  max="1000000000"
                  step="10000000"
                  label="New Allowance"
                  inverse-label
                  required
                ></v-slider>
              </v-row>
            </v-container>
          </v-list-item>
          <v-subheader>User Role</v-subheader>
          <v-divider></v-divider>
          <v-list-item>
            <v-container>
              <v-row align="center">
                <v-col cols="5">
                  <span class="display-1" v-text="editingUser.role"></span>
                </v-col>
                <v-col cols="2">
                  <v-icon x-large>mdi-arrow-right-bold</v-icon>
                </v-col>
                <v-col cols="5">
                  <v-select
                    v-model="newRole"
                    :items="['VIEWER', 'UPLOADER', 'ADMIN']"
                    required
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
          </v-list-item>
          <v-subheader>User Status</v-subheader>
          <v-divider></v-divider>
          <v-list-item>
            <v-row justify="center">
              <v-col cols="auto">
                <v-switch
                  :label="newStatus ? 'Active' : 'Inactive'"
                  v-model="newStatus"
                  inset
                ></v-switch>
              </v-col>
            </v-row>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="dialog = false">
          Close
        </v-btn>
        <v-btn color="blue darken-1" text @click="onSaveClicked"> Save </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions, mapState } from "vuex";

export default {
  name: "UserEditDialog",

  computed: {
    ...mapState({
      editingUser: (state) => state.users.editingUser,
      newRole: (state) => state.users.newRole,
      newAllowance: (state) => state.users.newAllowance,
      newStatus: (state) => state.users.newStatus,
    }),

    newRole: {
      get() {
        return this.$store.state.users.newRole;
      },
      set(val) {
        this.$store.commit("users/SET_NEW_ROLE", val);
      },
    },

    newAllowance: {
      get() {
        return this.$store.state.users.newAllowance;
      },
      set(val) {
        this.$store.commit("users/SET_NEW_ALLOWANCE", val);
      },
    },

    newStatus: {
      get() {
        return this.$store.state.users.newStatus;
      },
      set(val) {
        this.$store.commit("users/SET_NEW_STATUS", val);
      },
    },

    dialog: {
      get() {
        return this.$store.state.users.dialog;
      },
      set(value) {
        this.$store.commit("users/SET_USER_EDIT_DIALOG", value);
      },
    },
  },

  methods: {
    ...mapActions("users", ["onEditUserSave"]),

    onSaveClicked() {
      this.onEditUserSave();
    },
  },
};
</script>

<style scoped></style>
