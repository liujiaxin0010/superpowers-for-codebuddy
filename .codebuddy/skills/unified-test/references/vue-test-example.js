// __test__/dataExchangeConfig.test.js
// 源文件: src/components/systemComponent/dataExchangeConfig.vue
//
// 本文件为标准的 Vue 组件 Jest 测试模板
// 供 vue-test-adapter 生成测试时参考

import { mount, shallowMount, createLocalVue } from "@vue/test-utils";
import DataExchangeConfig from "@/components/systemComponent/dataExchangeConfig.vue";
import Vuex from "vuex";
import flushPromises from "flush-promises";

// 引入UI组件mock
import {
  UButton, UDialog, UForm, UFormItem, UTable, UTableColumn,
  UPagination, UTooltip, USwitch, UTimePicker, UOption,
  USelect, UInput
} from "@/TestMock/UI.js";

const localVue = createLocalVue();
localVue.use(Vuex);

// ============================================================
// Mock 配置区
// ============================================================

// Mock ComScript 全局对象
const mockComScript = {
  STATUSCODE: { success: 0 },
  MSGType: { SUCCEED: "success", FAIL: "error", WARNING: "warning" },
  ajax: jest.fn(),
};
global.ComScript = mockComScript;

// Mock $t 函数（国际化）
const mock$t = (key) => key;

// Mock $confirm（确认框）
const mock$confirm = jest.fn().mockResolvedValue(true);

// Mock 业务子组件
const SubComponent = {
  name: "SubComponent",
  render(h) {
    return h("div", this.$slots.default);
  },
};

// 注册组件
localVue.component("u-button", UButton);
localVue.component("u-dialog", UDialog);
localVue.component("u-form", UForm);
localVue.component("u-form-item", UFormItem);
localVue.component("u-table", UTable);
localVue.component("u-table-column", UTableColumn);
localVue.component("u-pagination", UPagination);
localVue.component("u-input", UInput);
localVue.component("u-select", USelect);
localVue.component("u-option", UOption);
localVue.component("sub-component", SubComponent);

// ============================================================
// 辅助函数区
// ============================================================

// 创建 wrapper 辅助函数
const createWrapper = (options = {}) => {
  const mockActions = {
    getConfigList: jest.fn().mockResolvedValue({
      data: { code: 0, data: [], total: 0 },
    }),
    saveConfig: jest.fn().mockResolvedValue({
      data: { code: 0 },
    }),
    deleteConfig: jest.fn().mockResolvedValue({
      data: { code: 0 },
    }),
  };

  const store = new Vuex.Store({
    state: {
      configList: [],
      totalCount: 0,
    },
    actions: mockActions,
  });

  return {
    wrapper: shallowMount(DataExchangeConfig, {
      localVue,
      store,
      mocks: {
        ComScript: mockComScript,
        $t: mock$t,
        $confirm: mock$confirm,
        ...options.mocks,
      },
    }),
    mockActions,
    store,
  };
};

// ============================================================
// 测试用例区
// ============================================================

describe("数据交换配置组件", () => {
  let wrapper;
  let mockActions;
  let store;

  beforeEach(() => {
    jest.clearAllMocks();
    const result = createWrapper();
    wrapper = result.wrapper;
    mockActions = result.mockActions;
    store = result.store;
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.destroy();
    }
  });

  // ----------------------------------------------------------
  // 组件基本渲染
  // ----------------------------------------------------------
  describe("组件基本渲染", () => {
    test("应该正确渲染组件", () => {
      expect(wrapper.exists()).toBe(true);
    });

    test("应该包含正确的根元素", () => {
      const rootElement = wrapper.find(".data-exchange-config");
      expect(rootElement.exists()).toBe(true);
    });
  });

  // ----------------------------------------------------------
  // 方法功能测试
  // ----------------------------------------------------------
  describe("方法功能", () => {
    test("应该正确初始化数据", async () => {
      await wrapper.vm.init();
      await flushPromises();
      expect(mockActions.getConfigList).toHaveBeenCalled();
    });

    test("应该正确加载配置列表", async () => {
      mockActions.getConfigList.mockResolvedValueOnce({
        data: {
          code: 0,
          data: [{ id: 1, name: "config1" }],
          total: 1,
        },
      });
      await wrapper.vm.loadData();
      await flushPromises();
      expect(mockActions.getConfigList).toHaveBeenCalled();
    });

    test("应该正确保存配置", async () => {
      await wrapper.setData({
        formData: { name: "newConfig", value: "test" },
      });
      await wrapper.vm.saveConfig();
      await flushPromises();
      expect(mockActions.saveConfig).toHaveBeenCalled();
    });
  });

  // ----------------------------------------------------------
  // 事件功能测试
  // ----------------------------------------------------------
  describe("事件功能", () => {
    test("应该正确触发搜索", async () => {
      await wrapper.setData({ searchKeyword: "test" });
      await wrapper.vm.handleSearch();
      await flushPromises();
      expect(mockActions.getConfigList).toHaveBeenCalled();
    });

    test("应该正确处理分页变化", async () => {
      await wrapper.vm.handlePageChange(2);
      await flushPromises();
      expect(wrapper.vm.currentPage).toBe(2);
    });
  });

  // ----------------------------------------------------------
  // 边界条件测试
  // ----------------------------------------------------------
  describe("边界条件", () => {
    test("应该处理空列表", async () => {
      await wrapper.setData({ configList: [] });
      await wrapper.vm.$nextTick();
      expect(wrapper.exists()).toBe(true);
    });

    test("应该优雅处理加载错误", async () => {
      mockActions.getConfigList.mockRejectedValueOnce(
        new Error("Network Error")
      );
      const errorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
      await wrapper.vm.loadData();
      await flushPromises();
      expect(wrapper.exists()).toBe(true);
      errorSpy.mockRestore();
    });

    test("应该处理删除确认取消", async () => {
      mock$confirm.mockRejectedValueOnce("cancel");
      await wrapper.vm.handleDelete(1);
      await flushPromises();
      expect(mockActions.deleteConfig).not.toHaveBeenCalled();
    });
  });
});
