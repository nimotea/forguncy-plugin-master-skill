# 插件发布元数据配置指南

在活字格插件开发中，正确的元数据配置对于插件的发布和管理至关重要。这些信息将直接显示在活字格设计器的插件管理界面以及插件市场中。

## 1. 核心元数据 (.csproj 配置)

活字格插件项目基于标准的 .NET 项目结构，主要的元数据通过 `.csproj` 文件中的 `<PropertyGroup>` 进行配置。

### 关键属性说明

| 属性 | 说明 | 示例 |
| :--- | :--- | :--- |
| **Description** | 插件的详细描述，显示在插件管理界面。 | `这是一个用于集成第三方支付的高级插件。` |
| **Authors** | 插件作者或公司名称。 | `MyCompany` |
| **Version** | 插件版本号，遵循 SemVer 规范。 | `1.0.0` |
| **Product** | 产品名称（通常与插件名一致或为所属产品线）。 | `Advanced Payment Plugin` |
| **Copyright** | 版权信息。 | `Copyright © 2024 MyCompany` |
| **PackageIcon** | 插件包图标（在插件列表中显示）。 | `Icon.png` |
| **PackageTags** | 标签，有助于搜索（空格分隔）。 | `Forguncy Payment Integration` |

### 示例代码

```xml
<PropertyGroup>
  <TargetFramework>net6.0</TargetFramework>
  <!-- 插件描述 -->
  <Description>这是一个功能强大的活字格插件，提供了...功能。</Description>
  <!-- 作者 -->
  <Authors>GrapeCity</Authors>
  <!-- 版本号 -->
  <Version>1.0.0</Version>
  <!-- 产品名 -->
  <Product>MyAwesomePlugin</Product>
  <!-- 图标文件引用 (对应 ItemGroup 中的资源) -->
  <PackageIcon>icon.png</PackageIcon>
</PropertyGroup>
```

## 2. 插件图标配置

插件图标是用户识别插件的第一要素。

### 步骤 1: 准备图标文件
*   **格式**: 推荐使用 PNG 格式。
*   **尺寸**: 建议 128x128 像素或更高，以保证在高分屏下的显示效果。
*   **位置**: 将图标文件（如 `icon.png`）放置在项目根目录下。

### 步骤 2: 在 .csproj 中包含图标
你需要将图标文件作为资源包含在项目中，并将其打包路径 (`Pack`) 设置为 `true`，`PackagePath` 设置为根目录（即为空字符串或指定名称）。

```xml
<ItemGroup>
  <!-- Include the icon file -->
  <None Include="icon.png">
    <Pack>True</Pack>
    <PackagePath>\</PackagePath>
  </None>
</ItemGroup>
```

### 步骤 3: 关联图标属性
在 `<PropertyGroup>` 中通过 `<PackageIcon>` 属性引用该文件名。

```xml
<PropertyGroup>
  ...
  <PackageIcon>icon.png</PackageIcon>
  ...
</PropertyGroup>
```

## 3. 内部命令/单元格图标

除了插件包本身的图标，每个具体的命令（ServerCommand/ClientCommand）或单元格（CellType）也可以有自己的图标。这通常通过代码中的特性（Attribute）来配置。

### 使用 Icon 特性

```csharp
[Icon("pack://application:,,,/MyPluginNamespace;component/Resources/CommandIcon.png")]
public class MyCommand : Command
{
    // ...
}
```

*   注意：内部图标通常作为嵌入资源 (`Embedded Resource`) 处理，路径格式为 WPF Pack URI。
*   需要在 `.csproj` 中将这些图标设置为 `Embedded resource`。

```xml
<ItemGroup>
  <EmbeddedResource Include="Resources\CommandIcon.png" />
</ItemGroup>
```

## 4. 常见问题

### Q: 修改了 Description 但设计器中没更新？
A: 尝试重新构建项目，并确保在活字格设计器中卸载旧版插件后重新安装新编译的插件包（或 Zip/Dll）。

### Q: 版本号规则是什么？
A: 活字格插件版本号建议遵循 `主版本.次版本.补丁版本` (X.Y.Z) 的格式。升级插件时，确保新版本号高于旧版本号，活字格会自动处理更新。
