<template>
  <v-container>
    <v-row>
      <v-col cols="6">
        <v-text-field
          v-model="search"
          prepend-icon="mdi-magnify"
          label="Search"
        ></v-text-field>
      </v-col>
      <v-spacer></v-spacer>
      <v-col cols="3">
        <v-select
          v-model="searchField"
          :items="['Username', 'Email']"
          label="Search by"
        ></v-select>
      </v-col>
    </v-row>
    <v-card elevation="5" outlined>
      <v-data-table
        :headers="headers"
        :items="usersInTable"
        :loading="tableLoading"
        :options.sync="options"
        :server-items-length="usersCount"
        :footer-props="{ 'items-per-page-options': [10, 30, 50] }"
      >
        <!--      convert size in byte to KB or MB depending on the size-->
        <template v-slot:item.storage_allowance="{ item }">
          {{
            item.storage_allowance > 1000 * 1000
              ? (item.storage_allowance / 1000 / 1000).toFixed(1) + "MB"
              : (item.storage_allowance / 1000).toFixed(1) + "KB"
          }}
        </template>
        <template v-slot:item.storage_used="{ item }">
          {{
            item.storage_used > 1000 * 1000
              ? (item.storage_used / 1000 / 1000).toFixed(1) + "MB"
              : (item.storage_used / 1000).toFixed(1) + "KB"
          }}
        </template>
        <template v-slot:item.is_active="{ item }">
          {{ item.is_active === true ? "Active" : "Inactive" }}
        </template>
        <template v-slot:item.edit="{ item }">
          <v-row>
            <v-col cols="6">
              <v-icon @click.stop="openUserEditDialog(item)" color="indigo">
                mdi-pencil</v-icon
              >
            </v-col>
            <v-col cols="6">
              <v-icon @click="deleteUser(item)" color="red"> mdi-delete</v-icon>
            </v-col>
          </v-row>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script>
import { mapActions, mapState } from "vuex";

export default {
  name: "UsersTable",

  data: () => ({
    headers: [
      {
        text: "User ID",
        align: "start",
        value: "user_id",
        sortable: false,
        width: "20%",
      },
      { text: "Username", value: "username", filterable: false },
      { text: "Email", value: "email", filterable: false },
      {
        text: "Allowance",
        value: "storage_allowance",
        filterable: false,
        width: "7%",
      },
      { text: "Used", value: "storage_used", filterable: false, width: "7%" },
      { text: "Role", value: "role", filterable: false, width: "5%" },
      {
        text: "Joined At(UTC)",
        value: "joined_at",
        filterable: false,
        width: "10%",
      },
      { text: "Status", value: "is_active", filterable: false, width: "5%" },
      {
        text: "Actions",
        value: "edit",
        sortable: false,
        align: "center",
        filterable: false,
        width: "7%",
      },
    ],
    options: {},
    search: "",
    searchField: "Username",
  }),

  watch: {
    // watches for any change in table options such as sort type
    // and fetch the list from server using the option
    options: {
      handler(newVal) {
        this.$store.commit("users/SET_SORT_OPTIONS", newVal);
        this.fetchUserList();
      },
      deep: true,
    },
    search: {
      handler(newVal) {
        // reset page to page 1 for every input
        this.options.page = 1
        this.$store.commit("users/SET_SEARCH", newVal);
        this.fetchUserList();
      },
    },

    searchField: {
      handler(newVal) {
        // reset page to page 1 for every input
        this.options.page = 1
        this.$store.commit("users/SET_SEARCH_FIELD", newVal);
      },
    },
  },

  computed: {
    ...mapState({
      usersInTable: (state) => state.users.usersInTable,
      usersCount: (state) => state.users.usersCount,
      tableLoading: (state) => state.users.tableLoading,
    }),
  },

  methods: {
    ...mapActions("users", [
      "openUserEditDialog",
      "fetchUserList",
      "deleteUser",
    ]),
  },
};
</script>

<style scoped></style>
