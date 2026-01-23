# 活字格 (Forguncy) 插件开发文档索引

本索引旨在帮助开发者（及 AI 助手）快速定位相关技术文档。

## 1. 核心指南 (Core Guides)

*   **SOP 标准流程**: `references/SOP.md`
*   **最佳实践**: `references/SDK_BestPractices.md`
*   **API 速查表**: `references/API_Cheatsheet.md`
*   **项目配置与发布**: `references/Project_Configuration/Plugin_Metadata.md`

## 2. 插件类型参考 (Plugin Types)

### 2.1 服务端命令 (ServerCommand)
*   **基础结构**: `references/ServerCommand/Basic_Structure.md`
*   **数据库交互**: `references/ServerCommand/Other_Database_Interaction.md`
*   **日志记录**: `references/ServerCommand/Other_ServerCommand_Log.md`
*   **异常处理**: `references/ServerCommand/Process_Exception_Handling.md`
*   **返回结果**: `references/ServerCommand/Process_Return_Results.md`
*   **第三方网络请求**: `references/ServerCommand/Other_ThirdParty_Network.md`

#### 属性定义 (Properties)
*   **字符串**: `references/ServerCommand/Add_Property_String.md`
*   **整数/浮点数**: `references/ServerCommand/Add_Property_Integer.md`, `Add_Property_Double.md`
*   **布尔值**: `references/ServerCommand/Add_Property_Boolean.md`
*   **枚举/下拉框**: `references/ServerCommand/Add_Property_Enum.md`, `Add_Property_Dropdown.md`
*   **公式支持**: `references/ServerCommand/Add_Property_Formula.md`
*   **数据源/连接**: `references/ServerCommand/Add_Property_DataSource.md`, `Add_Property_DatabaseConnection.md`
*   **对象/列表**: `references/ServerCommand/Add_Property_Object.md`, `Add_Property_ObjectList.md`

#### 设计器行为 (Designer)
*   **校验**: `references/ServerCommand/Designer_Validation.md`
*   **动态可见性**: `references/ServerCommand/Designer_Dynamic_Visibility.md`
*   **高级折叠**: `references/ServerCommand/Designer_Advanced_Folding.md`

### 2.2 单元格类型 (CellType)
*   **基础结构**: `references/CellType/Basic_Structure.md`
*   **生命周期**: `references/CellType/Integration_Lifecycle.md`
*   **样式支持**: `references/CellType/Support_Cell_Style.md`, `Support_Complex_Style.md`, `Support_Template_Style.md`
*   **调试**: `references/CellType/Integration_DebugDisplay.md`

#### 属性定义 (Properties)
*   **基础类型**: `references/CellType/Add_Property_String.md`, `Add_Property_Integer.md`, `Add_Property_Double.md`, `Add_Property_Boolean.md`
*   **选择类**: `references/CellType/Add_Property_Enum.md`, `Add_Property_Dropdown.md`, `Add_Property_Radio.md`
*   **资源类**: `references/CellType/Add_Property_Image.md`, `Add_Property_Font.md`, `Add_Property_Color.md`
*   **对象/列表**: `references/CellType/Add_Property_Object.md`, `Add_Property_ObjectList.md`, `Add_Property_List.md`, `Add_Property_Tree.md`
*   **功能引用**: `references/CellType/Add_Property_PageName.md`, `Add_Property_ServerCommandName.md`, `Add_Property_RoleSelector.md`
*   **数据绑定**: `references/CellType/Add_Property_Formula.md`, `Add_Property_DataSource.md`, `Add_Property_DatabaseConnection.md`
*   **其他**: `references/CellType/Add_Property_Command.md`, `Add_Property_Percentage.md`

#### 表单行为 (Form Behavior)
*   **值与变更**: `references/CellType/Form_Support_Value.md`, `Form_Support_ValueChange.md`, `Form_Support_DefaultValue.md`
*   **状态控制**: `references/CellType/Form_Support_ReadOnly.md`, `Form_Support_Disable.md`, `Form_Support_DirtyCheck.md`
*   **校验与权限**: `references/CellType/Form_Support_Verification.md`, `Form_Support_Permission.md`
*   **交互**: `references/CellType/Form_Support_TabOrder.md`

#### 设计器集成 (Designer Integration)
*   **预览**: `references/CellType/Designer_Preview.md`
*   **属性交互**: `references/CellType/Designer_Property_Interaction.md`, `Designer_Init_Properties.md`
*   **校验与可见性**: `references/CellType/Designer_Behavior_Validation.md`, `Designer_Dynamic_Visibility.md`
*   **布局与分组**: `references/CellType/Designer_Grouping_Sorting.md`

#### 自定义操作与集成 (Actions & Integration)
*   **自定义操作**: `references/CellType/Action_AdvancedOperations.md`, `Action_DesignTime.md`
*   **动态属性修改**: `references/CellType/Action_ModifyProperty.md`
*   **列表视图 (ListView)**: `references/CellType/Integration_ListView.md`, `Integration_ListView_ClickEdit.md`, `Integration_ListView_DoubleClickEdit.md`, `Integration_ListView_Interaction.md`, `Integration_ListView_FAQ.md`
*   **图片上传**: `references/CellType/Integration_ImageUpload.md`
*   **可见范围**: `references/CellType/Integration_VisibleRange.md`

### 2.3 客户端命令 (ClientCommand)
*   **README**: `references/ClientCommand/README.md`

### 2.4 服务端 API (ServerApi)
*   **README**: `references/ServerApi/README.md`

### 2.5 中间件 (Middleware)
*   **README**: `references/Middleware/README.md`

## 3. 通用功能与特性

*   **属性索引**: `references/ServerCommand/Attribute_Index.md`
*   **搜索支持**: `references/ServerCommand/Attribute_Search.md`
*   **序列化**: `references/ServerCommand/Attribute_Serialization.md`
