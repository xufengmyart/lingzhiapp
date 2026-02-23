import { Routes, Route, lazy, Suspense } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import OnboardingGuard from './components/OnboardingGuard'

// 懒加载所有页面组件
const LoginFull = lazy(() => import('./pages/LoginFull'))
const RegisterManual = lazy(() => import('./pages/RegisterManual'))
const AdminLogin = lazy(() => import('./pages/AdminLogin'))
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'))
const ApiConfig = lazy(() => import('./pages/ApiConfig'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Chat = lazy(() => import('./pages/Chat'))
const ChatTest = lazy(() => import('./pages/ChatTest'))
const Economy = lazy(() => import('./pages/Economy'))
const Partner = lazy(() => import('./pages/Partner'))
const Profile = lazy(() => import('./pages/Profile'))
const SecuritySettings = lazy(() => import('./pages/SecuritySettings'))
const UserGuide = lazy(() => import('./pages/UserGuide'))
const ValueGuide = lazy(() => import('./pages/ValueGuide'))
const Feedback = lazy(() => import('./pages/Feedback'))
const MediumVideoProject = lazy(() => import('./pages/MediumVideoProject'))
const XianAesthetics = lazy(() => import('./pages/XianAesthetics'))
const WeChatCallback = lazy(() => import('./pages/WeChatCallback'))
const Recharge = lazy(() => import('./pages/Recharge'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const AgentManagement = lazy(() => import('./pages/AgentManagement'))
const KnowledgeManagement = lazy(() => import('./pages/KnowledgeManagement'))
const AdminModules = lazy(() => import('./pages/AdminModules'))
const UserManagementEnhanced = lazy(() => import('./pages/UserManagementEnhanced'))
const UserProfileEdit = lazy(() => import('./pages/UserProfileEdit'))
const ContributionManagement = lazy(() => import('./pages/ContributionManagement'))
const RoleManagement = lazy(() => import('./pages/RoleManagement'))
const UserTypeManagement = lazy(() => import('./pages/UserTypeManagement'))
const UserResources = lazy(() => import('./pages/UserResources'))
const ProjectPool = lazy(() => import('./pages/ProjectPool'))
const MerchantPool = lazy(() => import('./pages/MerchantPool'))
const MerchantDetail = lazy(() => import('./pages/MerchantDetail'))
const AestheticTasks = lazy(() => import('./pages/AestheticTasks'))
const DigitalAssets = lazy(() => import('./pages/DigitalAssets'))
const Docs = lazy(() => import('./pages/Docs'))
const BountyHunter = lazy(() => import('./pages/BountyHunter'))
const Knowledge = lazy(() => import('./pages/Knowledge'))
const CultureTranslation = lazy(() => import('./pages/CultureTranslation'))
const CultureProjects = lazy(() => import('./pages/CultureProjects'))
const CompanyNews = lazy(() => import('./pages/CompanyNews'))
const CompanyProjects = lazy(() => import('./pages/CompanyProjects'))
const CompanyInfo = lazy(() => import('./pages/CompanyInfo'))
const CompanyUsers = lazy(() => import('./pages/CompanyUsers'))
const CompanyKnowledge = lazy(() => import('./pages/CompanyKnowledge'))
const ReferralPage = lazy(() => import('./pages/ReferralPage'))
const DividendPool = lazy(() => import('./pages/DividendPool'))
const Journey = lazy(() => import('./pages/Journey'))
const Assets = lazy(() => import('./pages/Assets'))
const AssetManagement = lazy(() => import('./pages/AssetManagement'))
const SacredSitesManagement = lazy(() => import('./pages/SacredSitesManagement'))
const CulturalProjectsManagement = lazy(() => import('./pages/CulturalProjectsManagement'))
const UserLearning = lazy(() => import('./pages/UserLearning'))
const MerchantWorkbench = lazy(() => import('./pages/MerchantWorkbench'))
const ExpertWorkbench = lazy(() => import('./pages/ExpertWorkbench'))
const AnalyticsDashboard = lazy(() => import('./pages/AnalyticsDashboard'))
const UserResourcesMarket = lazy(() => import('./pages/UserResourcesMarket'))
const PrivateResourceLibrary = lazy(() => import('./pages/PrivateResourceLibrary'))
const ProjectRecommendations = lazy(() => import('./pages/ProjectRecommendations'))
const ProjectWorkflow = lazy(() => import('./pages/ProjectWorkflow'))
const ResourceManagement = lazy(() => import('./pages/ResourceManagement'))
const ProjectManagement = lazy(() => import('./pages/ProjectManagement'))
const MerchantManagement = lazy(() => import('./pages/MerchantManagement'))
const CulturalSitesManagement = lazy(() => import('./pages/CulturalSitesManagement'))
const EconomyManagement = lazy(() => import('./pages/EconomyManagement'))
const OperationsManagement = lazy(() => import('./pages/OperationsManagement'))

// 加载指示器组件
const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-50">
    <div className="flex flex-col items-center space-y-4">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      <p className="text-gray-600">加载中...</p>
    </div>
  </div>
)

function App() {
  return (
    <Suspense fallback={<LoadingFallback />}>
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
      </Routes>
    </Suspense>
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
