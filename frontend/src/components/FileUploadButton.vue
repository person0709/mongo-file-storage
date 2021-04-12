<!--
Component for initiating file upload.
-->
<template>
  <v-btn
    :loading="isUploadDone"
    color="blue"
    dark
    min-width="200px"
    :disabled="!canUpload"
    @click="onUploadButtonClick"
  >
    <v-icon>mdi-upload</v-icon>
    <input
      ref="uploader"
      accept="image/*, audio/*, video/*, .pdf, .doc, .docx, .ppt, .pptx, .xls, .xlsx, .txt, .csv"
      hidden="hidden"
      type="file"
      @change="onFileSelected"
    />
    UPLOAD
  </v-btn>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "FileUploadButton",

  computed: {
    ...mapGetters("users", ["canUpload"]),

    ...mapGetters("files", ["isUploadDone"]),
  },

  watch: {},

  methods: {
    onFileSelected(e) {
      if (e.target.files[0] === undefined) {
        return;
      }
      const uploadingFile = e.target.files[0];
      this.$store.dispatch("files/uploadFile", uploadingFile);
    },

    onUploadButtonClick() {
      window.addEventListener("focus", () => {}, { once: true });
      this.$refs.uploader.click();
    },
  },
};
</script>

<style scoped></style>
