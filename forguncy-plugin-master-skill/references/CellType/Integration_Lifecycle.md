# 和活字格原生功能集成 - 单元格生命周期 (Cell Lifecycle)

## 参考资料
[单元格生命周期 - 活字格V11帮助文档](https://www.grapecity.com.cn/solutions/huozige/help/docs/plugindevelopment/plugindevelop/developcelltypeplugin/integratedwithhzgfunction/celllifecycle)

## 概述
插件单元格在运行时会经历一系列生命周期，通过重写这些方法可以在特定阶段执行自定义逻辑。

## 生命周期顺序
1. `constructor()`: 构造函数
2. `createContent()`: 构建 DOM 结构
3. `onPageLoaded()`: 页面加载完成
4. `destroy()`: 单元格销毁

## 详细说明

### 1. constructor()
**用途**: 单元格被构造时调用，极少使用。
**注意**: 必须调用 `super(...arguments)`。
```javascript
class MyPluginCellType extends Forguncy.Plugin.CellTypeBase {
    constructor() {
        super(...arguments);
        this.initData = "test";
    }
}
```

### 2. createContent()
**用途**: **核心方法**。创建并返回单元格的 DOM 结构 (jQuery 对象)。
**注意**: 此时 DOM 尚未挂载到页面，不要进行依赖 DOM 存在的操作。
```javascript
createContent() {
    const prop = this.CellElement.CellType.MyProperty;
    return $(`<div>${prop}</div>`);
}
```

### 3. onPageLoaded()
**用途**: 页面数据初始化完成后调用。
**推荐操作**:
- 计算公式 (`evaluateFormula`)
- 初始化依赖 DOM 的第三方库
- 绑定复杂事件
```javascript
onPageLoaded() {
    const prop = this.CellElement.CellType.MyProperty;
    const result = this.evaluateFormula(prop);
    this.content.text(result);
}
```

### 4. destroy()
**用途**: 页面跳转或销毁时调用。
**推荐操作**: 解除全局事件绑定、销毁第三方控件实例。
```javascript
destroy() {
    // 清理资源
}
```

### 关于 onLoad()
`onLoad` 是旧版生命周期，调用时机在 DOM 挂载后但数据初始化前。**新版推荐完全使用 `onPageLoaded` 替代**。
