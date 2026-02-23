import { useState } from 'react'
import { ArrowRight, Sparkles, CheckCircle, ChevronRight } from 'lucide-react'
import { UserType, USER_TYPES, getUserTypeConfig, UserTypeConfig } from '../types/userPersona'
import './Onboarding.css'

// 步骤定义
enum OnboardingStep {
  WELCOME = 'welcome',
  USER_TYPE = 'user_type',
  WHO_AM_I = 'who_am_i',
  WHAT_I_HAVE = 'what_i_have',
  WHAT_I_OFFER = 'what_i_offer',
  GUIDANCE = 'guidance',
  COMPLETE = 'complete'
}

const OnboardingFlow = ({ onComplete }: { onComplete: (userType: UserType) => void }) => {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>(OnboardingStep.WELCOME)
  const [selectedUserType, setSelectedUserType] = useState<UserType | null>(null)
  const [userPersona, setUserPersona] = useState<UserTypeConfig | null>(null)

  // 处理用户类型选择
  const handleUserTypeSelect = (typeId: UserType) => {
    setSelectedUserType(typeId)
    const config = getUserTypeConfig(typeId)
    setUserPersona(config!)
    setCurrentStep(OnboardingStep.WHO_AM_I)
  }

  // 下一步
  const handleNext = () => {
    const stepOrder: OnboardingStep[] = [
      OnboardingStep.WELCOME,
      OnboardingStep.USER_TYPE,
      OnboardingStep.WHO_AM_I,
      OnboardingStep.WHAT_I_HAVE,
      OnboardingStep.WHAT_I_OFFER,
      OnboardingStep.GUIDANCE,
      OnboardingStep.COMPLETE
    ]
    
    const currentIndex = stepOrder.indexOf(currentStep)
    if (currentIndex < stepOrder.length - 1) {
      const nextStep = stepOrder[currentIndex + 1]
      setCurrentStep(nextStep)
    }
  }

  // 上一步
  const handlePrev = () => {
    const stepOrder: OnboardingStep[] = [
      OnboardingStep.WELCOME,
      OnboardingStep.USER_TYPE,
      OnboardingStep.WHO_AM_I,
      OnboardingStep.WHAT_I_HAVE,
      OnboardingStep.WHAT_I_OFFER,
      OnboardingStep.GUIDANCE,
      OnboardingStep.COMPLETE
    ]
    
    const currentIndex = stepOrder.indexOf(currentStep)
    if (currentIndex > 0) {
      const prevStep = stepOrder[currentIndex - 1]
      setCurrentStep(prevStep)
    }
  }

  // 完成引导
  const handleComplete = () => {
    if (selectedUserType) {
      // 保存用户类型到 localStorage
      localStorage.setItem('userPersona', selectedUserType)
      localStorage.setItem('onboardingCompleted', 'true')
      onComplete(selectedUserType)
    }
  }

  return (
    <div className="onboarding-container">
      {currentStep === OnboardingStep.WELCOME && <WelcomePage onNext={handleNext} onSkip={() => onComplete('visitor')} />}
      {currentStep === OnboardingStep.USER_TYPE && (
        <UserTypeSelectionPage onSelect={handleUserTypeSelect} selectedType={selectedUserType} />
      )}
      {currentStep === OnboardingStep.WHO_AM_I && (
        <WhoAmIPage onNext={handleNext} onPrev={handlePrev} userType={userPersona} />
      )}
      {currentStep === OnboardingStep.WHAT_I_HAVE && (
        <WhatIHavePage onNext={handleNext} onPrev={handlePrev} userType={userPersona} />
      )}
      {currentStep === OnboardingStep.WHAT_I_OFFER && (
        <WhatIOfferPage onNext={handleNext} onPrev={handlePrev} userType={userPersona} />
      )}
      {currentStep === OnboardingStep.GUIDANCE && (
        <GuidancePage onNext={handleNext} onPrev={handlePrev} userType={userPersona} />
      )}
      {currentStep === OnboardingStep.COMPLETE && (
        <CompletePage onComplete={handleComplete} userType={userPersona} />
      )}
    </div>
  )
}

// 欢迎页面
const WelcomePage = ({ onNext, onSkip }: { onNext: () => void; onSkip: () => void }) => {
  const [skipOnboarding, setSkipOnboarding] = useState(false)

  const handleStart = () => {
    if (skipOnboarding) {
      // 如果勾选了跳过，直接标记完成并进入主页
      onSkip()
    } else {
      onNext()
    }
  }

  return (
    <div className="onboarding-page welcome-page">
      <div className="onboarding-content">
        <div className="welcome-icon">
          <Sparkles size={80} className="animate-pulse" />
        </div>
        <h1 className="welcome-title">欢迎来到灵值生态园</h1>
        <p className="welcome-subtitle">
          探索数字世界，发现无限可能
        </p>
        <div className="welcome-features">
          <div className="feature-item">
            <CheckCircle className="feature-icon" />
            <span>丰富的文化知识库</span>
          </div>
          <div className="feature-item">
            <CheckCircle className="feature-icon" />
            <span>智能对话助手</span>
          </div>
          <div className="feature-item">
            <CheckCircle className="feature-icon" />
            <span>资源市场与创作平台</span>
          </div>
        </div>
        
        {/* 跳过选项 */}
        <div className="skip-option">
          <label className="skip-checkbox">
            <input
              type="checkbox"
              checked={skipOnboarding}
              onChange={(e) => setSkipOnboarding(e.target.checked)}
            />
            <span className="skip-label">不再显示引导，直接进入主页</span>
          </label>
        </div>
        
        <button className="primary-button" onClick={handleStart}>
          开始探索
          <ArrowRight className="button-icon" />
        </button>
      </div>
    </div>
  )
}

// 用户类型选择页面
const UserTypeSelectionPage = ({ 
  onSelect, 
  selectedType 
}: { 
  onSelect: (type: UserType) => void
  selectedType: UserType | null 
}) => (
  <div className="onboarding-page user-type-page">
    <div className="onboarding-content">
      <h2 className="page-title">选择您的身份类型</h2>
      <p className="page-subtitle">我们将为您推荐最合适的功能和内容</p>
      
      <div className="user-type-grid">
        {USER_TYPES.map(type => (
          <div
            key={type.id}
            className={`user-type-card ${selectedType === type.id ? 'selected' : ''}`}
            onClick={() => onSelect(type.id)}
            style={{
              background: selectedType === type.id 
                ? `linear-gradient(135deg, ${type.color})`
                : ''
            }}
          >
            <div className="type-icon">{type.icon}</div>
            <h3 className="type-name">{type.name}</h3>
            <p className="type-description">{type.description}</p>
            {selectedType === type.id && (
              <CheckCircle className="selected-icon" />
            )}
          </div>
        ))}
      </div>
      
      {selectedType && (
        <div className="selection-confirmed">
          <CheckCircle />
          <span>已选择：{USER_TYPES.find(t => t.id === selectedType)?.name}</span>
          <ArrowRight />
        </div>
      )}
    </div>
  </div>
)

// 我是谁页面
const WhoAmIPage = ({ 
  onNext, 
  onPrev,
  userType 
}: { 
  onNext: () => void
  onPrev: () => void
  userType: UserTypeConfig | null
}) => (
  <div className="onboarding-page who-am-i-page">
    <div className="onboarding-content">
      <div className="page-header">
        <button className="back-button" onClick={onPrev}>
          <ChevronRight className="rotate-180" />
        </button>
        <h2 className="page-title">我是谁？</h2>
      </div>
      
      <div className="intro-content">
        <div className="intro-icon">🌟</div>
        <h3 className="intro-heading">灵值生态园</h3>
        <p className="intro-text">
          灵值生态园是一个融合传统文化与现代科技的数字元宇宙平台。
          我们致力于将深厚的文化底蕴与前沿的AI技术相结合，
          为用户提供一个探索、学习、创作和交易的全新空间。
        </p>
        
        <div className="intro-highlights">
          <div className="highlight-item">
            <div className="highlight-number">1000+</div>
            <div className="highlight-label">文化知识</div>
          </div>
          <div className="highlight-item">
            <div className="highlight-number">50+</div>
            <div className="highlight-label">AI智能体</div>
          </div>
          <div className="highlight-item">
            <div className="highlight-number">∞</div>
            <div className="highlight-label">创作可能</div>
          </div>
        </div>
      </div>
      
      <div className="page-navigation">
        <button className="primary-button" onClick={onNext}>
          继续探索
          <ArrowRight />
        </button>
      </div>
    </div>
  </div>
)

// 我有什么页面
const WhatIHavePage = ({ 
  onNext, 
  onPrev,
  userType 
}: { 
  onNext: () => void
  onPrev: () => void
  userType: UserTypeConfig | null
}) => {
  const features = [
    {
      icon: '📚',
      title: '知识库',
      description: '海量文化知识，AI智能检索'
    },
    {
      icon: '🤖',
      title: '智能对话',
      description: '专业AI助手，24/7在线服务'
    },
    {
      icon: '🎨',
      title: '创作工具',
      description: 'AI辅助创作，激发无限灵感'
    },
    {
      icon: '🏪',
      title: '资源市场',
      description: '数字资产交易，创作者经济'
    },
    {
      icon: '📊',
      title: '数据分析',
      description: '用户行为分析，精准洞察'
    },
    {
      icon: '🤝',
      title: '社区协作',
      description: '用户互动，合作共赢'
    }
  ]
  
  return (
    <div className="onboarding-page what-i-have-page">
      <div className="onboarding-content">
        <div className="page-header">
          <button className="back-button" onClick={onPrev}>
            <ChevronRight className="rotate-180" />
          </button>
          <h2 className="page-title">我有什么？</h2>
        </div>
        
        <p className="page-subtitle">
          灵值生态园为您提供全方位的数字化服务
        </p>
        
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h4 className="feature-title">{feature.title}</h4>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
        
        <div className="page-navigation">
          <button className="primary-button" onClick={onNext}>
            继续探索
            <ArrowRight />
          </button>
        </div>
      </div>
    </div>
  )
}

// 我能带来什么页面
const WhatIOfferPage = ({ 
  onNext, 
  onPrev,
  userType 
}: { 
  onNext: () => void
  onPrev: () => void
  userType: UserTypeConfig | null
}) => (
  <div className="onboarding-page what-i-offer-page">
    <div className="onboarding-content">
      <div className="page-header">
        <button className="back-button" onClick={onPrev}>
          <ChevronRight className="rotate-180" />
        </button>
        <h2 className="page-title">我能为您带来什么？</h2>
      </div>
      
      <div className="value-content">
        <div className="value-item">
          <div className="value-icon">🎯</div>
          <h4 className="value-title">精准定位</h4>
          <p className="value-description">
            根据您的身份类型，为您推荐最合适的功能和内容
          </p>
        </div>
        
        <div className="value-item">
          <div className="value-icon">💡</div>
          <h4 className="value-title">智能推荐</h4>
          <p className="value-description">
            AI智能分析您的兴趣和行为，提供个性化建议
          </p>
        </div>
        
        <div className="value-item">
          <div className="value-icon">⚡</div>
          <h4 className="value-title">高效赋能</h4>
          <p className="value-description">
            工具和资源，让您的创作和学习事半功倍
          </p>
        </div>
        
        <div className="value-item">
          <div className="value-icon">🌍</div>
          <h4 className="value-title">无限可能</h4>
          <p className="value-description">
            连接全球创作者和爱好者，发现更多机会
          </p>
        </div>
      </div>
      
      {userType && (
        <div className="personalized-benefits">
          <h4 className="benefits-title">专为您定制的权益</h4>
          <div className="benefits-list">
            {userType.benefits.map((benefit, index) => (
              <div key={index} className="benefit-item">
                <CheckCircle className="benefit-icon" />
                <span>{benefit}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="page-navigation">
        <button className="primary-button" onClick={onNext}>
          开始使用
          <ArrowRight />
        </button>
      </div>
    </div>
  </div>
)

// 引导页面
const GuidancePage = ({ 
  onNext, 
  onPrev,
  userType 
}: { 
  onNext: () => void
  onPrev: () => void
  userType: UserTypeConfig | null
}) => (
  <div className="onboarding-page guidance-page">
    <div className="onboarding-content">
      <div className="page-header">
        <button className="back-button" onClick={onPrev}>
          <ChevronRight className="rotate-180" />
        </button>
        <h2 className="page-title">开始您的旅程</h2>
      </div>
      
      <p className="page-subtitle">
        {userType ? `作为${userType.name}，我们为您推荐以下功能：` : '探索以下核心功能：'}
      </p>
      
      <div className="guidance-list">
        {userType ? userType.recommendedPages.map((page, index) => (
          <div key={index} className="guidance-item">
            <div className="guidance-number">{index + 1}</div>
            <div className="guidance-info">
              <h4 className="guidance-title">{page}</h4>
              <p className="guidance-description">深入了解{page}功能</p>
            </div>
            <ChevronRight />
          </div>
        )) : (
          <>
            <div className="guidance-item">
              <div className="guidance-number">1</div>
              <div className="guidance-info">
                <h4 className="guidance-title">知识库</h4>
                <p className="guidance-description">探索丰富的文化知识</p>
              </div>
              <ChevronRight />
            </div>
            <div className="guidance-item">
              <div className="guidance-number">2</div>
              <div className="guidance-info">
                <h4 className="guidance-title">智能对话</h4>
                <p className="guidance-description">与AI助手互动交流</p>
              </div>
              <ChevronRight />
            </div>
            <div className="guidance-item">
              <div className="guidance-number">3</div>
              <div className="guidance-info">
                <h4 className="guidance-title">资源市场</h4>
                <p className="guidance-description">发现和交易数字资产</p>
              </div>
              <ChevronRight />
            </div>
          </>
        )}
      </div>
      
      <div className="page-navigation">
        <button className="primary-button" onClick={onNext}>
          进入主页面
          <ArrowRight />
        </button>
      </div>
    </div>
  </div>
)

// 完成页面
const CompletePage = ({ 
  onComplete,
  userType 
}: { 
  onComplete: () => void
  userType: UserTypeConfig | null
}) => (
  <div className="onboarding-page complete-page">
    <div className="onboarding-content">
      <div className="complete-icon">
        <CheckCircle size={80} />
      </div>
      <h2 className="complete-title">准备就绪！</h2>
      <p className="complete-subtitle">
        {userType ? `欢迎您，${userType.name}` : '欢迎来到灵值生态园'}
      </p>
      
      <div className="complete-message">
        <p>您已经完成了引导设置，现在可以开始探索灵值生态园了。</p>
        <p>祝您在这个充满创造力和可能性的数字世界中找到属于自己的精彩！</p>
      </div>
      
      <button className="primary-button complete-button" onClick={onComplete}>
        开始体验
        <ArrowRight />
      </button>
    </div>
  </div>
)

export default OnboardingFlow
