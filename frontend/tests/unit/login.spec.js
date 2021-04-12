import Login from "@/views/Login";
import { createLocalVue, mount } from "@vue/test-utils";
import Vuetify from "vuetify";
import VueRouter from "vue-router";

describe("Login.vue", () => {
  const localVue = createLocalVue();
  let vuetify;
  let router;

  beforeEach(() => {
    vuetify = new Vuetify();
    router = new VueRouter();
  });

  it("should have title", function () {
    const wrapper = mount(Login, {
      localVue,
      vuetify,
      stubs: ["router-link", "router-view"],
    });

    expect(wrapper.find(".v-toolbar__title").text()).toMatch("File Storage");
  });

  it("should have a form", function () {
    const wrapper = mount(Login, {
      localVue,
      vuetify,
      stubs: ["router-link", "router-view"],
    });

    expect(wrapper.find(".v-form").exists()).toBe(true);
  });

  it("should have a register link", function () {
    const wrapper = mount(Login, {
      localVue,
      vuetify,
      router,
      stubs: ["router-view"],
    });

    expect(wrapper.find("a").text()).toMatch("Need an account?");
    expect(wrapper.find("a").attributes().href).toContain("/register");
  });

  it("should have a login button", async function () {
    const wrapper = mount(Login, {
      localVue,
      vuetify,
      router,
      stubs: ["router-link", "router-view"],
    });

    const button = wrapper.find("button");
    expect(button.text()).toMatch("Login");
  });
});
