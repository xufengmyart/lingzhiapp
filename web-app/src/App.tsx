import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import LoginFull from './pages/LoginFull'
import RegisterManual from './pages/RegisterManual'
import AdminLogin from './pages/AdminLogin'
import ForgotPassword from './pages/ForgotPassword'

import ApiConfig from './pages/ApiConfig'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import ChatTest from './pages/ChatTest'

import Economy from './pages/Economy'
import Partner from './pages/Partner'
import Profile from './pages/Profile'
import SecuritySettings from './pages/SecuritySettings'
import UserGuide from './pages/UserGuide'
import ValueGuide from './pages/ValueGuide'
import Feedback from './pages/Feedback'
import MediumVideoProject from './pages/MediumVideoProject'
import XianAesthetics from './pages/XianAesthetics'
import ChangePassword from './pages/ChangePassword'

import WeChatCallback from './pages/WeChatCallback'
import Recharge from './pages/Recharge'
import AdminDashboard from './pages/AdminDashboard'
import AgentManagement from './pages/AgentManagement'
import KnowledgeManagement from './pages/KnowledgeManagement'
import AdminModules from './pages/AdminModules'
import UserManagementEnhanced from './pages/UserManagementEnhanced'
import UserProfileEdit from './pages/UserProfileEdit'
import ContributionManagement from './pages/ContributionManagement'
import RoleManagement from './pages/RoleManagement'
import UserTypeManagement from './pages/UserTypeManagement'
import UserResources from './pages/UserResources'
import ProjectPool from './pages/ProjectPool'
import MerchantPool from './pages/MerchantPool'
import MerchantDetail from './pages/MerchantDetail'
import AestheticTasks from './pages/AestheticTasks'
import DigitalAssets from './pages/DigitalAssets'
import Docs from './pages/Docs'
import BountyHunter from './pages/BountyHunter'
import Knowledge from './pages/Knowledge'
import CultureTranslation from './pages/CultureTranslation'
import CultureProjects from './pages/CultureProjects'
import CompanyNews from './pages/CompanyNews'
import CompanyProjects from './pages/CompanyProjects'
import CompanyInfo from './pages/CompanyInfo'
import CompanyUsers from './pages/CompanyUsers'
import CompanyKnowledge from './pages/CompanyKnowledge'
import ReferralPage from './pages/ReferralPage'
import DividendPool from './pages/DividendPool'
import Journey from './pages/Journey'
import Assets from './pages/Assets'
import AssetManagement from './pages/AssetManagement'
import SacredSitesManagement from './pages/SacredSitesManagement'
import CulturalProjectsManagement from './pages/CulturalProjectsManagement'
import UserLearning from './pages/UserLearning'
import MerchantWorkbench from './pages/MerchantWorkbench'
import ExpertWorkbench from './pages/ExpertWorkbench'
import AnalyticsDashboard from './pages/AnalyticsDashboard'
import UserResourcesMarket from './pages/UserResourcesMarket'
import PrivateResourceLibrary from './pages/PrivateResourceLibrary'
import ProjectRecommendations from './pages/ProjectRecommendations'
import ProjectWorkflow from './pages/ProjectWorkflow'
import ResourceManagement from './pages/ResourceManagement'
import ProjectManagement from './pages/ProjectManagement'
import MerchantManagement from './pages/MerchantManagement'
import CulturalSitesManagement from './pages/CulturalSitesManagement'
import EconomyManagement from './pages/EconomyManagement'
import OperationsManagement from './pages/OperationsManagement'
import BatchImport from './pages/BatchImport'
import AssetMarket from './pages/AssetMarket'
import ErrorLogs from './pages/ErrorLogs'
import APIMonitor from './pages/APIMonitor'
import NewsArticles from './pages/NewsArticles'
import UserNotifications from './pages/UserNotifications'
import RechargeHistory from './pages/RechargeHistory'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import OnboardingGuard from './components/OnboardingGuard'
import { Outlet } from 'react-router-dom'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginFull />} />
      <Route path="/login-full" element={<LoginFull />} />
      <Route path="/register" element={<RegisterManual />} />
      <Route path="/api-config" element={<ApiConfig />} />
      <Route path="/wechat/callback" element={<WeChatCallback />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/referral" element={<ReferralPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<OnboardingGuard />}>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/knowledge" element={<Knowledge />} />
            <Route path="/chat-test" element={<ChatTest />} />
            <Route path="/economy" element={<Economy />} />
            <Route path="/partner" element={<Partner />} />
            <Route path="/guide" element={<UserGuide />} />
            <Route path="/value-guide" element={<ValueGuide />} />
            <Route path="/medium-video" element={<MediumVideoProject />} />
            <Route path="/xian-aesthetics" element={<XianAesthetics />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/change-password" element={<ChangePassword />} />
            <Route path="/security" element={<SecuritySettings />} />
            <Route path="/recharge" element={<Recharge />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/user-resources" element={<UserResources />} />
            <Route path="/project-pool" element={<ProjectPool />} />
            <Route path="/merchant-pool" element={<MerchantPool />} />
            <Route path="/merchant-detail/:id" element={<MerchantDetail />} />
            <Route path="/aesthetic-tasks" element={<AestheticTasks />} />
            <Route path="/digital-assets" element={<DigitalAssets />} />
            <Route path="/docs" element={<Docs />} />
            <Route path="/docs/:slug" element={<Docs />} />
            <Route path="/bounty-hunter" element={<BountyHunter />} />
            <Route path="/dividend-pool" element={<DividendPool />} />
            <Route path="/journey" element={<Journey />} />
            <Route path="/assets" element={<Assets />} />
            <Route path="/asset-management" element={<AssetManagement />} />
            <Route path="/sacred-sites" element={<SacredSitesManagement />} />
            <Route path="/culture-translation" element={<CultureTranslation />} />
            <Route path="/culture-projects" element={<CultureProjects />} />
            <Route path="/cultural-projects" element={<CulturalProjectsManagement />} />
            <Route path="/user-learning" element={<UserLearning />} />
            <Route path="/user-resources" element={<UserResourcesMarket />} />
            <Route path="/company/news" element={<CompanyNews />} />
            <Route path="/company/projects" element={<CompanyProjects />} />
            <Route path="/company/info" element={<CompanyInfo />} />
            <Route path="/company/users" element={<CompanyUsers />} />
            <Route path="/company/knowledge" element={<CompanyKnowledge />} />
            <Route path="/merchant-workbench" element={<MerchantWorkbench />} />
            <Route path="/expert-workbench" element={<ExpertWorkbench />} />
            <Route path="/admin/analytics" element={<AnalyticsDashboard />} />
            <Route path="/private-resources" element={<PrivateResourceLibrary />} />
            <Route path="/project-recommendations" element={<ProjectRecommendations />} />
            <Route path="/project-workflow" element={<ProjectWorkflow />} />
            <Route path="/asset-market" element={<AssetMarket />} />
            <Route path="/news" element={<NewsArticles />} />
            <Route path="/notifications" element={<UserNotifications />} />
            <Route path="/recharge-history" element={<RechargeHistory />} />
          </Route>
        </Route>
      </Route>

      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/admin/modules" element={<AdminModules />} />
      <Route path="/admin/users" element={<UserManagementEnhanced />} />
      <Route path="/admin/users/:userId/edit" element={<UserProfileEdit />} />
      <Route path="/admin/contribution" element={<ContributionManagement />} />
      <Route path="/admin/roles" element={<RoleManagement />} />
      <Route path="/admin/user-types" element={<UserTypeManagement />} />
      <Route path="/admin/agents" element={<AgentManagement />} />
      <Route path="/admin/knowledge" element={<KnowledgeManagement />} />
      <Route path="/admin/resources" element={<ResourceManagement />} />
      <Route path="/admin/projects" element={<ProjectManagement />} />
      <Route path="/admin/merchants" element={<MerchantManagement />} />
      <Route path="/admin/cultural-sites" element={<CulturalSitesManagement />} />
      <Route path="/admin/economy" element={<EconomyManagement />} />
      <Route path="/admin/operations" element={<OperationsManagement />} />
      <Route path="/admin/batch-import" element={<BatchImport />} />
      <Route path="/admin/error-logs" element={<ErrorLogs />} />
      <Route path="/admin/api-monitor" element={<APIMonitor />} />
    </Routes>
  )
}

const AppWrapper: React.FC = () => {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  )
}

export default AppWrapper
// Build timestamp: 1770600145
