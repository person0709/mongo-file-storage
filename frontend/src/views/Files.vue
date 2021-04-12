<template>
  <v-container>
    <v-progress-linear
      :value="uploadProgress"
      v-show="isUploadDone"
      color="blue"
      buffer-value="2"
      stream
    >
    </v-progress-linear>
    <v-progress-linear
      :value="downloadProgress"
      v-show="isDownloadDone"
      color="green"
      buffer-value="2"
      stream
    >
    </v-progress-linear>
    <v-row justify="center" align="center">
      <v-col align-self="center">
        <FilesTable></FilesTable>
      </v-col>
    </v-row>

    <v-row align="center" justify="center">
      <v-col cols="auto" align-self="center">
        <FileUploadButton></FileUploadButton>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import FilesTable from "@/components/FilesTable";
import FileUploadButton from "@/components/FileUploadButton";
import { mapGetters, mapState } from "vuex";

export default {
  name: "Files",
  components: { FileUploadButton, FilesTable },

  watch: {},

  computed: {
    ...mapState({
      downloadProgress: (state) => state.files.downloadProgress,
      uploadProgress: (state) => state.files.uploadProgress,
    }),

    ...mapGetters("files", ["isDownloadDone", "isUploadDone"]),
  },

  methods: {},
};
</script>

<style scoped></style>
