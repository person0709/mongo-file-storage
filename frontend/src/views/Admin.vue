<!--
Vue file for admin page. It contains page for various admin actions such as user role change.
-->
<template>
  <v-container fill-height>
    <h1>Admin Page</h1>
    <v-divider inset></v-divider>
    <v-row align="center" justify="center">
      <v-col>
        <UsersTable></UsersTable>
        <UserEditDialog></UserEditDialog>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import UsersTable from "@/components/UsersTable";
import UserEditDialog from "@/components/UserEditDialog";

export default {
  name: "Admin",
  components: { UserEditDialog, UsersTable },
};
</script>

<style scoped></style>
