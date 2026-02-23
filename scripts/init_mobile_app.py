#!/usr/bin/env python3
"""
移动端项目初始化脚本
使用 React Native 创建移动端应用
"""

import os
import subprocess
import json

def run_command(cmd, description):
    """执行命令"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print('='*60)

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)

    if result.stderr:
        print("错误输出:", result.stderr)

    if result.returncode != 0:
        print(f"❌ {description} 失败 (退出码: {result.returncode})")
        return False

    print(f"✓ {description} 成功")
    return True

def main():
    print("="*60)
    print("灵值生态园移动端项目初始化")
    print("="*60)

    project_name = "LingzhiEcosystemApp"
    base_dir = "/workspace/projects"
    project_dir = os.path.join(base_dir, project_name)

    # 1. 创建项目目录
    print("\n创建项目目录...")
    os.makedirs(project_dir, exist_ok=True)

    # 2. 初始化 React Native 项目
    print("\n初始化 React Native 项目...")
    if os.path.exists(os.path.join(project_dir, "package.json")):
        print("项目已存在，跳过初始化")
    else:
        # 使用 npx 创建 React Native 项目
        if not run_command(
            f"cd {base_dir} && npx react-native@latest init {project_name}",
            "初始化 React Native 项目"
        ):
            return

    # 3. 创建项目结构
    print("\n创建项目结构...")
    dirs = [
        "src",
        "src/screens",
        "src/components",
        "src/navigation",
        "src/services",
        "src/store",
        "src/utils",
        "src/assets",
        "src/assets/images",
        "src/assets/fonts",
        "src/config",
        "src/contexts",
    ]

    for dir_path in dirs:
        full_path = os.path.join(project_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"✓ 创建目录: {dir_path}")

    # 4. 创建配置文件

    # API 配置
    api_config = """// API 配置
const API_BASE_URL = 'https://meiyueart.com/api';

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  TIMEOUT: 30000,
};

export const API_ENDPOINTS = {
  // 认证
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',

  // 用户
  USER_INFO: '/user/info',

  // 圣地
  SACRED_SITES: '/sacred-sites',
  SACRED_SITE_DETAIL: (id) => `/sacred-sites/${id}`,

  // 项目
  CULTURAL_PROJECTS: '/cultural-projects',

  // 资产
  TOKENS: '/tokens',
  USER_TOKENS: '/user/tokens',

  // 智能体
  AGENT_CHAT: '/agent/chat',
  AGENT_CONVERSATIONS: '/agent/conversations',

  // 通知
  NOTIFICATIONS: '/notifications',
};

export default API_CONFIG;
"""

    with open(os.path.join(project_dir, "src/config/api.ts"), "w") as f:
        f.write(api_config)

    # 主题配置
    theme_config = """// 主题配置
export const COLORS = {
  primary: '#4F46E5',
  secondary: '#8B5CF6',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6',

  background: '#F9FAFB',
  surface: '#FFFFFF',
  text: '#111827',
  textSecondary: '#6B7280',
  border: '#E5E7EB',
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const FONTS = {
  size: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 32,
  },
  weight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
};

export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

export const SHADOWS = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
};

export default {
  COLORS,
  SPACING,
  FONTS,
  BORDER_RADIUS,
  SHADOWS,
};
"""

    with open(os.path.join(project_dir, "src/config/theme.ts"), "w") as f:
        f.write(theme_config)

    # 5. 创建导航配置
    navigation_config = """// 导航配置
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createNativeStackNavigator} from '@react-navigation/native-stack';

// 这里将导入实际的屏幕组件
const HomeScreen = () => null;
const SacredSitesScreen = () => null;
const ProjectsScreen = () => null;
const AssetsScreen = () => null;
const ProfileScreen = () => null;

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// 底部标签导航
function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
      }}>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="SacredSites" component={SacredSitesScreen} />
      <Tab.Screen name="Projects" component={ProjectsScreen} />
      <Tab.Screen name="Assets" component={AssetsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

// 主导航
export function RootNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="MainTabs"
        component={TabNavigator}
        options={{headerShown: false}}
      />
    </Stack.Navigator>
  );
}
"""

    with open(os.path.join(project_dir, "src/navigation/AppNavigator.tsx"), "w") as f:
        f.write(navigation_config)

    # 6. 创建 API 服务
    api_service = """// API 服务
import API_CONFIG, {API_ENDPOINTS} from '../config/api';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // 添加 Token
    const token = this.getToken();
    if (token) {
      defaultOptions.headers = {
        ...defaultOptions.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    try {
      const response = await fetch(url, defaultOptions);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || '请求失败');
      }

      return data;
    } catch (error) {
      console.error('API 请求错误:', error);
      throw error;
    }
  }

  private getToken(): string | null {
    // 从 AsyncStorage 获取 Token
    return null;
  }

  // 认证
  async login(username: string, password: string) {
    return this.request(API_ENDPOINTS.LOGIN, {
      method: 'POST',
      body: JSON.stringify({username, password}),
    });
  }

  async register(userData: any) {
    return this.request(API_ENDPOINTS.REGISTER, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getUserInfo() {
    return this.request(API_ENDPOINTS.USER_INFO);
  }

  // 圣地
  async getSacredSites() {
    return this.request(API_ENDPOINTS.SACRED_SITES);
  }

  async getSacredSiteDetail(id: number) {
    return this.request(API_ENDPOINTS.SACRED_SITE_DETAIL(id));
  }

  // 项目
  async getCulturalProjects() {
    return this.request(API_ENDPOINTS.CULTURAL_PROJECTS);
  }

  // 资产
  async getUserTokens() {
    return this.request(API_ENDPOINTS.USER_TOKENS);
  }

  // 智能体
  async chat(conversationId: string, message: string) {
    return this.request(API_ENDPOINTS.AGENT_CHAT, {
      method: 'POST',
      body: JSON.stringify({conversationId, message}),
    });
  }

  // 通知
  async getNotifications() {
    return this.request(API_ENDPOINTS.NOTIFICATIONS);
  }
}

export default new ApiService();
"""

    with open(os.path.join(project_dir, "src/services/api.ts"), "w") as f:
        f.write(api_service)

    # 7. 创建 README
    readme = """# 灵值生态园移动端应用

## 项目简介
灵值生态园的 React Native 移动端应用，支持 iOS 和 Android 平台。

## 技术栈
- React Native
- TypeScript
- React Navigation
- Redux Toolkit
- Axios

## 功能特性
- 用户认证（登录/注册）
- 圣地管理
- 文化项目管理
- 资产管理
- 智能体对话
- 通知系统
- 用户画像

## 安装依赖
\`\`\`bash
npm install
\`\`\`

## 运行应用

### iOS
\`\`\`bash
npm run ios
\`\`\`

### Android
\`\`\`bash
npm run android
\`\`\`

## 构建应用

### iOS
\`\`\`bash
npm run build:ios
\`\`\`

### Android
\`\`\`bash
npm run build:android
\`\`\`

## 项目结构
\`\`\`
src/
├── assets/          # 资源文件
├── components/      # 组件
├── config/          # 配置文件
├── contexts/        # 上下文
├── navigation/      # 导航
├── screens/         # 页面
├── services/        # 服务
├── store/           # 状态管理
└── utils/           # 工具函数
\`\`\`

## 环境变量
创建 `.env` 文件：
\`\`\`
API_BASE_URL=https://meiyueart.com/api
\`\`\`

## 开发指南
1. 确保安装了 Node.js 和 React Native CLI
2. 安装依赖：`npm install`
3. 启动开发服务器：`npm start`
4. 运行应用：`npm run ios` 或 `npm run android`

## 发布
### iOS
1. 更新版本号和构建号
2. 构建 Archive
3. 上传到 App Store

### Android
1. 更新版本号
2. 生成签名 APK 或 AAB
3. 上传到 Google Play

## 联系方式
- 项目地址：https://meiyueart.com
- 问题反馈：support@meiyueart.com
"""

    with open(os.path.join(project_dir, "README.md"), "w") as f:
        f.write(readme)

    # 8. 创建 package.json 补充依赖
    print("\n添加依赖...")
    dependencies = [
        "@react-navigation/native",
        "@react-navigation/bottom-tabs",
        "@react-navigation/native-stack",
        "@reduxjs/toolkit",
        "react-redux",
        "axios",
        "@react-native-async-storage/async-storage",
        "react-native-vector-icons",
    ]

    for dep in dependencies:
        run_command(f"cd {project_dir} && npm install {dep}", f"安装 {dep}")

    dev_dependencies = [
        "@types/react-native-vector-icons",
    ]

    for dep in dev_dependencies:
        run_command(f"cd {project_dir} && npm install --save-dev {dep}", f"安装 {dep}")

    print("\n" + "="*60)
    print("✅ 移动端项目初始化完成")
    print("="*60)
    print(f"\n项目目录: {project_dir}")
    print("\n下一步:")
    print("1. cd LingzhiEcosystemApp")
    print("2. npm install")
    print("3. npm run ios    # iOS")
    print("4. npm run android  # Android")

if __name__ == "__main__":
    main()
