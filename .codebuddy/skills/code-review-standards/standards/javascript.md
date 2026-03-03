# JavaScript 安全编码规范

> **版本**：V2.0 &nbsp;|&nbsp; **适用范围**：所有基于 JavaScript/React 进行前端开发的产品  
> **级别定义**：【规则】必须遵守的强制约定 ·【建议】应加以考虑的推荐约定

---

## 1 基本格式化

### 1.1 缩进与行长度

| 项目 | 规范 |
|------|------|
| 缩进 | 2 个空格，禁止使用 Tab |
| 行长度 | 单行不超过 120 个字符 |
| 换行 | 在运算符之后换行，下一行增加 4 个空格缩进 |
| 语句结尾 | 必须以分号结尾 |

### 1.2 空格规则

- 关键词后跟括号须用空格隔开：`if (condition)`
- 逗号和冒号之后保留一个空格
- 二元运算符前后各一个空格
- 点号前后不加空格
- 函数名与左括号之间不加空格
- 括号内侧不加空格

### 1.3 文件规范

| 项目 | 规范 |
|------|------|
| 编码 | UTF-8 |
| 文件名 | 全小写，禁止缩写或首字母组合 |
| React 组件文件 | 后缀使用 `.jsx`，文件名与公共组件一致 |
| JS 文件 | 后缀使用 `.js` |

---

## 2 安全编码规则

### 2.1 【规则】禁止使用 `eval()` 执行动态代码

`eval()` 会执行传入的任意字符串作为代码，是 XSS 和代码注入的主要入口。仅在解析序列化串（如 JSON）时可有限使用，优先使用 `JSON.parse()`。

```javascript
// ✗ 危险
eval(userInput);

// ✓ 安全
const data = JSON.parse(jsonString);
```

### 2.2 【规则】禁止使用 `with` 语句

`with` 语句的作用域解析行为不可预测，可能导致安全漏洞和调试困难。

### 2.3 【规则】仅在函数内使用 `this`

禁止在全局作用域使用 `this`。在 React 组件中，`this` 可能出现指向变更的场景时，须使用箭头函数强制绑定。

```javascript
// ✓ 箭头函数绑定 this
handleClick = () => {
  this.setState({ clicked: true });
};
```

### 2.4 【规则】禁止在生产代码中保留调试语句

禁止上库 `debugger`、`alert()` 和无关的 `console.log`。

### 2.5 【规则】使用 `===` 和 `!==` 代替 `==` 和 `!=`

严格相等运算符避免了弱类型自动转换带来的安全隐患和逻辑错误。

```javascript
// ✓ 正确
if (a === b) { ... }

// ✗ 错误：可能因类型转换产生非预期结果
if (a == b) { ... }
```

### 2.6 【规则】变量声明使用 `let` / `const`，禁止使用 `var`

`var` 的函数作用域和变量提升特性容易导致意外的变量泄露和覆盖。

- `const`：不会被重新赋值的变量
- `let`：会被重新赋值的变量

### 2.7 【规则】禁止对函数参数重新赋值

对参数赋值会修改 `arguments` 对象，导致混乱。

```javascript
// ✗ 错误
function foo(bar) {
  bar = 13;
}

// ✓ 正确
function foo(bar) {
  const localBar = bar || 13;
}
```

### 2.8 【规则】禁止出现重复的函数参数名

后出现的同名参数会覆盖前面的参数。

### 2.9 【规则】禁止封装基本类型

```javascript
// ✗ 错误
const str = new String("hello");
const num = new Number(10);

// ✓ 正确
const str = "hello";
const num = 10;
```

### 2.10 【规则】减少魔法数字

对重要常量须赋予有意义的名称。

```javascript
// ✓ 正确
const ONE_DAY_MS = 3600 * 24 * 1000;
const tomorrow = today + ONE_DAY_MS;

// ✗ 错误
const tomorrow = today + 86400000;
```

---

## 3 类型安全

### 3.1 【规则】`null` 的使用规范

**允许使用 `null` 的场景**：
- 初始化可能赋值为对象的变量
- 与已初始化的变量比较
- 函数参数或返回值期望为对象时

**禁止使用 `null` 的场景**：
- 检测是否传入了某个参数
- 检测未初始化的变量

### 3.2 【规则】判断变量是否定义须使用 `typeof`

```javascript
// ✓ 正确
if (typeof variable === "undefined") { ... }

// ✗ 错误：undefined 可能被覆盖
if (variable === undefined) { ... }
```

### 3.3 【规则】小数运算须使用 `toFixed()` 避免精度丢失

```javascript
const result = (0.1 + 0.2).toFixed(2);  // "0.30"
```

### 3.4 【建议】数字避免使用八进制表示

八进制已废弃，容易造成混淆。

---

## 4 函数安全

### 4.1 【规则】函数在使用前定义

### 4.2 【规则】其他函数内定义的函数须在变量声明之后

### 4.3 【规则】立即执行函数须用圆括号包裹

```javascript
// ✓ 正确
const value = (function() {
  return { message: "Hi" };
}());

// ✗ 错误：外层缺少括号
const value = function() {
  return { message: "Hi" };
}();
```

### 4.4 【规则】控制代码嵌套深度

嵌套层级不宜超过 3-4 层，过深的嵌套应拆分为独立函数或使用提前返回（early return）模式。

---

## 5 DOM 与浏览器安全

### 5.1 【规则】禁止将用户输入直接插入 DOM

使用 `textContent` 而非 `innerHTML` 输出用户数据，或使用专业的 XSS 过滤库（如 DOMPurify）。

```javascript
// ✗ 危险：XSS 风险
element.innerHTML = userInput;

// ✓ 安全：纯文本输出
element.textContent = userInput;

// ✓ 安全：使用 DOMPurify 过滤
element.innerHTML = DOMPurify.sanitize(userInput);
```

### 5.2 【规则】URL 参数须编码后使用

```javascript
const safeParam = encodeURIComponent(userInput);
const url = `/api/search?q=${safeParam}`;
```

### 5.3 【规则】敏感操作须验证请求来源

表单提交和 AJAX 请求须携带 CSRF Token 进行验证。

### 5.4 【规则】敏感数据禁止存储在前端

口令、密钥、令牌等敏感信息不得存储在 `localStorage`、`sessionStorage`、Cookie（无 `HttpOnly` 标志）或 URL 参数中。

### 5.5 【规则】第三方脚本引入须验证完整性

使用 CDN 引入外部脚本时，须添加 SRI（Subresource Integrity）校验。

```html
<script src="https://cdn.example.com/lib.js"
  integrity="sha384-xxxx"
  crossorigin="anonymous"></script>
```

---

## 6 React 特有规则

### 6.1 【规则】JSX 中变量声明禁止使用 `var`

### 6.2 【规则】JSX 使用双引号，其他 JS 属性使用单引号

### 6.3 【规则】生命周期方法须严格按标准顺序排列

`constructor` → `componentDidMount` → `shouldComponentUpdate` → `componentDidUpdate` → `componentWillUnmount` → 事件处理 → render 辅助方法 → `render`

### 6.4 【规则】单个 JSX 文件只能有一个公共组件

### 6.5 【规则】禁止使用 `dangerouslySetInnerHTML` 输出未过滤的用户数据

如确需使用，必须先通过 DOMPurify 等库进行 XSS 过滤。

---

## 7 注释规范

### 7.1 【规则】函数须添加 JSDoc 注释

包含函数用途、参数类型与说明、返回值类型与描述。

```javascript
/**
 * 计算两数之和
 * @param {number} a - 加数
 * @param {number} b - 被加数
 * @returns {number} 两数之和
 */
function add(a, b) {
  return a + b;
}
```

### 7.2 【规则】修改注释须定期清理

避免过时的修改注释堆积降低可读性。

---

## 8 安全检查工具

### 8.1 【建议】推荐使用以下安全扫描工具

| 工具 | 用途 |
|------|------|
| ESLint + eslint-plugin-security | JS 代码安全规则检查 |
| npm audit | 依赖包漏洞扫描 |
| Snyk | 第三方依赖安全检测 |
| SonarQube | 综合代码质量与安全分析 |

---

## 参考文献

- OWASP Cheat Sheet Series — DOM-based XSS Prevention
- ESLint Security Plugin (https://github.com/eslint-community/eslint-plugin-security)
- MDN Web Security Guidelines
