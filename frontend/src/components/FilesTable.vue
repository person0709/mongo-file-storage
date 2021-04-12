<!--
Component that contains file list. User can view, search and upload files from this page.
-->
<template>
  <v-container>
    <v-row justify="space-between">
      <v-col lg="3" md="4" sm="4" align-self="center">
        <!--        text field for file search-->
        <v-text-field
          v-model="search"
          prepend-icon="mdi-magnify"
          label="search"
          single-line
          hide-details
        ></v-text-field>
      </v-col>
      <!--      storage limit display-->
      <v-col md="4" sm="4" align-self="center">
        <v-icon class="pr-2">mdi-cloud-outline</v-icon>
        <span class="body-1">Storage</span>
        <span class="body-2 float-right"
          >{{ (storageUsed / 1000 / 1000).toFixed(1) }}MB of
          {{ currentUser.storage_allowance / 1000 / 1000 }}MB used
        </span>
        <v-progress-linear :value="storagePercentage" :color="storageColor">
        </v-progress-linear>
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-col>
        <v-card elevation="5" outlined>
          <v-data-table
            :headers="headers"
            :items="fileMetas"
            :loading="tableLoading"
            :options.sync="options"
            :server-items-length="totalFileCount"
            :footer-props="{ 'items-per-page-options': [10, 30, 50] }"
          >
            <!--      convert size in byte to KB or MB depending on the size-->
            <template v-slot:item.size="{ item }">
              {{
                item.size > 1000 * 1000
                  ? (item.size / 1000 / 1000).toFixed(1) + "MB"
                  : (item.size / 1000).toFixed(1) + "KB"
              }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-row align-content="center" align="center">
                <v-col>
                  <v-icon
                    @click="downloadFile(item)"
                    color="green"
                    :disabled="!canDownload"
                  >
                    mdi-download</v-icon
                  >
                </v-col>
                <v-col>
                  <v-icon
                    @click="deleteFile(item)"
                    color="red"
                    :disabled="!canDelete"
                  >
                    mdi-delete</v-icon
                  >
                </v-col>
              </v-row>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";

export default {
  name: "FilesTable",

  data: () => ({
    headers: [
      {
        text: "Filename",
        align: "start",
        value: "filename",
      },
      { text: "Size", value: "size", filterable: false, width: "150px" },
      {
        text: "Uploaded At(UTC)",
        value: "uploaded_at",
        filterable: false,
        width: "250px",
      },
      {
        text: "Actions",
        value: "actions",
        sortable: false,
        filterable: false,
        width: "110px",
      },
    ],
    search: "",
    options: {},
  }),

  watch: {
    // watches for any change in table options such as sort type
    // and fetch the list from server using the option
    options: {
      handler(newVal) {
        this.$store.commit("files/SET_SORT_OPTIONS", newVal);
        this.fetchFileMetas();
      },
      deep: true,
    },

    // watch for any user input in the search field and fetch file list using the input as regex
    search: {
      handler() {
        this.fetchFileSearch(this.search);
      },
    },

    fileMetas: {
      handler() {
        this.$store.commit("files/SET_SORT_OPTIONS", this.options);
        this.fetchStorageUsed();
      },
    },
  },

  computed: {
    ...mapState({
      currentUser: (state) => state.users.currentUser,
      fileMetas: (state) => state.files.fileMetas,
      totalFileCount: (state) => state.files.totalFileCount,
      tableLoading: (state) => state.files.tableLoading,
      storageUsed: (state) => state.files.storageUsed,
    }),

    ...mapGetters("files", [
      "storageColor",
      "storagePercentage",
      "isUploadDone",
    ]),

    ...mapGetters("users", ["canDownload", "canDelete"]),
  },

  methods: {
    ...mapActions("files", [
      "fetchFileMetas",
      "fetchFileSearch",
      "deleteFile",
      "downloadFile",
      "fetchStorageUsed",
    ]),
  },
};
</script>

<style scoped></style>
